import os
import django
import pandas as pd
import re

# 1. Initialize Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from services.models import Category, LaundryItem

def split_multilingual_name(full_text):
    if pd.isna(full_text) or not str(full_text).strip():
        return "", ""
    full_text = str(full_text)
    # Split by newline or transitions between English and Arabic
    parts = re.split(r'\n|(?<=[\u0000-\u007F])(?=[\u0600-\u06FF])|(?<=[\u0600-\u06FF])(?=[\u0000-\u007F])', full_text)
    english_name = parts[0].strip() if len(parts) > 0 else full_text
    arabic_name = parts[1].strip() if len(parts) > 1 else (parts[0].strip() if len(parts) > 0 else "")
    return english_name, arabic_name

def parse_price(value):
    try:
        if pd.isna(value): return None
        return float(value)
    except:
        return None

def start_import():
    excel_file = 'data.xlsx' # Make sure your original file is named data.xlsx
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found.")
        return

    print("🚀 Starting direct Excel import process...")
    try:
        # Load the excel file directly
        df = pd.read_excel(excel_file)
        
        # Clean column names (remove hidden spaces)
        df.columns = [str(c).strip() for c in df.columns]
        
        items_created = 0
        for index, row in df.iterrows():
            # Get values using the exact names from your file
            cat_name = str(row['Column1']).strip()
            prod_name_raw = row['Product']
            
            if pd.isna(prod_name_raw): continue

            # Create/Get Category
            category, _ = Category.objects.get_or_create(
                name_en=cat_name, 
                defaults={'name': cat_name}
            )

            # Process Names
            en_name, ar_name = split_multilingual_name(prod_name_raw)

            # Process Prices
            LaundryItem.objects.create(
                category=category,
                name_en=en_name,
                name=ar_name,
                dry_cleaning_price=parse_price(row['Dry Clean (Normal)']),
                washing_price=parse_price(row['Wash & Pressing (Normal)']),
                ironing_price=parse_price(row['Pressing (Normal)']),
                is_active=True
            )
            
            items_created += 1
            print(f"✅ Imported {items_created}: {en_name}")

        print(f"\n✨ MISSION ACCOMPLISHED: {items_created} items added to Almarona V2!")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == '__main__':
    start_import()