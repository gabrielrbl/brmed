from rest_framework.routers import DefaultRouter
from django.urls import path
from django.conf.urls import include
from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r'currencies', views.CurrencyViewSet, basename='currencies')
router.register(r'rates', views.RateViewSet, basename='rates')

urlpatterns = [
    path('', views.home, name='home'),
    path('api/', include(router.urls)),
]
