from rest_framework.routers import DefaultRouter
from .views import (
    IncidentViewSet,
    MaintenanceViewSet,
    QuestionMaintenanceViewSet,
    ReponseMaintenanceViewSet,
)

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'maintenances', MaintenanceViewSet, basename='maintenance')
router.register(r'questions-maintenance', QuestionMaintenanceViewSet, basename='questionmaintenance')
router.register(r'reponses-maintenance', ReponseMaintenanceViewSet, basename='reponsermaintenance')

urlpatterns = router.urls
