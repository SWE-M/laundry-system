from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Order(models.Model):
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, verbose_name=_("Branch"))
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Customer"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Amount"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=_("Discount Percentage"))
    remarks = models.TextField(blank=True, null=True, verbose_name=_("Order Remarks"))
    reference = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Reference Number"))
    delivery_date = models.DateField(null=True, blank=True, verbose_name=_("Delivery Date"))
    is_void = models.BooleanField(default=False, verbose_name=_("Void Order"))
    
    processing_type = models.CharField(max_length=10, choices=[('HANGER', 'Hanger'), ('FOLDED', 'Folded')], default='FOLDED')
    logistics_type = models.CharField(max_length=10, choices=[('DELIVERY', 'Delivery'), ('PICKUP', 'Pickup')], default='PICKUP')

    # 🌟 الحالات الشاملة 🌟
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),        
        ('PROCESSING', 'Processing'),  
        ('READY', 'Ready'),            
        ('COMPLETED', 'Completed'),    
        ('DELIVERED', 'Delivered'),
        ('VOID', 'Void / Cancelled')  # 👈 هذا هو السطر السحري اللي كان ناقص!
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    processing_start_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Washing/Ironing Start"))
    ready_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Ready at Time"))

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Order"))
    item = models.ForeignKey('services.LaundryItem', on_delete=models.RESTRICT, verbose_name=_("Laundry Item"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price per item")) 
    ITEM_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('READY', 'Ready'),
        ('DELIVERED', 'Delivered')
    ]
    status = models.CharField(max_length=20, choices=ITEM_STATUS_CHOICES, default='PENDING', verbose_name=_("Item Status"))
    is_express = models.BooleanField(default=False, verbose_name=_("Express Service"))
    
    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

class Payment(models.Model):
    METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('WALLET', 'Wallet'),
        ('GIFT_CARD', 'Gift Card'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name=_("Order"))
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name=_("Payment Method"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    created_at = models.DateTimeField(auto_now_add=True, null=True) 

class GiftCard(models.Model):
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Purchaser"))
    card_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name=_("Card Number"))
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Initial Amount"))
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Current Balance"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_("Expiry Date"))
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.balance = self.initial_amount
        super().save(*args, **kwargs)
        if not self.card_number:
            self.card_number = str(10000 + self.pk)
            self.save(update_fields=['card_number'])

    def __str__(self):
        return f"Card: {self.card_number} | Balance: {self.balance}"

class AuditLog(models.Model):
    ACTION_CHOICES = [('ORDER_VOID', 'Order Cancelled'), ('CUSTOMER_DELETE', 'Customer Deleted')]
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    related_id = models.IntegerField() 
    reason = models.TextField() 
    performed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")

    def __str__(self):
        return self.name

class Expense(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('FAWRAN', 'Fawran'),
        ('CHECK', 'Check'),
    ]
    date = models.DateField(verbose_name="تاريخ المصروف")
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, verbose_name="التصنيف")
    description = models.CharField(max_length=255, verbose_name="الوصف")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ الإجمالي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="طريقة الدفع")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.total_amount} QAR"

class ShiftReport(models.Model):
    session_id = models.CharField(max_length=50, unique=True, verbose_name="رقم الجلسة")
    cashier = models.ForeignKey('auth.User', on_delete=models.PROTECT, verbose_name="الكاشير")
    opened_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الفتح")
    closed_at = models.DateTimeField(default=timezone.now, verbose_name="وقت الإغلاق")
    
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    expenses_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deleted_orders_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    expected_cash = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكاش المتوقع")
    actual_cash = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكاش الفعلي")
    actual_card = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="شبكة الفعلي")
    difference = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="العجز/الزيادة")
    
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تقرير وردية"
        verbose_name_plural = "تقارير الورديات"
        ordering = ['-closed_at']

    def __str__(self):
        return f"{self.session_id} - {self.cashier.username}"

class InventoryProduct(models.Model):
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="Barcode/SKU")
    name_en = models.CharField(max_length=200, verbose_name="Product Name")
    name_ar = models.CharField(max_length=200, blank=True, null=True, verbose_name="Arabic Name")
    product_type = models.CharField(max_length=100, default="Consumable")
    quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=0)
    opening_stock = models.IntegerField(default=0)
    opening_date = models.DateField(blank=True, null=True)
    allow_zero_stock = models.BooleanField(default=False)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unit = models.CharField(max_length=50, blank=True, null=True) # kg, liter, piece
    category = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='inventory_images/', blank=True, null=True) # لاحظ التعديل هنا لـ upload_to
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_en   