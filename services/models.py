from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image # ضروري لتصغير حجم الصور تلقائياً

# 1. جدول التصنيفات (مثل: ملابس رجالية، ملابس نسائية، سجاد)
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Category Name (AR)"))
    name_en = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Category Name (EN)"))
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

# 2. جدول قطع الغسيل (مثل: ثوب، شماغ، فستان)
class LaundryItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name=_("Category"))
    
    # الأسماء باللغتين لدعم الواجهة المزدوجة
    name = models.CharField(max_length=100, verbose_name=_("Item Name (AR)"))
    name_en = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Item Name (EN)"))
    
    # الأسعار العادية
    washing_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Washing Price"))
    ironing_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Ironing Price"))
    dry_cleaning_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Dry Cleaning Price"))
    
    # 🌟 إضافة حقول الأسعار المستعجلة لتعمل مع صفحة الإدارة الجديدة 🌟
    washing_express_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Washing Express Price"))
    ironing_express_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Ironing Express Price"))
    dry_cleaning_express_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Dry Cleaning Express Price"))

    # إضافة صورة للقطعة
    image = models.ImageField(upload_to='items/', null=True, blank=True, verbose_name=_("Item Image"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    def __str__(self):
        return f"{self.name} | {self.name_en or ''}"

    # 🌟 دالة سحرية لتصغير الصورة تلقائياً عند الحفظ لتبدو متناسقة 🌟
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            # إذا كانت الصورة أكبر من 600 بكسل، نقوم بتصغيرها فوراً
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        verbose_name = _("Laundry Item")
        verbose_name_plural = _("Laundry Items")

    # جدول خاص بفئات المصروفات (مفصول تماماً عن فئات الملابس)
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name  


# جدول فواتير المشتريات/المصروفات
class Expense(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=255)
    # ربط الفاتورة بجدول فئات المصروفات
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)
    # ربط الفاتورة بجدول الفروع (المواقع)
    location = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.total_amount}"