from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategorieViewSet, MarqueViewSet, EquipementViewSet , StockViewSet

router = DefaultRouter()
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'marques', MarqueViewSet, basename='marque')
router.register(r'equipements', EquipementViewSet, basename='equipement')
router.register(r"stock", StockViewSet, basename="stock")

urlpatterns = [
    path('api/', include(router.urls)),
]
