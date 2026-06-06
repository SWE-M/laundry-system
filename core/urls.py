from django.contrib import admin
from django.urls import path, include
from services import views as services_views
from orders.views import orders_management
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static

# استدعاء دوال الدخول والخروج من تطبيق accounts
from accounts.views import custom_login_view, custom_logout_view 
from django.contrib.auth.decorators import login_required
from accounts.views import chart_of_accounts_view
from accounts.views import ledger_report_view
from accounts.views import ledger_report_view, trial_balance_view
from accounts.views import api_trial_balance_data

urlpatterns = [
    # التوجيه الافتراضي إلى صفحة تسجيل الدخول
    path('', RedirectView.as_view(url='/login/', permanent=False)), 

    path('admin/', admin.site.urls),

    # روابط تسجيل الدخول والخروج
    path('login/', custom_login_view, name='login'),
    path('logout/', custom_logout_view, name='logout'),

    # روابط الـ APIs
    path('api/services/', include('services.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/accounts/', include('accounts.urls')),


    path('api/branches/', include('branches.urls')), 
    path('api/reports/', include('services.expense_urls')),

    # ==========================================
    # 🛡️ الروابط الرئيسية المحمية (لا تُفتح إلا بتسجيل دخول)
    # ==========================================
    
    # حماية الدوال (Views)
    path('cashier/', login_required(services_views.cashier_view, login_url='/login/'), name='cashier'),
    path('customers/', login_required(services_views.customers_page, login_url='/login/'), name='customers_page'),
    path('orders/management/', login_required(orders_management, login_url='/login/'), name='orders_management'),

    # حماية الصفحات الثابتة (TemplateViews) للوحة الإدارة والورشة
    path('admin-dashboard/', login_required(TemplateView.as_view(template_name='admin_dashboard.html'), login_url='/login/'), name='admin_dashboard'),
    path('workshop/', login_required(TemplateView.as_view(template_name='workshop.html'), login_url='/login/'), name='workshop'),
    
    # صفحات إدارة النظام (محمية)
    path('items-management/', login_required(TemplateView.as_view(template_name='items_management.html'), login_url='/login/'), name='items_management'),
    path('customers-management/', login_required(TemplateView.as_view(template_name='customers_management.html'), login_url='/login/'), name='customers_management'),
    path('staff-management/', login_required(TemplateView.as_view(template_name='staff_management.html'), login_url='/login/'), name='staff_management'),
    # رابط صفحة إدارة المشتريات (ضروري جداً للدخول للصفحة)
    path('purchases-management/', login_required(TemplateView.as_view(template_name='purchases_management.html'), login_url='/login/'), name='purchases_management'),
    # ==========================================
    # 📄 صفحات الطباعة (الإيصالات) - يمكن تركها بدون حماية أو حمايتها
    # ==========================================
    path('debt-receipt/', TemplateView.as_view(template_name='debt_receipt.html'), name='debt_receipt'), 
    path('gift-card-receipt/', TemplateView.as_view(template_name='gift_card_receipt.html'), name='gift_card_receipt'),
    path('wallet-recharge-receipt/', TemplateView.as_view(template_name='wallet_recharge_receipt.html'), name='wallet_recharge_receipt'),
    path('wallet-balance-print/', TemplateView.as_view(template_name='wallet_balance_receipt.html'), name='wallet_balance_print'),
    path('gift-card-balance-print/', TemplateView.as_view(template_name='gift_card_balance_receipt.html'), name='gift_card_balance_print'),
    path('orders/', include('orders.urls')),
    path('chart-of-accounts/', chart_of_accounts_view, name='chart_of_accounts'),
    path('ledger-report/', ledger_report_view, name='ledger_report'),
    path('trial-balance/', trial_balance_view, name='trial_balance'),
    path('api/accounts/trial-balance-data/', api_trial_balance_data, name='api_trial_balance_data'),
]

# إعدادات ملفات الميديا للصور في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)