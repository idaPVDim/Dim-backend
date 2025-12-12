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


# installation/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Devis, LigneDevis, ServiceDevisFinal, ConditionsDevis
from product.serializers import EquipementSerializer  # si tu veux embed equipement
from product.models import Equipement

User = get_user_model()

class LigneDevisSerializer(serializers.ModelSerializer):
    equipement_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LigneDevis
        fields = [
            "id", "equipement", "equipement_detail",
            "quantite", "prix_unitaire", "prix_total",
            "disponibilite", "garantie_mois", "commentaires"
        ]

    def get_equipement_detail(self, obj):
        try:
            return {"id": obj.equipement.id, "nom": obj.equipement.nom}
        except:
            return None

    def validate(self, data):
        # calcul automatique prix_total si prix_unitaire et quantite fournis
        if data.get("prix_unitaire") is not None and "quantite" in data:
            data["prix_total"] = data["prix_unitaire"] * data["quantite"]
        return data


class ServiceDevisFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDevisFinal
        fields = ["id", "nom", "description", "prix"]


class ConditionsDevisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionsDevis
        fields = ["id", "validite_jours", "garantie_installation_mois", "modalites_paiement"]


class DevisSerializer(serializers.ModelSerializer):
    lignes = LigneDevisSerializer(many=True, required=False)
    services = ServiceDevisFinalSerializer(many=True, required=False)
    conditions = ConditionsDevisSerializer(required=False, allow_null=True)
    emetteur_email = serializers.ReadOnlyField(source='emetteur.email')
    destinataire_email = serializers.ReadOnlyField(source='destinataire.email')

    class Meta:
        model = Devis
        fields = [
            "id", "type_devis", "statut",
            "titre_projet", "emetteur", "emetteur_email", "destinataire", "destinataire_email",
            "nom_client", "telephone_client", "localisation_client",
            "date_creation", "date_mise_a_jour",
            "lignes", "services", "conditions", "fichier_devis_pdf",
        ]
        read_only_fields = ["date_creation", "date_mise_a_jour", "fichier_devis_pdf"]

    def create(self, validated_data):
        lignes_data = validated_data.pop("lignes", [])
        services_data = validated_data.pop("services", [])
        conditions_data = validated_data.pop("conditions", None)

        # emetteur doit être l'utilisateur courant (en view.perform_create on set)
        devis = Devis.objects.create(**validated_data)

        for l in lignes_data:
            LigneDevis.objects.create(devis=devis, **l)

        for s in services_data:
            ServiceDevisFinal.objects.create(devis=devis, **s)

        if conditions_data:
            ConditionsDevis.objects.create(devis=devis, **conditions_data)

        return devis

    def update(self, instance, validated_data):
        # update simples pour champs principaux
        lignes_data = validated_data.pop("lignes", None)
        services_data = validated_data.pop("services", None)
        conditions_data = validated_data.pop("conditions", None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if lignes_data is not None:
            # strategy simple : supprimer et recréer (pour MVP)
            instance.lignes.all().delete()
            for l in lignes_data:
                LigneDevis.objects.create(devis=instance, **l)

        if services_data is not None:
            instance.services.all().delete()
            for s in services_data:
                ServiceDevisFinal.objects.create(devis=instance, **s)

        if conditions_data is not None:
            if hasattr(instance, "conditions"):
                for attr, val in conditions_data.items():
                    setattr(instance.conditions, attr, val)
                instance.conditions.save()
            else:
                ConditionsDevis.objects.create(devis=instance, **conditions_data)
        return instance

# ==========================================================
# COMPARAISON ÉCONOMIQUE
# ==========================================================
class ComparaisonEconomiqueSerializer(serializers.ModelSerializer):
    devis_detail = DevisSerializer(source="devis", read_only=True)

    class Meta:
        model = ComparaisonEconomique
        fields = "__all__"


