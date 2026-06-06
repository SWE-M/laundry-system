import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from services.models import Category, LaundryItem

class Command(BaseCommand):
    help = 'سحب بيانات الملابس والأسعار من ملف CSV إلى قاعدة البيانات'

    def handle(self, *args, **kwargs):
        # مسار ملف البيانات الذي وضعناه بجانب manage.py
        file_path = os.path.join(settings.BASE_DIR, 'data.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'الملف غير موجود في المسار: {file_path}'))
            return

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                count = 0
                
                for row in reader:
                    category_name = row.get('Category')
                    item_name = row.get('Item Name')
                    price = row.get('Price')

                    # التأكد من عدم وجود بيانات فارغة في الصف
                    if not category_name or not item_name or not price:
                        continue

                    # 1. جلب التصنيف أو إنشائه إذا لم يكن موجوداً
                    category, _ = Category.objects.get_or_create(name=category_name.strip())

                    # 2. إنشاء قطعة الغسيل وربطها بالتصنيف
                    item, created = LaundryItem.objects.get_or_create(
                        category=category,
                        name=item_name.strip(),
                        defaults={'price': price}
                    )
                    
                    if created:
                        count += 1

            self.stdout.write(self.style.SUCCESS(f'تم سحب {count} صنف بنجاح إلى النظام! 🎉'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'حدث خطأ أثناء السحب: {str(e)}'))