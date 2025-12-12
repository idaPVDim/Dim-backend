from rest_framework.routers import DefaultRouter
from .views import TechnicalRequestViewSet, VendorQuoteViewSet

router = DefaultRouter()
router.register(r'technical-requests', TechnicalRequestViewSet, basename='technicalrequest')
router.register(r'vendor-quotes', VendorQuoteViewSet, basename='vendorquote')

urlpatterns = router.urls
