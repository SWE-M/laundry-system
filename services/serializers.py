from rest_framework import serializers
from .models import Category, LaundryItem
from .models import ExpenseCategory

# هذا هو الكلاس الذي كان ناقصاً وتسبب في الخطأ
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class LaundryItemSerializer(serializers.ModelSerializer):
    # سحبنا اسم القسم باللغتين عشان نقدر نفلتر الملابس في الشاشة لاحقاً
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_name_en = serializers.CharField(source='category.name_en', read_only=True)
    
    class Meta:
        model = LaundryItem
        fields = [
            'id', 
            'name', 'name_en', 
            'category', 'category_name', 'category_name_en',
            'washing_price', 'ironing_price', 'dry_cleaning_price',
            'image', 'is_active','washing_express_price', 'ironing_express_price', 'dry_cleaning_express_price',
            'image', 'is_active'
        ]

        from .models import ExpenseCategory

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'