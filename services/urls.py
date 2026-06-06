from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, LaundryItemViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'items', LaundryItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]