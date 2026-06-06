from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, GiftCardViewSet, OrderItemViewSet, 
    orders_management, print_order_receipt, admin_dashboard, 
    workshop_view, close_shift_api  # 👈 تمت إضافتها هنا
)
from django.urls import path
from . import views

router = DefaultRouter()
router.register(r'checkout', OrderViewSet, basename='checkout')
router.register(r'giftcards', GiftCardViewSet)
router.register(r'items', OrderItemViewSet)

urlpatterns = [
    path('management/', orders_management, name='orders-management'),
    path('dashboard/', admin_dashboard, name='admin-dashboard'),
    path('print/<int:order_id>/', print_order_receipt, name='print_order_receipt'),
    
    # 🌟 هذا السطر هو الذي سيحل مشكلة الـ 404 🌟
    path('workshop/', workshop_view, name='workshop'), 
    path('close-shift/', close_shift_api, name='close-shift'),

    path('shift-reports/', views.shift_reports_list, name='shift-reports-list'), # 👈 أضف هذا السطر
    
    path('', include(router.urls)),
    path('api/services/expense-categories/', views.expense_categories_list, name='expense-categories'),
    path('api/reports/save-expense/', views.save_expense, name='save-expense'),
    path('orders-report/', views.orders_report_page, name='orders_report_page'),
path('api/orders-report-data/', views.api_orders_report_data, name='api_orders_report_data'),
path('api/orders-report-csv/', views.export_orders_csv, name='export_orders_csv'),
path('revenue-report/', views.revenue_report_page, name='revenue_report_page'),
    path('api/revenue-report-data/', views.api_revenue_report_data, name='api_revenue_report_data'),
    path('api/revenue-report-excel/', views.export_revenue_excel, name='export_revenue_excel'),
    path('api/print-grouped-receipt/', views.print_grouped_receipt, name='print_grouped_receipt'),
    path('balance-sheet/', views.balance_sheet_page, name='balance_sheet_page'),
    path('api/balance-sheet-data/', views.api_balance_sheet_data, name='api_balance_sheet_data'),
    path('api/balance-sheet-excel/', views.export_balance_sheet_excel, name='export_balance_sheet_excel'),
    path('collection-report/', views.collection_report_page, name='collection_report_page'),
    path('api/collection-report-data/', views.api_collection_report_data, name='api_collection_report_data'),
    path('api/collection-excel/', views.export_collection_excel, name='export_collection_excel'),
    path('customer-ledger/', views.customer_ledger_page, name='customer_ledger_page'),
    path('api/customer-ledger-data/', views.api_ledger_report_data, name='api_ledger_report_data'),
    path('api/customer-ledger-export/', views.export_ledger_excel, name='export_ledger_excel'),
    path('profitability-report/', views.profitability_report_page, name='profitability_report_page'),
    path('api/profitability-data/', views.api_profitability_report_data, name='api_profitability_report_data'),
    path('api/profitability-export/', views.export_profitability_excel, name='export_profitability_excel'),
    path('profit-loss/', views.profit_loss_page, name='profit_loss_page'),
    path('api/profit-loss-data/', views.api_profit_loss_data, name='api_profit_loss_data'),
    path('api/profit-loss-export/', views.export_profit_loss_excel, name='export_profit_loss_excel'),
    path('purchases-report/', views.purchase_report_page, name='purchase_report_page'),
    path('api/purchases-data/', views.api_purchase_report_data, name='api_purchase_report_data'),
    path('api/purchases-export/', views.export_purchase_excel, name='export_purchase_excel'),
    path('inventory/products/', views.inventory_products_page, name='inventory_products_page'),
    path('api/inventory/products/', views.api_inventory_products, name='api_inventory_products'),
    path('api/inventory/products/export/', views.export_inventory_excel, name='export_inventory_excel'),
    path('inventory/stock-report/', views.stock_report_page, name='stock_report_page'),
    path('api/inventory/stock-data/', views.api_stock_report_data, name='api_stock_report_data'),
    path('api/inventory/stock-export/', views.export_stock_excel, name='export_stock_excel'),
    path('reports/inventory-valuation/', views.inventory_valuation_report_page, name='inventory_valuation_report_page'),
    path('api/reports/inventory-valuation-data/', views.api_inventory_valuation_data, name='api_inventory_valuation_data'),
    path('api/reports/inventory-valuation-export/', views.export_inventory_valuation_excel, name='export_inventory_valuation_excel'),
    path('reports/trial-balance/', views.trial_balance_page, name='trial_balance_page'),
    path('api/reports/trial-balance-data/', views.api_trial_balance_data, name='api_trial_balance_data'),
    path('api/reports/trial-balance-export/', views.export_trial_balance_excel, name='export_trial_balance_excel'),
    path('api/export-service-catalog/', views.export_service_catalog_excel, name='export_service_catalog_excel'),
]