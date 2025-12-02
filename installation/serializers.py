from rest_framework import serializers
from .models import (
    Province,
    Installation,
    InstallationEquipement,
    SchemaInstallation,
    Devis,
    ComparaisonEconomique
)
from product.serializers import EquipementSerializer
from user.serializers import ProfilClientSerializer, ProfilTechnicienSerializer


# ==========================================================
# PROVINCE
# ==========================================================
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = "__all__"


# ==========================================================
# INSTALLATION → EQUIPEMENTS
# ==========================================================
class InstallationEquipementSerializer(serializers.ModelSerializer):
    equipement_detail = EquipementSerializer(source="equipement", read_only=True)

    class Meta:
        model = InstallationEquipement
        fields = [
            "id",
            "installation",
            "equipement",
            "equipement_detail",
            "quantite",
            "source",
        ]


# ==========================================================
# INSTALLATION
# ==========================================================
class InstallationSerializer(serializers.ModelSerializer):
    client_detail = ProfilClientSerializer(source="client", read_only=True)
    technicien_detail = ProfilTechnicienSerializer(source="technicien", read_only=True)
    province_detail = ProvinceSerializer(source="province", read_only=True)

    equipements = InstallationEquipementSerializer(
        many=True,
        source='installationequipement_set',
        read_only=True
    )

    class Meta:
        model = Installation
        fields = [
            "id",
            "client",
            "client_detail",
            "technicien",
            "technicien_detail",
            "province",
            "province_detail",
            "source_donnees",
            "budget_client",
            "surface_disponible_m2",
            "contraintes_specifiques",
            "status",
            "date_creation",
            "date_derniere_mise_a_jour",
            "equipements",
        ]
        read_only_fields = ["date_creation", "date_derniere_mise_a_jour"]


# ==========================================================
# SCHÉMA INSTALLATION
# ==========================================================
class SchemaInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaInstallation
        fields = "__all__"


# ==========================================================
# DEVIS
# ==========================================================
class DevisSerializer(serializers.ModelSerializer):
    installation_detail = InstallationSerializer(source="installation", read_only=True)
    entreprise_nom = serializers.CharField(source="entreprise.nom", read_only=True)

    class Meta:
        model = Devis
        fields = [
            "id",
            "installation",
            "installation_detail",
            "entreprise",
            "entreprise_nom",
            "numero_devis",
            "cout_achat_equipements",
            "cout_installation_main_oeuvre",
            "cout_maintenance_estime_an",
            "montant_total",
            "fichier_devis_pdf",
            "date_creation",
        ]
        read_only_fields = ["date_creation"]


# ==========================================================
# COMPARAISON ÉCONOMIQUE
# ==========================================================
class ComparaisonEconomiqueSerializer(serializers.ModelSerializer):
    devis_detail = DevisSerializer(source="devis", read_only=True)

    class Meta:
        model = ComparaisonEconomique
        fields = "__all__"
