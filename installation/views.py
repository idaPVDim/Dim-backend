from rest_framework import viewsets, permissions
from .models import Installation, InstallationEquipement, SchemaInstallation, Devis, ComparaisonEconomique ,Province
from .serializers import (
    InstallationSerializer,
    InstallationEquipementSerializer,
    SchemaInstallationSerializer,
    DevisSerializer,
    ComparaisonEconomiqueSerializer,
    ProvinceSerializer
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [IsAuthenticated]

class InstallationViewSet(viewsets.ModelViewSet):
    queryset = Installation.objects.all()
    serializer_class = InstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Associer automatiquement le client connecté
        serializer.save(client=self.request.user.profilclient)

class InstallationEquipementViewSet(viewsets.ModelViewSet):
    queryset = InstallationEquipement.objects.all()
    serializer_class = InstallationEquipementSerializer
    permission_classes = [permissions.IsAuthenticated]

class SchemaInstallationViewSet(viewsets.ModelViewSet):
    queryset = SchemaInstallation.objects.all()
    serializer_class = SchemaInstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

class DevisViewSet(viewsets.ModelViewSet):
    queryset = Devis.objects.all()
    serializer_class = DevisSerializer
    permission_classes = [permissions.AllowAny]

class ComparaisonEconomiqueViewSet(viewsets.ModelViewSet):
    queryset = ComparaisonEconomique.objects.all()
    serializer_class = ComparaisonEconomiqueSerializer
    permission_classes = [permissions.AllowAny]
