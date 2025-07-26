from rest_framework import viewsets, permissions
from .models import Installation, SchemaInstallation, Devis, ComparaisonEconomique
from .serializers import InstallationSerializer, SchemaInstallationSerializer, DevisSerializer, ComparaisonEconomiqueSerializer

class InstallationViewSet(viewsets.ModelViewSet):
    queryset = Installation.objects.all()
    serializer_class = InstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Assigner automatiquement le client connecté s’il est client - à adapter selon votre logique
        if self.request.user.role == 'client':
            profil_client = self.request.user.profil_client
            serializer.save(client=profil_client)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Installation.objects.filter(client=user.profil_client)
        elif user.role == 'technicien':
            return Installation.objects.filter(technicien=user.profil_technicien)
        # admin et autres roles voient tout
        return Installation.objects.all()


class SchemaInstallationViewSet(viewsets.ModelViewSet):
    queryset = SchemaInstallation.objects.all()
    serializer_class = SchemaInstallationSerializer
    permission_classes = [permissions.IsAuthenticated]


class DevisViewSet(viewsets.ModelViewSet):
    queryset = Devis.objects.all()
    serializer_class = DevisSerializer
    permission_classes = [permissions.IsAuthenticated]


class ComparaisonEconomiqueViewSet(viewsets.ModelViewSet):
    queryset = ComparaisonEconomique.objects.all()
    serializer_class = ComparaisonEconomiqueSerializer
    permission_classes = [permissions.IsAuthenticated]
