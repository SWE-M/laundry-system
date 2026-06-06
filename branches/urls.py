from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet # تأكد من وجود ViewSet في views.py

router = DefaultRouter()
router.register(r'', BranchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]