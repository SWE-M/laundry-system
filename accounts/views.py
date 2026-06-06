from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import CustomerProfile, CustomerCategory, StaffPermission
from .serializers import (
    CustomerProfileSerializer, 
    CustomerCategorySerializer, 
    StaffSerializer, 
    StaffPermissionSerializer
)

from .serializers import FinancialAccountSerializer
from django.http import JsonResponse
from django.db.models import Sum
from .models import FinancialAccount, JournalItem
from .models import FinancialAccount, JournalItem
from datetime import datetime
import csv
from django.http import HttpResponse
from .models import FinancialAccount
import json
from .models import FinancialAccount, JournalItem, PaymentVoucher
from .models import FinancialAccount, JournalItem, PaymentVoucher, ReceiptVoucher, ReceiptItem
from .models import FinancialAccount, JournalItem, PaymentVoucher, ReceiptVoucher, ReceiptItem, Vendor
from .models import Vendor, PurchaseReturn



# === الـ ViewSet الخاص بفئات العملاء ===
class CustomerCategoryViewSet(viewsets.ModelViewSet):
    queryset = CustomerCategory.objects.all().order_by('-created_at')
    serializer_class = CustomerCategorySerializer

# === الـ ViewSet الخاص بالعملاء ===
class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    
    def get_queryset(self):
        queryset = CustomerProfile.objects.all()
        phone = self.request.query_params.get('phone')
        if phone:
            queryset = queryset.filter(phone=phone)
        return queryset

# === الـ ViewSet الخاص بالموظفين والصلاحيات ===
class StaffViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = StaffSerializer

    @action(detail=True, methods=['get', 'patch'])
    def permissions(self, request, pk=None):
        user = self.get_object()
        perms, created = StaffPermission.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = StaffPermissionSerializer(perms)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = StaffPermissionSerializer(perms, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

# 🛡️ دالة جلب صلاحيات الموظف المسجل دخوله حالياً
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_permissions(request):
    # 1. إذا كان المستخدم مديراً (Superuser)، نعطيه الصلاحية المطلقة في كل شيء
    if request.user.is_superuser:
        return Response({
            'is_superuser': True,
            'can_access_pos': True,
            'can_access_customers': True,
            'can_access_orders': True,
            'can_sell_gift_cards': True,
            'can_recharge_wallet': True,
            'can_add_expenses': True,
            'can_add_new_customer': True,
            'can_apply_discount': True,
            'can_pay_with_wallet_gc': True,
            'can_edit_customer': True,
            'can_delete_customer': True,
            'can_pay_debt': True,
            'can_view_history': True,
            'can_add_category': True,
            'can_void_order': True,
            'can_change_order_status': True,
            'can_add_items_to_order': True,
            'can_access_finance_center': True,
        })
    
    # 2. إذا كان موظفاً عادياً، نجلب صلاحياته من الداتابيز
    try:
        perms = request.user.permissions # تأكد أن الـ related_name في الـ model هو permissions
        serializer = StaffPermissionSerializer(perms)
        data = serializer.data
        data['is_superuser'] = False  # 🌟 تأكيد صريح للواجهة أنه ليس مديراً 🌟
        return Response(data)
    except:
        return Response({'error': 'No permissions found', 'is_superuser': False}, status=403)

# 🚪 دالة تسجيل الدخول الذكية
def custom_login_view(request):
    # 1. إذا كان المستخدم مسجل دخول بالفعل، وجهه حسب صلاحياته
    if request.user.is_authenticated:
        return smart_redirect(request.user)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                # 🚦 استخدام التوجيه الذكي بعد نجاح الدخول
                return smart_redirect(user)
            else:
                messages.error(request, "❌ حسابك موقوف، راجع الإدارة.")
        else:
            messages.error(request, "❌ اسم المستخدم أو الرقم السري غير صحيح.")
            
    return render(request, 'login.html')

# 🛡️ دالة التوجيه الذكي بناءً على الصلاحيات
def smart_redirect(user):
    # أولاً: إذا كان مدير عام (Superuser)، يذهب للداشبورد مباشرة
    if user.is_superuser:
        return redirect('/admin-dashboard/')
    
    # ثانياً: فحص صلاحيات الموظف العادي
    try:
        perms = user.permissions
        
        # 🚦 الترتيب المنطقي لتوجيه الموظف في شاشات النظام (POS)
        if perms.can_access_pos:
            return redirect('/cashier/')
            
        elif perms.can_access_customers:
            return redirect('/customers/')  # 🌟 التعديل هنا: تم تغييرها إلى شاشة النظام بدلاً من الداشبورد
            
        elif perms.can_access_orders:
            # تأكد أن هذا الرابط هو الخاص بشاشة الطلبات في النظام وليس الإدارة
            return redirect('/orders/management/') 
            
        else:
            # إذا لم تكن لديه أي صلاحية، يتم إخراجه
            return redirect('/logout/')
    except:
        # التوجيه الافتراضي إذا لم يكن لديه سجل صلاحيات بعد
        return redirect('/cashier/')
# 🚪 دالة تسجيل الخروج
def custom_logout_view(request):
    logout(request)
    return redirect('/login/')

class FinancialAccountViewSet(viewsets.ModelViewSet):
    queryset = FinancialAccount.objects.all().order_by('-created_at')
    serializer_class = FinancialAccountSerializer

def chart_of_accounts_view(request):
    return render(request, 'chart_of_accounts.html')    

def ledger_report_view(request):
    """
    دالة لفتح صفحة تقرير دفتر الأستاذ
    """
    return render(request, 'ledger_report.html')

def trial_balance_view(request):
    return render(request, 'trial_balance.html')    

def api_trial_balance_data(request):
    """ API لحساب ميزان المراجعة بناءً على قيود اليومية والتاريخ """
    start_date = request.GET.get('start', '2000-01-01')
    end_date = request.GET.get('end', '2100-01-01')

    accounts = FinancialAccount.objects.filter(is_active=True)
    results = []

    for acc in accounts:
        # تجميع المدين والدائن لهذا الحساب في الفترة المحددة
        totals = JournalItem.objects.filter(
            account=acc,
            entry__date__gte=start_date,
            entry__date__lte=end_date
        ).aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )

        debit_sum = totals['total_debit'] or 0
        credit_sum = totals['total_credit'] or 0

        # الرصيد الافتتاحي الثابت (المسجل في شجرة الحسابات)
        base_balance = float(acc.balance or 0)

        # إضافة الرصيد الافتتاحي للمجاميع بناءً على طبيعة الحساب
        if acc.account_type in ['ASSET', 'EXPENSE']:
            debit_sum = float(debit_sum) + base_balance
        else:
            credit_sum = float(credit_sum) + base_balance

        # إرسال البيانات للواجهة
        results.append({
            'id': acc.id,
            'name': acc.name,
            'account_type': acc.account_type,
            'balance': abs(float(debit_sum) - float(credit_sum)), # الرصيد الصافي كقيمة مطلقة للواجهة
        })

    return JsonResponse(results, safe=False)    

def profit_loss_report(request):
    # لاحظ هنا عدلناها إلى FinancialAccount
    sales_accounts = FinancialAccount.objects.filter(account_type='REVENUE')
    total_sales = 0
    for acc in sales_accounts:
        credit_sum = acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0
        debit_sum = acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0
        total_sales += (credit_sum - debit_sum)

    expense_accounts = FinancialAccount.objects.filter(account_type='EXPENSE')
    total_expenses = 0
    for acc in expense_accounts:
        debit_sum = acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0
        credit_sum = acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0
        total_expenses += (debit_sum - credit_sum)

    net_profit = total_sales - total_expenses
    
    context = {
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'generated_at': datetime.now().strftime("%d %b %Y, %H:%M:%S"),
    }
    return render(request, 'profit_loss.html', context)

def export_profit_loss_csv(request):
    # إنشاء استجابة بملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig') # utf-8-sig يدعم العربي بالإكسل
    response['Content-Disposition'] = 'attachment; filename="Profit_Loss_Report.csv"'
    
    writer = csv.writer(response)
    
    # 1. ترويسة الملف (Header)
    writer.writerow(['ALMARONA LAUNDRY - PROFIT & LOSS STATEMENT'])
    writer.writerow([]) # سطر فارغ
    
    # 2. الحسابات (بنفس المنطق اللي استخدمناه بالشاشة)
    sales_accounts = FinancialAccount.objects.filter(account_type='REVENUE')
    total_sales = 0
    for acc in sales_accounts:
        credit = acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0
        debit = acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0
        total_sales += (credit - debit)

    expense_accounts = FinancialAccount.objects.filter(account_type='EXPENSE')
    total_expenses = 0
    for acc in expense_accounts:
        debit = acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0
        credit = acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0
        total_expenses += (debit - credit)

    net_profit = total_sales - total_expenses

    # 3. كتابة البيانات على شكل جدول (يمين ويسار)
    writer.writerow(['Particulars (Expenses)', 'Amount', '', 'Particulars (Income)', 'Amount'])
    writer.writerow(['Purchase Account / Expenses', str(total_expenses), '', 'Sales Account', str(total_sales)])
    writer.writerow(['-------------------', '-------', '', '-------------------', '-------'])
    writer.writerow(['Net Profit', str(net_profit), '', '-', '-'])
    writer.writerow(['Grand Total', str(total_sales), '', 'Grand Total', str(total_sales)])

    return response    


def balance_sheet_report(request):
    # 1. سحب الأصول (Assets) مع تفاصيلها
    assets_list = []
    total_assets = 0
    for acc in FinancialAccount.objects.filter(account_type='ASSET'):
        bal = (acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0) - \
              (acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0)
        assets_list.append({'code': f"ASS-{acc.id:04d}", 'name': acc.name, 'balance': bal})
        total_assets += bal

    # 2. سحب الخصوم (Liabilities)
    liabilities_list = []
    total_liabilities = 0
    for acc in FinancialAccount.objects.filter(account_type='LIABILITY'):
        bal = (acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0) - \
              (acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0)
        liabilities_list.append({'code': f"LIA-{acc.id:04d}", 'name': acc.name, 'balance': bal})
        total_liabilities += bal

    # 3. حساب الأرباح المبقاة (Retained Earnings) من الإيرادات والمصاريف
    total_sales = sum(((a.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0) - (a.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0)) for a in FinancialAccount.objects.filter(account_type='REVENUE'))
    total_expenses = sum(((a.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0) - (a.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0)) for a in FinancialAccount.objects.filter(account_type='EXPENSE'))
    retained_earnings = total_sales - total_expenses

    context = {
        'assets': assets_list,
        'total_assets': total_assets,
        'liabilities': liabilities_list,
        'total_liabilities': total_liabilities,
        'retained_earnings': retained_earnings,
        'total_equity': retained_earnings, # يمكن إضافة رأس المال هنا مستقبلاً
        'generated_at': datetime.now().strftime("%b %d, %Y, %I:%M:%S %p"),
        'as_of_date': datetime.now().strftime("%B %d, %Y"),
    }
    return render(request, 'balance_sheet.html', context)


def export_balance_sheet_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Balance_Sheet.csv"'
    writer = csv.writer(response)
    
    writer.writerow(['ALMARONA LAUNDRY - BALANCE SHEET'])
    writer.writerow([f'As of: {datetime.now().strftime("%B %d, %Y")}'])
    writer.writerow([])
    
    # ترويسة الجدول للإكسل
    writer.writerow(['ASSETS', 'AMOUNT', '', 'LIABILITIES & EQUITY', 'AMOUNT'])
    
    # (هنا بنجيب القيم بسرعة للطباعة)
    assets_total = sum(((a.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0) - (a.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0)) for a in FinancialAccount.objects.filter(account_type='ASSET'))
    liab_total = sum(((a.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0) - (a.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0)) for a in FinancialAccount.objects.filter(account_type='LIABILITY'))
    sales = sum(((a.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0) - (a.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0)) for a in FinancialAccount.objects.filter(account_type='REVENUE'))
    exp = sum(((a.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0) - (a.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0)) for a in FinancialAccount.objects.filter(account_type='EXPENSE'))
    retained = sales - exp

    writer.writerow(['Current Assets', str(assets_total), '', 'Total Liabilities', str(liab_total)])
    writer.writerow(['', '', '', 'Retained Earnings', str(retained)])
    writer.writerow(['-------------------', '-------', '', '-------------------', '-------'])
    writer.writerow(['TOTAL ASSETS', str(assets_total), '', 'TOTAL LIAB & EQUITY', str(liab_total + retained)])
    
    return response


from django.http import JsonResponse
import json

def payments_list(request):
    # جلب جميع السندات غير المحذوفة
    vouchers = PaymentVoucher.objects.filter(is_deleted=False).order_by('-date', '-id')
    
    total_payments = sum(v.amount for v in vouchers)
    cash_payments = sum(v.amount for v in vouchers if v.payment_method == 'Cash')
    bank_payments = sum(v.amount for v in vouchers if v.payment_method == 'Bank')
    pdc_payments = sum(v.amount for v in vouchers if v.payment_method == 'PDC')

    # جلب الموردين مع حساب رصيد كل واحد فيهم
    suppliers_data = []
    for sup in FinancialAccount.objects.filter(account_type='LIABILITY'):
        bal = (sup.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0) - \
              (sup.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0)
        suppliers_data.append({'id': sup.id, 'name': sup.name, 'balance': bal})

    context = {
        'vouchers': vouchers,
        'total_payments': total_payments,
        'cash_payments': cash_payments,
        'bank_payments': bank_payments,
        'pdc_payments': pdc_payments,
        'total_count': vouchers.count(),
        'cash_count': vouchers.filter(payment_method='Cash').count(),
        'bank_count': vouchers.filter(payment_method='Bank').count(),
        'pdc_count': vouchers.filter(payment_method='PDC').count(),
        'suppliers': suppliers_data, 
    }
    return render(request, 'payments.html', context)


def save_payment_api(request):
    """ دالة حفظ السند الأساسي """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier = FinancialAccount.objects.get(id=data['supplier_id'])
            
            PaymentVoucher.objects.create(
                supplier=supplier,
                date=data['date'],
                amount=data['amount'],
                payment_method=data['payment_method'],
                reference=data.get('reference', ''),
                notes=data.get('notes', ''),
                is_direct_payment=data.get('is_direct_payment', True),
                status='Posted'
            )
            return JsonResponse({'status': 'success', 'message': 'Payment saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)


def quick_add_account_api(request):
    """ دالة إضافة حساب مورد جديد من زر (+) """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_acc = FinancialAccount.objects.create(
                name=data['name'],
                group_name=data['group'],
                account_type='LIABILITY', 
                is_active=(data['status'] == 'Active')
            )
            return JsonResponse({
                'status': 'success', 
                'account': {'id': new_acc.id, 'name': new_acc.name, 'balance': 0}
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# ==========================================
# 🌟 قسم المقبوضات (Receipt Vouchers) 🌟
# ==========================================

def receipts_list(request):
    vouchers = ReceiptVoucher.objects.filter(is_deleted=False).order_by('-date', '-id')
    
    total_receipts = sum(v.total_amount for v in vouchers)
    cash_receipts = sum(v.total_amount for v in vouchers if v.payment_method == 'Cash')
    bank_receipts = sum(v.total_amount for v in vouchers if v.payment_method == 'Bank')
    pdc_receipts = sum(v.total_amount for v in vouchers if v.payment_method == 'PDC')

    # جلب الحسابات للقائمة المنسدلة الأساسية (Receipt From)
    accounts_data = []
    for acc in FinancialAccount.objects.all():
        bal = (acc.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0) - \
              (acc.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0)
        accounts_data.append({'id': acc.id, 'name': acc.name, 'balance': abs(bal)})

    # جلب حسابات الإيرادات (Sales) لجدول الأصناف
    sale_accounts = FinancialAccount.objects.filter(account_type='REVENUE')

    context = {
        'vouchers': vouchers,
        'total_receipts': total_receipts,
        'cash_receipts': cash_receipts,
        'bank_receipts': bank_receipts,
        'pdc_receipts': pdc_receipts,
        'total_count': vouchers.count(),
        'cash_count': vouchers.filter(payment_method='Cash').count(),
        'bank_count': vouchers.filter(payment_method='Bank').count(),
        'pdc_count': vouchers.filter(payment_method='PDC').count(),
        'accounts': accounts_data,
        'sale_accounts': sale_accounts,
    }
    return render(request, 'receipts.html', context)

def save_receipt_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            main_account = FinancialAccount.objects.get(id=data['account_id'])
            
            # إنشاء السند الأساسي
            voucher = ReceiptVoucher.objects.create(
                account=main_account,
                date=data['date'],
                total_amount=data['total_amount'],
                payment_method=data['payment_method'],
                reference=data.get('reference', ''),
                notes=data.get('notes', ''),
                is_direct_payment=data.get('is_direct_payment', True)
            )

            # إضافة الأصناف (Items) المرتبطة بالسند
            for item in data.get('items', []):
                sale_acc = FinancialAccount.objects.get(id=item['sale_account_id'])
                ReceiptItem.objects.create(
                    voucher=voucher,
                    sale_account=sale_acc,
                    description=item.get('description', ''),
                    amount=item['amount']
                )

            return JsonResponse({'status': 'success', 'message': 'Receipt saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)    

# ==========================================
# 🌟 قسم المشتريات والموردين (Vendors) 🌟
# ==========================================

def vendors_list(request):
    vendors = Vendor.objects.all().order_by('-created_at')
    context = {
        'vendors': vendors,
        'vendors_count': vendors.count()
    }
    return render(request, 'vendors.html', context)

def add_vendor_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Vendor.objects.create(
                company_name=data['company_name'],
                email=data.get('email', ''),
                phone_number=data['phone_number'],
                contact_person=data.get('contact_person', ''),
                address=data.get('address', ''),
                opening_balance=data.get('opening_balance', 0) or 0,
                opening_balance_date=data.get('opening_balance_date') or None,
                remarks=data.get('remarks', '')
            )
            return JsonResponse({'status': 'success', 'message': 'Supplier added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)    

def active_vendors_api(request):
    # جلب أسماء الموردين فقط لإرسالها للكاشير
    vendors = list(Vendor.objects.values('id', 'company_name'))
    return JsonResponse(vendors, safe=False)


def purchase_returns_page(request):
    return render(request, 'purchase_returns.html')

def api_purchase_returns(request):
    if request.method == 'GET':
        returns = PurchaseReturn.objects.all().order_by('-created_at')
        data = [{
            'id': r.id,
            'return_number': f"RET-{r.id:05d}",
            'purchase_reference': r.purchase_reference,
            # 🌟 التعديل 1: حماية التاريخ عشان ما يسوي كراش 🌟
            'date': str(r.date) if r.date else '---',
            # 🌟 التعديل 2: تحويل مبلغ الديسيمال إلى رقم عشري عشان يقبله الـ JSON 🌟
            'total_amount': float(r.total_amount) if r.total_amount else 0.0,
            'payment_method': r.payment_method,
            'status': r.status,
            'items_data': r.items_data,
            'reason': r.reason
        } for r in returns]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        # ... (باقي كود الـ POST خله زي ما هو عندك لا تغيره) ...
        try:
            data = json.loads(request.body)
            new_return = PurchaseReturn.objects.create(
                purchase_reference=data.get('purchase_reference', ''),
                date=data.get('date'),
                supplier_invoice_number=data.get('supplier_invoice_number', ''),
                status=data.get('status', 'Pending'),
                payment_method=data.get('payment_method', 'Cash'),
                reason=data.get('reason', ''),
                total_amount=data.get('total_amount', 0),
                items_data=data.get('items', [])
            )
            return JsonResponse({'status': 'success', 'message': 'Return created successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def api_purchase_returns_detail(request, pk):
    if request.method == 'DELETE':
        try:
            return_record = PurchaseReturn.objects.get(id=pk)
            return_record.delete()
            return JsonResponse({'status': 'success', 'message': 'تم الحذف بنجاح!'})
        except PurchaseReturn.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'المرتجع غير موجود!'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def payment_vouchers_view(request):
    # جلب السندات
    vouchers = PaymentVoucher.objects.filter(is_deleted=False).order_by('-date', '-id')
    
    total_payments = sum(v.amount for v in vouchers)
    cash_payments = sum(v.amount for v in vouchers if v.payment_method == 'Cash')
    bank_payments = sum(v.amount for v in vouchers if v.payment_method == 'Bank')
    pdc_payments = sum(v.amount for v in vouchers if v.payment_method == 'PDC')

    # جلب الموردين
    suppliers_data = []
    for sup in FinancialAccount.objects.filter(account_type='LIABILITY'):
        bal = (sup.journalitem_set.aggregate(Sum('credit'))['credit__sum'] or 0) - \
              (sup.journalitem_set.aggregate(Sum('debit'))['debit__sum'] or 0)
        suppliers_data.append({'id': sup.id, 'name': sup.name, 'balance': bal})

    context = {
        'vouchers': vouchers,
        'total_payments': total_payments,
        'cash_payments': cash_payments,
        'bank_payments': bank_payments,
        'pdc_payments': pdc_payments,
        'total_count': vouchers.count(),
        'cash_count': vouchers.filter(payment_method='Cash').count(),
        'bank_count': vouchers.filter(payment_method='Bank').count(),
        'pdc_count': vouchers.filter(payment_method='PDC').count(),
        'suppliers': suppliers_data, 
    }
    # 🌟 هنا نوجهها للملف الجديد 🌟
    return render(request, 'payment_vouchers.html', context)            

