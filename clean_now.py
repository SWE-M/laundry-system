import os
import django
import sys

# 1. إعداد البيئة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append(os.getcwd())
django.setup()

from django.apps import apps

def force_delete_all():
    print("🧹 جاري تصفية قاعدة البيانات بالكامل...")
    
    # قائمة بأسماء الموديلات التي نريد حذفها
    target_models = ['OrderItem', 'Order', 'LaundryItem', 'Category']
    
    # الحصول على كل الموديلات المسجلة في النظام
    all_models = apps.get_models()
    
    for model in all_models:
        if model.__name__ in target_models:
            try:
                count = model.objects.all().count()
                # حذف السجلات (استخدمنا _raw_delete لتجاوز بعض قيود الحماية إذا لزم الأمر)
                model.objects.all().delete()
                print(f"✅ تم تصفير موديل {model.__name__} (حذف {count} سجل)")
            except Exception as e:
                print(f"❌ فشل حذف {model.__name__}: {e}")

    print("\n✨ قاعدة البيانات الآن نظيفة تماماً.")

if __name__ == '__main__':
    force_delete_all()