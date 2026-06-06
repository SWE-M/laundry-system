from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser 

# 🌟 استدعاء جميع الموديلات من نفس التطبيق 🌟
from .models import Category, LaundryItem, ExpenseCategory, Expense
# 🌟 استدعاء موديل الفروع 🌟
from branches.models import Branch  
from .serializers import CategorySerializer, LaundryItemSerializer, ExpenseCategorySerializer

# ==========================================
# روابط صفحات الـ HTML (الواجهة)
# ==========================================
def cashier_view(request):
    return render(request, 'cashier.html')

def customers_page(request):
    return render(request, 'customers.html')


# ==========================================
# روابط الـ API الخاصة بالخدمات والأقسام
# ==========================================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    # 🌟 النسخة المحسنة والمضمونة لحذف التصنيف 🌟
    def destroy(self, request, *args, **kwargs):
        try:
            category = self.get_object()
            
            # 1. البحث عن أو إنشاء تصنيف افتراضي (لأن قاعدة البيانات لا تقبل "فارغ")
            uncategorized_cat, created = Category.objects.get_or_create(name="Uncategorized")
            
            # منع حذف التصنيف الافتراضي نفسه لضمان استقرار النظام
            if category.id == uncategorized_cat.id:
                return Response({"error": "لا يمكن حذف التصنيف الافتراضي للنظام"}, status=status.HTTP_400_BAD_REQUEST)

            # 2. نقل كل الأصناف التابعة لهذا التصنيف إلى التصنيف الافتراضي
            LaundryItem.objects.filter(category=category).update(category=uncategorized_cat)
            
            # 3. الآن نحذف التصنيف بأمان
            category.delete()
            return Response({"message": "تم حذف التصنيف بنجاح ونقل الأصناف لـ Uncategorized"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LaundryItemViewSet(viewsets.ModelViewSet):
    queryset = LaundryItem.objects.filter(is_active=True)
    serializer_class = LaundryItemSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer 


# ==========================================
# 🌟 الدوال الحقيقية للمصروفات (بديلة الوهمية) 🌟
# ==========================================
@api_view(['POST'])
def save_expense_api(request):
    try:
        data = request.data
        cat_id = data.get('category')
        loc_id = data.get('location')

        # جلب الكائنات (Category و Location) من قاعدة البيانات إذا تم إرسالها
        category_obj = ExpenseCategory.objects.filter(id=cat_id).first() if cat_id else None
        location_obj = Branch.objects.filter(id=loc_id).first() if loc_id else None

        # إنشاء وحفظ الفاتورة فعلياً في قاعدة البيانات
        expense = Expense.objects.create(
            date=data.get('date'),
            description=data.get('description'),
            category=category_obj,
            location=location_obj,
            total_amount=data.get('total_amount', 0),
            paid_amount=data.get('paid_amount', 0),
            payment_method=data.get('payment_method', 'CASH'),
            notes=data.get('notes', '')
        )
        
        # نرد بالـ ID الحقيقي الخاص بقاعدة البيانات
        return Response({"id": expense.id, "message": "تم الحفظ بنجاح"}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_expenses_api(request):
    try:
        # جلب أحدث المصروفات من قاعدة البيانات
        expenses = Expense.objects.all().order_by('-id')
        data = []
        for exp in expenses:
            data.append({
                "id": exp.id,
                "date": exp.date.strftime('%Y-%m-%d') if exp.date else '',
                "description": exp.description,
                "category_name": exp.category.name if exp.category else '---',
                "location_name": exp.location.name if exp.location else '---',
                "total_amount": float(exp.total_amount),
                "paid_amount": float(exp.paid_amount),
                "payment_method": exp.payment_method
            })
        return Response({"results": data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 🌟 دالة جديدة خاصة بالتعديل (PUT) والحذف (DELETE) 🌟
@api_view(['PUT', 'DELETE'])
def expense_detail_api(request, pk):
    try:
        expense = Expense.objects.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({"error": "الفاتورة غير موجودة"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        expense.delete()
        return Response({"message": "تم الحذف بنجاح"}, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data
        cat_id = data.get('category')
        loc_id = data.get('location')

        if cat_id: expense.category = ExpenseCategory.objects.filter(id=cat_id).first()
        if loc_id: expense.location = Branch.objects.filter(id=loc_id).first()

        expense.date = data.get('date', expense.date)
        expense.description = data.get('description', expense.description)
        expense.total_amount = data.get('total_amount', expense.total_amount)
        expense.paid_amount = data.get('paid_amount', expense.paid_amount)
        expense.payment_method = data.get('payment_method', expense.payment_method)
        expense.save()

        return Response({"message": "تم التعديل بنجاح"}, status=status.HTTP_200_OK)