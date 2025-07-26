from rest_framework.routers import DefaultRouter
from .views import InstallationViewSet, SchemaInstallationViewSet, DevisViewSet, ComparaisonEconomiqueViewSet

router = DefaultRouter()
router.register(r'installations', InstallationViewSet, basename='installation')
router.register(r'schemas', SchemaInstallationViewSet, basename='schemainstallation')
router.register(r'devis', DevisViewSet, basename='devis')
router.register(r'comparaisons', ComparaisonEconomiqueViewSet, basename='comparaisoneconomique')

urlpatterns = router.urls
