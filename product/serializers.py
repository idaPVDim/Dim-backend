from rest_framework import serializers
from .models import Categorie, Marque, Equipement


class CategorieSerializer(serializers.ModelSerializer):
    enfants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'parent', 'enfants']

    def get_enfants(self, obj):
        # Sérialiser récursivement les enfants (catégories filles)
        enfants = obj.enfants.all()
        serializer = CategorieSerializer(enfants, many=True, context=self.context)
        return serializer.data


class MarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marque
        fields = ['id', 'nom']


class EquipementSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(), source='categorie', write_only=True
    )

    marque = MarqueSerializer(read_only=True)
    marque_id = serializers.PrimaryKeyRelatedField(
        queryset=Marque.objects.all(), source='marque', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Equipement
        fields = [
            'id',
            'nom',
            'description',
            'categorie',
            'categorie_id',
            'marque',
            'marque_id',
            'puissance_W',
            'tension_V',
            'frequence_Hz',
            'capacite_Ah',
            'taille',
            'type_equipement',
            'mode',
        ]
