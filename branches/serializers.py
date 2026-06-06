from rest_framework import serializers
from .models import Branch

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__' # هذا سيجعل دجانغو يقبل (الاسم، الهاتف، الموقع)