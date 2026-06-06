from rest_framework import serializers
from .models import CustomerProfile, CustomerCategory
from django.contrib.auth.models import User
from .models import CustomerProfile, CustomerCategory, StaffPermission
from .models import FinancialAccount

# السيرياليزر الجديد الخاص بفئات العملاء
class CustomerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategory
        fields = '__all__'

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        # استخدمنا '__all__' لكي يقبل ويرسل كل الحقول (القديمة والجديدة) تلقائياً
        fields = '__all__'

# السيرياليزر الخاص بالموظفين (يستخدم جدول User الافتراضي في جانغو)
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_active', 'is_staff']
        # نخلي الباسوورد write_only عشان ما يرجع في الـ API كـ نص صريح للأمان
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def create(self, validated_data):
        # نجعل المستخدم موظف تلقائياً
        validated_data['is_staff'] = True
        # create_user تقوم بتشفير الباسوورد تلقائياً
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # إذا تم إرسال باسوورد جديد أثناء التعديل، نقوم بتشفيره
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)        

class StaffPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPermission
        fields = '__all__'
        read_only_fields = ['user']        

class FinancialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialAccount
        fields = ['id', 'name', 'account_type', 'group_name', 'balance', 'is_active', 'created_at']
