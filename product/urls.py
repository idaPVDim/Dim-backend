from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategorieViewSet, 
    MarqueViewSet, 
    EquipementPublicViewSet,      # ✅ Vue publique
    EquipementMarchandViewSet,    # ✅ Vue pour marchands
    EquipementAdminViewSet,       # ✅ Vue pour admin (optionnel)
   # StockViewSet
)

router = DefaultRouter()
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'marques', MarqueViewSet, basename='marque')

# ✅ Vue publique - accessible à tous
router.register(r'equipements/public', EquipementPublicViewSet, basename='equipement-public')

# ✅ Vue pour marchands - gestion de leurs produits
router.register(r'equipements/marchand', EquipementMarchandViewSet, basename='equipement-marchand')

# ✅ Vue pour admin - accès à tout (optionnel)
router.register(r'equipements/admin', EquipementAdminViewSet, basename='equipement-admin')

# ✅ Stock management (maintenez votre vue existante)
#router.register(r"stock", StockViewSet, basename="stock")

urlpatterns = [
    path('api/', include(router.urls)),
]