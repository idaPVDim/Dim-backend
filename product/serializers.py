from rest_framework import serializers
from .models import Categorie, Marque, Equipement


class CategorieSerializer(serializers.ModelSerializer):
    enfants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'parent', 'enfants']

    def get_enfants(self, obj):
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

    # Déclarez explicitement les DecimalFields en fixant max_digits et decimal_places selon votre modèle
    puissance_W = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    puissance_VA = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    puissance_nominale_W = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_V = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_entree_DC_V = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_sortie_AC_V = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    frequence_Hz = serializers.IntegerField(allow_null=True, required=False)
    capacite_Ah = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    energie_Wh = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True, required=False)
    efficacite_module_pourcent = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    tension_puissance_max_VMP = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    courant_puissance_max_Imp = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_circuit_ouvert_VOC = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    courant_court_circuit_ISC = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_maximale_systeme_V = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    calibre_max_fusibles_serie_A = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    rendement_pourcent = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    courant_charge_A = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    ir_initiale_mOhm = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    poids_kg = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)

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
            'puissance_VA',
            'puissance_nominale_W',
            'tension_V',
            'tension_entree_DC_V',
            'tension_sortie_AC_V',
            'frequence_Hz',
            'capacite_Ah',
            'energie_Wh',
            'taille',
            'type_equipement',
            'mode',
            'efficacite_module_pourcent',
            'tension_puissance_max_VMP',
            'courant_puissance_max_Imp',
            'tension_circuit_ouvert_VOC',
            'courant_court_circuit_ISC',
            'tolerance_puissance_W',
            'tension_maximale_systeme_V',
            'temperature_module_fonctionnement_C',
            'calibre_max_fusibles_serie_A',
            'cycle_vie_cycles',
            'ir_initiale_mOhm',
            'poids_kg',
            'forme_onde',
            'rendement_pourcent',
            'courant_charge_A',
            'tension_systeme_V',
            'tension_max_PV_V',
            'puissance_PV_max_12V',
            'puissance_PV_max_24V',
            'puissance_PV_max_48V',
            'caracteristiques_additionnelles',
            'conditions_test',
            'type_stockage',
        ]
