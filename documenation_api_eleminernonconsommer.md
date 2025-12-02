from rest_framework import serializers
from .models import Categorie, Marque, Equipement

# =========================
# CATEGORIE
# =========================
class CategorieSerializer(serializers.ModelSerializer):
    enfants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'parent', 'enfants']

    def get_enfants(self, obj):
        enfants = obj.enfants.all()
        serializer = CategorieSerializer(enfants, many=True, context=self.context)
        return serializer.data


# =========================
# MARQUE
# =========================
class MarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marque
        fields = ['id', 'nom']


# =========================
# EQUIPEMENT / PRODUIT
# =========================
class EquipementSerializer(serializers.ModelSerializer):
    # Relations read-only
    categorie = CategorieSerializer(read_only=True)
    marque = MarqueSerializer(read_only=True)
    marchant_nom = serializers.CharField(source='marchant.nom_boutique', read_only=True)
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)

    # Relations write-only pour POST / PUT / PATCH
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(), source='categorie', write_only=True
    )
    marque_id = serializers.PrimaryKeyRelatedField(
        queryset=Marque.objects.all(), source='marque', write_only=True, allow_null=True, required=False
    )

    # Champs Decimal / Integer explicites
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
    courant_puissance_max_Imp = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    courant_court_circuit_ISC = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_puissance_max_VMP = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_circuit_ouvert_VOC = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    tension_maximale_systeme_V = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    rendement_pourcent = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    courant_charge_A = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    ir_initiale_mOhm = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    poids_kg = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    prix_unitaire_fcfa = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True, required=False)

    class Meta:
        model = Equipement
        fields = [
            'id', 'nom', 'description', 'type_equipement', 'mode', 'mode_display',
            'categorie', 'categorie_id', 'marque', 'marque_id', 'marchant_nom',
            'puissance_W', 'puissance_VA', 'puissance_nominale_W', 'tension_V', 'tension_entree_DC_V',
            'tension_sortie_AC_V', 'frequence_Hz', 'capacite_Ah', 'energie_Wh',
            'taille', 'taille_mm', 'poids_kg',
            'efficacite_module_pourcent', 'courant_puissance_max_Imp', 'courant_court_circuit_ISC',
            'tension_puissance_max_VMP', 'tension_circuit_ouvert_VOC', 'tension_maximale_systeme_V',
            'forme_onde', 'rendement_pourcent', 'courant_charge_A', 'cycle_vie_cycles', 'ir_initiale_mOhm',
            'type_stockage', 'puissance_PV_max_12V', 'puissance_PV_max_24V', 'puissance_PV_max_48V',
            'caracteristiques_additionnelles', 'description_technique', 'prix_unitaire_fcfa', 'quantite_stock',
            'est_disponible', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['date_creation', 'date_modification', 'marchant_nom', 'mode_display']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'profil_marchand'):
            validated_data['marchant'] = request.user.profil_marchand
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
