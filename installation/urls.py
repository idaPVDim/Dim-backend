from rest_framework.routers import DefaultRouter
from .views import (
    InstallationViewSet,
    InstallationEquipementViewSet,
    SchemaInstallationViewSet,
    DevisViewSet,
    ComparaisonEconomiqueViewSet,
    ProvinceViewSet
)

router = DefaultRouter()
router.register(r'provinces', ProvinceViewSet, basename='province')
router.register(r'installations', InstallationViewSet, basename='installation')
router.register(r'installation-equipements', InstallationEquipementViewSet, basename='installationequipement')
router.register(r'schemas', SchemaInstallationViewSet, basename='schemainstallation')
router.register(r'devis', DevisViewSet, basename='devis')
router.register(r'comparaisons-economiques', ComparaisonEconomiqueViewSet, basename='comparaisoneconomique')

urlpatterns = router.urls
