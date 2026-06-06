from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    # إضافة file_number لكي يظهر كعمود في الجدول
    list_display = ('name', 'phone', 'file_number', 'wallet_balance') 
    
    # إضافة file_number لكي تستطيع البحث عنه في مربع البحث العلوي
    search_fields = ('name', 'phone', 'file_number')