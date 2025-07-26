from rest_framework import serializers
from .models import Installation, InstallationEquipement, Devis, ComparaisonEconomique, SchemaInstallation
from product.serializers import EquipementSerializer
from user.serializers import ProfilClientSerializer, ProfilTechnicienSerializer

class InstallationEquipementSerializer(serializers.ModelSerializer):
    equipement = EquipementSerializer(read_only=True)
    equipement_id = serializers.PrimaryKeyRelatedField(queryset=EquipementSerializer.Meta.model.objects.all(), source='equipement', write_only=True)

    class Meta:
        model = InstallationEquipement
        fields = ['id', 'equipement', 'equipement_id', 'quantite']

class InstallationSerializer(serializers.ModelSerializer):
    client = ProfilClientSerializer(read_only=True)
    technicien = ProfilTechnicienSerializer(read_only=True)
    equipements_proposes = InstallationEquipementSerializer(many=True, source='installationequipement_set', read_only=True)

    # Pour créer/modifier équipements proposés via l’installation
    new_equipements = InstallationEquipementSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Installation
        fields = [
            'id', 'client', 'technicien', 'consommation_energetique',
            'province', 'budget_client', 'surface_disponible_m2', 'contraintes_specifiques',
            'status', 'date_creation', 'date_derniere_mise_a_jour', 'equipements_proposes', 'new_equipements',
        ]
        read_only_fields = ['date_creation', 'date_derniere_mise_a_jour', 'equipements_proposes']

    def create(self, validated_data):
        new_equipements_data = validated_data.pop('new_equipements', [])
        installation = Installation.objects.create(**validated_data)

        for equip_data in new_equipements_data:
            InstallationEquipement.objects.create(installation=installation, **equip_data)

        return installation

    def update(self, instance, validated_data):
        new_equipements_data = validated_data.pop('new_equipements', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if new_equipements_data is not None:
            # Supprimez les anciens équipements liés si besoin ou adaptez la logique
            instance.installationequipement_set.all().delete()
            for equip_data in new_equipements_data:
                InstallationEquipement.objects.create(installation=instance, **equip_data)

        return instance

class SchemaInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaInstallation
        fields = '__all__'

class DevisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devis
        fields = '__all__'

class ComparaisonEconomiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparaisonEconomique
        fields = '__all__'
