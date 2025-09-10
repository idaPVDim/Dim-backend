from rest_framework import viewsets, permissions
from .models import Incident, Maintenance, QuestionMaintenance, ReponseMaintenance
from .serializers import (
    IncidentSerializer,
    MaintenanceSerializer,
    QuestionMaintenanceSerializer,
    ReponseMaintenanceSerializer,
)

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuestionMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = QuestionMaintenance.objects.all()
    serializer_class = QuestionMaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReponseMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = ReponseMaintenance.objects.all()
    serializer_class = ReponseMaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
