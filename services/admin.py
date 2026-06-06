from django.contrib import admin
from .models import Category, LaundryItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en') # عرض الاسمين للقسم

@admin.register(LaundryItem)
class LaundryItemAdmin(admin.ModelAdmin):
    # عرضنا الاسم، القسم، والأسعار الثلاثة الجديدة في الجدول
    list_display = ('name', 'name_en', 'category', 'washing_price', 'ironing_price', 'dry_cleaning_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'name_en')
    
    # 🌟 الجديد: تحديد الحقول وترتيبها صراحة داخل صفحة التعديل لضمان ظهور حقل الصورة
    fields = ('category', 'name', 'name_en', 'washing_price', 'ironing_price', 'dry_cleaning_price', 'image', 'is_active')