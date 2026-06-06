from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.http import JsonResponse


# 1. الموديل الخاص بتصنيفات العملاء
class CustomerCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Category Name"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Customer Category")
        verbose_name_plural = _("Customer Categories")

    def __str__(self):
        return self.name


# 2. ملف بيانات العميل (النسخة المستقرة بحقل نصي)
class CustomerProfile(models.Model):
    FOLD_CHOICES = [
        ('Folded', 'Folded'),
        ('Hanged', 'Hanged'),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Customer Name"))
    phone = models.CharField(max_length=20, unique=True, verbose_name=_("Phone Number"))
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Wallet Balance"))
    file_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("File Number"))
    fold_type = models.CharField(max_length=20, choices=FOLD_CHOICES, default='Folded', verbose_name=_("Fold Type"))
    
    # 🌟 العودة للحقل النصي الأصلي لتجنب أخطاء قاعدة البيانات 🌟
    customer_category = models.CharField(max_length=50, default='Uncategorized', verbose_name=_("Customer Category"))
    
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))

    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profiles")

    def __str__(self):
        return f"{self.name} - {self.phone}"


# 3. جدول صلاحيات الموظفين
class StaffPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='permissions')
    
    can_access_pos = models.BooleanField(default=False)
    can_access_customers = models.BooleanField(default=False)
    can_access_orders = models.BooleanField(default=False)
    
    can_sell_gift_cards = models.BooleanField(default=False)
    can_recharge_wallet = models.BooleanField(default=False)
    can_add_expenses = models.BooleanField(default=False)
    can_apply_discount = models.BooleanField(default=False)
    can_delete_from_cart = models.BooleanField(default=False)
    can_add_new_customer = models.BooleanField(default=False)
    can_pay_with_wallet_gc = models.BooleanField(default=False)

    can_edit_customer = models.BooleanField(default=False)
    can_delete_customer = models.BooleanField(default=False)
    can_pay_debt = models.BooleanField(default=False)
    can_add_category = models.BooleanField(default=False)
    can_view_history = models.BooleanField(default=False)

    can_void_order = models.BooleanField(default=False)
    can_access_finance_center = models.BooleanField(default=False)
    can_change_order_status = models.BooleanField(default=False)
    can_add_items_to_order = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions for {self.user.username}"    


# 4. شجرة الحسابات المالية
class FinancialAccount(models.Model):
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset / أصول'),
        ('LIABILITY', 'Liability / خصوم'),
        ('REVENUE', 'Revenue / إيرادات'),
        ('EXPENSE', 'Expense / مصروفات'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم الحساب")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='ASSET')
    group_name = models.CharField(max_length=100, verbose_name="المجموعة")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.account_type})"

# أضف هذا الكود في أسفل ملف accounts/models.py

class JournalEntry(models.Model):
    """ جدول قيد اليومية الأساسي """
    date = models.DateField(verbose_name="تاريخ القيد")
    reference = models.CharField(max_length=100, null=True, blank=True, verbose_name="رقم المرجع (مثال: رقم الفاتورة)")
    description = models.TextField(null=True, blank=True, verbose_name="البيان / الوصف")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"قيد رقم #{self.id} - {self.date}"

class JournalItem(models.Model):
    """ جدول أطراف القيد (مدين / دائن) """
    entry = models.ForeignKey(JournalEntry, related_name='items', on_delete=models.CASCADE)
    account = models.ForeignKey('FinancialAccount', on_delete=models.CASCADE, verbose_name="الحساب")
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="مدين (Debit)")
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="دائن (Credit)")

    def __str__(self):
        return f"{self.account.name} | مدين: {self.debit} | دائن: {self.credit}"  
        
        return f"{self.voucher_number} - {self.supplier.name}"     

# أضف هذا الكلاس في آخر ملف models.py
class PaymentVoucher(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Bank', 'Bank Transfer'),
        ('PDC', 'Post Dated Check'),
    ]
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Posted', 'Posted'),
        ('Cancelled', 'Cancelled'),
    ]

    voucher_number = models.CharField(max_length=20, unique=True, blank=True)
    # نربط المورد بشجرة الحسابات (الخصوم)
    supplier = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name='payments_received', limit_choices_to={'account_type': 'LIABILITY'})
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    is_direct_payment = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.voucher_number:
            # توليد رقم السند تلقائياً مثل PV-0001
            last_voucher = PaymentVoucher.objects.all().order_by('id').last()
            if last_voucher:
                new_id = last_voucher.id + 1
                self.voucher_number = f"PV-{new_id:04d}"
            else:
                self.voucher_number = "PV-0001"
        super(PaymentVoucher, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.voucher_number} - {self.supplier.name}"      

class ReceiptVoucher(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Bank', 'Bank Transfer'),
        ('PDC', 'Post Dated Check'),
    ]

    voucher_number = models.CharField(max_length=20, unique=True, blank=True)
    # الحساب اللي اخذنا منه الفلوس (غالباً عميل أو أصول)
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name='receipts_given')
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_direct_payment = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.voucher_number:
            last_voucher = ReceiptVoucher.objects.all().order_by('id').last()
            if last_voucher:
                new_id = last_voucher.id + 1
                self.voucher_number = f"RV-{new_id:04d}"
            else:
                self.voucher_number = "RV-0001"
        super(ReceiptVoucher, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.voucher_number} - {self.account.name}"

class ReceiptItem(models.Model):
    voucher = models.ForeignKey(ReceiptVoucher, on_delete=models.CASCADE, related_name='items')
    sale_account = models.ForeignKey(FinancialAccount, on_delete=models.SET_NULL, null=True, related_name='receipt_sales')
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.voucher.voucher_number} - {self.amount}"       

class Vendor(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    opening_balance_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    # الربط الذكي مع الحسابات المالية (الاجتهاد اللي تكلمنا عنه)
    financial_account = models.OneToOneField(FinancialAccount, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Vendor, self).save(*args, **kwargs)
        
        # إذا المورد جديد، ننشئ له حساب مالي تلقائياً في الخصوم
        if is_new and not self.financial_account:
            acc = FinancialAccount.objects.create(
                name=f"مورد: {self.company_name}",
                group_name="Current Liabilities",
                account_type="LIABILITY"
            )
            self.financial_account = acc
            self.save(update_fields=['financial_account'])

            # إذا عنده رصيد افتتاحي، نسجل له قيد محاسبي (اختياري مستقبلاً)

    def __str__(self):
        return self.company_name      

# أضف هذا الكلاس في آخر ملف accounts/models.py
class PurchaseReturn(models.Model):
    # ربط المرتجع بالفاتورة الأصلية (المشتريات/المصروفات)
    # ملاحظة: استبدل 'Expense' باسم الموديل الفعلي للمشتريات عندك إذا كان مختلف
    purchase_reference = models.CharField(max_length=255, blank=True, null=True) 
    
    date = models.DateField()
    supplier_invoice_number = models.CharField(max_length=255, blank=True, null=True)
    
    # Dropdowns
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    
    PAYMENT_CHOICES = (
        ('Cash', 'Cash'),
        ('Bank', 'Bank'),
        ('Credit', 'Credit'),
    )
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Cash')
    
    reason = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # حفظ الأصناف المرتجعة كبيانات مرنة
    items_data = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RET-{self.id:05d}"
            