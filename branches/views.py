from rest_framework import viewsets
from .models import Branch
from .serializers import BranchSerializer

# هذا هو الكلاس الذي كان يبحث عنه السيرفر
class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer