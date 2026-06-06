from django.contrib import admin
from .models import Order, OrderItem, Payment, GiftCard

# هذي الأكواد بتخلي القطع والمدفوعات تظهر داخل صفحة الطلب نفسها!
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # لمنع ظهور أسطر فارغة مزعجة

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'customer', 'total_amount', 'is_void', 'created_at')
    list_filter = ('is_void', 'branch', 'created_at')
    inlines = [OrderItemInline, PaymentInline] # أضفنا السحر هنا

# ابحث عن هذا الجزء واستبدله بالكامل
@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    # الحقول الجديدة التي ستظهر في جدول لوحة التحكم
    list_display = ('card_number', 'customer', 'initial_amount', 'balance', 'is_active', 'expiry_date')
    
    # الفلاتر الجانبية
    list_filter = ('is_active', 'created_at', 'expiry_date')
    
    # حقل البحث (للبحث برقم البطاقة)
    search_fields = ('card_number',)
    
    # جعل بعض الحقول للقراءة فقط (لأن النظام ينشئها تلقائياً)
    readonly_fields = ('card_number', 'created_at')