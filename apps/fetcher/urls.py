from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientDataSourceConfigViewSet

router = DefaultRouter()
router.register(r'fetch-configs', ClientDataSourceConfigViewSet)

urlpatterns = [
  path('', include(router.urls)),
]