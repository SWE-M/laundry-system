import os
import django

# 1. إعداد بيئة دجانغو للوصول لقاعدة البيانات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# استيراد الموديل الخاص بالأصناف
from services.models import LaundryItem

def run_inventory():
    print("📋 جاري جرد الأصناف الموجودة في قاعدة البيانات...")
    
    # جلب كل الأصناف وترتيبها أبجدياً حسب الاسم الإنجليزي
    items = LaundryItem.objects.all().order_by('name_en')
    
    # إنشاء ملف نصي لكتابة النتائج فيه
    with open('database_inventory.txt', 'w', encoding='utf-8') as f:
        f.write(f"قائمة الأصناف المستوردة (الإجمالي: {items.count()})\n")
        f.write("="*50 + "\n")
        
        for i, item in enumerate(items, 1):
            line = f"{i}. {item.name_en} | {item.name}\n"
            f.write(line)
    
    print(f"✨ تم بنجاح! تم استخراج {items.count()} صنف.")
    print("📂 افتح ملف 'database_inventory.txt' في مجلد المشروع لرؤية القائمة.")

if __name__ == '__main__':
    run_inventory()