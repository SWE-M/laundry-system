from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import save_expense_api, get_expenses_api, ExpenseCategoryViewSet, expense_detail_api

router = DefaultRouter()
router.register(r'categories', ExpenseCategoryViewSet, basename='expense-categories')

urlpatterns = [
    path('save-expense/', save_expense_api, name='save_expense_api'),
    path('expenses/', get_expenses_api, name='get_expenses_api'),
    
    # 🌟 الرابط الجديد للتعديل والحذف 🌟
    path('expenses/<int:pk>/', expense_detail_api, name='expense_detail_api'), 
    
    path('', include(router.urls)), 
]