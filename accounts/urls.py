from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerCategoryViewSet, StaffViewSet, my_permissions
from . import views
from accounts.views import chart_of_accounts_view

router = DefaultRouter()

# تسجيل المسارات التلقائية للـ API
router.register(r'search', CustomerViewSet, basename='customer-profile')
router.register(r'categories', CustomerCategoryViewSet, basename='customer-category')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'financial-accounts', views.FinancialAccountViewSet, basename='financial-accounts')


urlpatterns = [
    # روابط الـ API (search, categories, staff)
    path('', include(router.urls)),
    
    # 🛡️ رابط جلب صلاحيات الموظف الحالي (مهم جداً للحماية)
    path('my-permissions/', my_permissions, name='my-permissions'),

    path('chart-of-accounts/', views.chart_of_accounts_view, name='chart-of-accounts'),

    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),

    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),

    path('profit-loss/export/', views.export_profit_loss_csv, name='export_profit_loss_csv'),

    path('balance-sheet/', views.balance_sheet_report, name='balance_sheet_report'),
    path('balance-sheet/export/', views.export_balance_sheet_csv, name='export_balance_sheet_csv'),

    path('payments/', views.payments_list, name='payments_list'),
    path('api/save-payment/', views.save_payment_api, name='save_payment_api'),


    path('api/quick-add-account/', views.quick_add_account_api, name='quick_add_account_api'),

    path('receipts/', views.receipts_list, name='receipts_list'),
path('api/save-receipt/', views.save_receipt_api, name='save_receipt_api'),

path('vendors/', views.vendors_list, name='vendors_list'),
path('api/add-vendor/', views.add_vendor_api, name='add_vendor_api'),
path('active-vendors/', views.active_vendors_api, name='active_vendors_api'),
path('purchase-returns/', views.purchase_returns_page, name='purchase_returns_page'),
path('api/purchase-returns/', views.api_purchase_returns, name='api_purchase_returns'),
path('api/purchase-returns/<int:pk>/', views.api_purchase_returns_detail, name='api_purchase_returns_detail'),
path('payment-vouchers/', views.payment_vouchers_view, name='payment_vouchers_view'),
    
]