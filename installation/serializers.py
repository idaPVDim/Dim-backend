from rest_framework import serializers
from .models import (
    Province,
    Installation,
    InstallationEquipement,
    SchemaInstallation,
    Devis,
    ComparaisonEconomique,
)
from maintenance.models import Incident, Maintenance, QuestionMaintenance, ReponseMaintenance
from product.serializers import EquipementSerializer  # Assurez-vous de l'avoir
from user.serializers import ProfilClientSerializer, ProfilTechnicienSerializer  # Idem
from user.models import ProfilClient, ProfilTechnicien
from rest_framework import serializers

class ClientInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = ProfilClient
        fields = ['first_name', 'last_name', 'email', 'address', 'consommation_annuelle_moyenne_kwh']

from rest_framework import serializers

class TechnicienInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = ProfilTechnicien
        fields = [
            'first_name', 'last_name', 'email', 'is_certified', 'zone_couverture',
            'id_document', 'formation_document', 'certification_docs',
            'autorisation_docs', 'autres_docs'
        ]

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'nom', 'irradiation']


class InstallationEquipementSerializer(serializers.ModelSerializer):
    equipement = EquipementSerializer(read_only=True)
    equipement_id = serializers.PrimaryKeyRelatedField(
        queryset=EquipementSerializer.Meta.model.objects.all(),
        write_only=True,
        source='equipement'
    )
    source = serializers.ChoiceField(choices=InstallationEquipement._meta.get_field('source').choices)

    class Meta:
        model = InstallationEquipement
        fields = ['id', 'equipement', 'equipement_id', 'quantite', 'source']


class InstallationSerializer(serializers.ModelSerializer):
    client = ClientInfoSerializer(read_only=True)
    technicien = TechnicienInfoSerializer(read_only=True, allow_null=True)
    province = ProvinceSerializer(read_only=True)
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(),
        source='province',
        write_only=True
    )

    equipements_proposes = InstallationEquipementSerializer(
        source='installationequipement_set',
        many=True,
        required=False
    )

    source_donnees = serializers.ChoiceField(choices=Installation._meta.get_field('source_donnees').choices)

    class Meta:
        model = Installation
        fields = [
            'id', 'client', 'technicien', 'source_donnees',
            'province', 'province_id',
            'budget_client', 'surface_disponible_m2', 'contraintes_specifiques',
            'status', 'date_creation', 'date_derniere_mise_a_jour',
            'equipements_proposes'
        ]

    def create(self, validated_data):
        equipements_data = validated_data.pop('installationequipement_set', [])
        installation = Installation.objects.create(**validated_data)
        for eq_data in equipements_data:
            InstallationEquipement.objects.create(installation=installation, **eq_data)
        return installation

    def update(self, instance, validated_data):
        equipements_data = validated_data.pop('installationequipement_set', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Mise à jour simplifiée des équipements : suppression + recréation
        instance.installationequipement_set.all().delete()
        for eq_data in equipements_data:
            InstallationEquipement.objects.create(installation=instance, **eq_data)
        return instance


class SchemaInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaInstallation
        fields = ['id', 'installation', 'fichier_schema', 'description', 'date_creation']


class DevisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devis
        fields = [
            'id', 'installation', 'cout_achat_equipements',
            'cout_installation_main_oeuvre', 'cout_maintenance_estime_an',
            'montant_total', 'date_creation', 'fichier_devis_pdf'
        ]


class ComparaisonEconomiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparaisonEconomique
        fields = [
            'id', 'devis', 'cout_electricite_traditionnelle_estime_an',
            'economies_potentielles_annuelles', 'duree_retour_investissement_annees'
        ]


