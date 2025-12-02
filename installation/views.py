from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal

from .models import (
    Province,
    Installation,
    InstallationEquipement,
    SchemaInstallation,
    Devis,
    ComparaisonEconomique
)
from .serializers import (
    ProvinceSerializer,
    InstallationSerializer,
    InstallationEquipementSerializer,
    SchemaInstallationSerializer,
    DevisSerializer,
    ComparaisonEconomiqueSerializer
)
from product.models import Equipement
from user.models import ProfilTechnicien

# ==================================================
# Province
# ==================================================
class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [permissions.IsAuthenticated]

# ==================================================
# Installation
# ==================================================
class InstallationViewSet(viewsets.ModelViewSet):
    queryset = Installation.objects.all()
    serializer_class = InstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.profilclient)

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profilclient"):
            return Installation.objects.filter(client=user.profilclient)
        if hasattr(user, "profiltechnicien"):
            return Installation.objects.filter(technicien=user.profiltechnicien)
        return Installation.objects.none()

    # ------------------------
    # Assign technician
    # ------------------------
    @action(detail=True, methods=['post'], url_path='assign-technician')
    def assign_technician(self, request, pk=None):
        installation = self.get_object()
        technicien_id = request.data.get("technicien_id")
        if not technicien_id:
            return Response({"error": "technicien_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            technicien = ProfilTechnicien.objects.get(id=technicien_id)
            installation.technicien = technicien
            installation.save()
            return Response({"success": f"Technician {technicien.user.username} assigned."})
        except ProfilTechnicien.DoesNotExist:
            return Response({"error": "Technician not found"}, status=status.HTTP_404_NOT_FOUND)

    # ------------------------
    # Change installation status
    # ------------------------
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        installation = self.get_object()
        status_value = request.data.get("status")
        if status_value not in dict(Installation.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        installation.status = status_value
        installation.save()
        return Response({"success": f"Status changed to {status_value}"})

    # ------------------------
    # Add equipment to installation + manage stock
    # ------------------------
    @action(detail=True, methods=['post'], url_path='add-equipement')
    def add_equipement(self, request, pk=None):
        installation = self.get_object()
        equipement_id = request.data.get("equipement_id")
        quantite = int(request.data.get("quantite", 1))
        source = request.data.get("source", "technicien")

        if not equipement_id:
            return Response({"error": "equipement_id required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            equipement = Equipement.objects.get(id=equipement_id)

            # Stock check
            if equipement.quantite_stock < quantite:
                return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)

            # Add or update InstallationEquipement
            ie, created = InstallationEquipement.objects.get_or_create(
                installation=installation,
                equipement=equipement,
                defaults={"quantite": quantite, "source": source}
            )
            if not created:
                ie.quantite += quantite
                ie.save()

            # Reduce stock
            equipement.quantite_stock -= quantite
            equipement.save()

            return Response({"success": f"{quantite} × {equipement.nom} added to installation."})
        except Equipement.DoesNotExist:
            return Response({"error": "Equipement not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================================================
# InstallationEquipement
# ==================================================
class InstallationEquipementViewSet(viewsets.ModelViewSet):
    queryset = InstallationEquipement.objects.all()
    serializer_class = InstallationEquipementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profilclient"):
            return InstallationEquipement.objects.filter(installation__client=user.profilclient)
        if hasattr(user, "profiltechnicien"):
            return InstallationEquipement.objects.filter(installation__technicien=user.profiltechnicien)
        return InstallationEquipement.objects.none()


# ==================================================
# SchemaInstallation
# ==================================================
class SchemaInstallationViewSet(viewsets.ModelViewSet):
    queryset = SchemaInstallation.objects.all()
    serializer_class = SchemaInstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profilclient"):
            return SchemaInstallation.objects.filter(installation__client=user.profilclient)
        if hasattr(user, "profiltechnicien"):
            return SchemaInstallation.objects.filter(installation__technicien=user.profiltechnicien)
        return SchemaInstallation.objects.none()


# ==================================================
# Devis
# ==================================================
class DevisViewSet(viewsets.ModelViewSet):
    queryset = Devis.objects.all()
    serializer_class = DevisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profilclient"):
            return Devis.objects.filter(installation__client=user.profilclient)
        if hasattr(user, "profiltechnicien"):
            return Devis.objects.filter(installation__technicien=user.profiltechnicien)
        return Devis.objects.none()

    # ------------------------
    # Generate PDF + calculate total
    # ------------------------
    @action(detail=True, methods=['post'], url_path='generate-pdf')
    def generate_pdf(self, request, pk=None):
        devis = self.get_object()
        # Calculate equipment cost
        cout_equipements = sum(
            ie.quantite * ie.equipement.prix_unitaire_fcfa
            for ie in devis.installation.installationequipement_set.all()
        )
        devis.cout_achat_equipements = cout_equipements
        # Example: labor = 10% of equipment cost
        devis.cout_installation_main_oeuvre = cout_equipements * Decimal('0.1')
        devis.montant_total = devis.cout_achat_equipements + devis.cout_installation_main_oeuvre
        devis.save()
        return Response({
            "message": "Devis recalculated and PDF ready (simulation).",
            "montant_total": devis.montant_total
        })


# ==================================================
# ComparaisonEconomique
# ==================================================
class ComparaisonEconomiqueViewSet(viewsets.ModelViewSet):
    queryset = ComparaisonEconomique.objects.all()
    serializer_class = ComparaisonEconomiqueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profilclient"):
            return ComparaisonEconomique.objects.filter(devis__installation__client=user.profilclient)
        if hasattr(user, "profiltechnicien"):
            return ComparaisonEconomique.objects.filter(devis__installation__technicien=user.profiltechnicien)
        return ComparaisonEconomique.objects.none()
