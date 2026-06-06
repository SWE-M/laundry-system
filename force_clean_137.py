import os
import django
import pandas as pd
import re
import sys

# 1. إعداد بيئة دجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append(os.getcwd())
django.setup()

from django.apps import apps

def split_multilingual_name(full_text):
    if pd.isna(full_text) or not str(full_text).strip():
        return "", ""
    text = str(full_text)
    parts = re.split(r'\n|(?<=[\u0000-\u007F])(?=[\u0600-\u06FF])|(?<=[\u0600-\u06FF])(?=[\u0000-\u007F])', text)
    en = parts[0].strip() if len(parts) > 0 else text
    ar = parts[1].strip() if len(parts) > 1 else (parts[0].strip() if len(parts) > 0 else "")
    return en, ar

def heavy_clean():
    print("🧨 Starting Nuclear Clean-up...")
    
    # قائمة الجداول التي سنفرغها تماماً لفك كل القيود
    models_to_delete = [
        ('laundry', 'OrderItem'), 
        ('laundry', 'Order'),
        ('services', 'LaundryItem'),
        ('services', 'Category')
    ]

    for app_label, model_name in models_to_delete:
        try:
            model = apps.get_model(app_label, model_name)
            deleted_count = model.objects.all().delete()[0]
            print(f"🗑️ Cleared {deleted_count} records from {model_name}")
        except Exception as e:
            print(f"⚠️ Could not clear {model_name}: {e}")

    print("\n🚀 Importing the clean 137 items from data.xlsx...")
    try:
        excel_file = 'data.xlsx'
        df = pd.read_excel(excel_file)
        df.columns = [str(c).strip() for c in df.columns]
        
        items_created = 0
        Category = apps.get_model('services', 'Category')
        LaundryItem = apps.get_model('services', 'LaundryItem')

        for _, row in df.iterrows():
            if pd.isna(row.get('Product')): continue

            # إنشاء القسم
            cat_name = str(row['Column1']).strip()
            category, _ = Category.objects.get_or_create(name_en=cat_name, defaults={'name': cat_name})

            # معالجة الأسماء
            en_name, ar_name = split_multilingual_name(row['Product'])
            
            # معالجة الأسعار
            def p(val):
                try: return float(val) if not pd.isna(val) else 0.0
                except: return 0.0

            LaundryItem.objects.create(
                category=category,
                name_en=en_name,
                name=ar_name if ar_name else en_name,
                dry_cleaning_price=p(row.get('Dry Clean (Normal)')),
                washing_price=p(row.get('Wash & Pressing (Normal)')),
                ironing_price=p(row.get('Pressing (Normal)')),
                is_active=True
            )
            items_created += 1
            print(f"✅ [{items_created}] {en_name}")

        print(f"\n✨ MISSION ACCOMPLISHED: Now you have exactly {items_created} items!")

    except Exception as e:
        print(f"❌ Error during import: {e}")

if __name__ == '__main__':
    heavy_clean()