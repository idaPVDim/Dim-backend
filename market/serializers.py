# market/serializers.py
from rest_framework import serializers
from .models import (
    TechnicalRequest, TechnicalRequestItem,
    VendorQuote, VendorQuoteItem, SelectedVendorQuote
)
from product.serializers import EquipementSerializer
from product.models import Equipement

class TechnicalRequestItemSerializer(serializers.ModelSerializer):
    equipement_detail = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = TechnicalRequestItem
        fields = ["id", "equipement", "equipement_detail", "nom_libre", "quantite", "caracteristiques", "commentaire"]
    def get_equipement_detail(self, obj):
        if obj.equipement:
            return EquipementSerializer(obj.equipement, context=self.context).data
        return None

class TechnicalRequestSerializer(serializers.ModelSerializer):
    items = TechnicalRequestItemSerializer(many=True)
    destinataires_ids = serializers.PrimaryKeyRelatedField(queryset=__import__('user').models.ProfilMarchand.objects.all(), many=True, write_only=True, required=False)

    class Meta:
        model = TechnicalRequest
        fields = ["id", "reference", "installation", "createur", "technicien", "titre", "description", "date_creation", "date_envoi", "statut", "items", "destinataires_ids"]
        read_only_fields = ["reference", "date_creation", "createur", "date_envoi"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        destinataires = validated_data.pop("destinataires_ids", [])
        user = self.context["request"].user
        validated_data["createur"] = user
        tr = TechnicalRequest.objects.create(**validated_data)
        if destinataires:
            tr.destinataires.set(destinataires)
        for item in items_data:
            TechnicalRequestItem.objects.create(request=tr, **item)
        return tr

class VendorQuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorQuoteItem
        fields = ["id","technical_item","equipement","nom_libre","quantite","prix_unitaire_fcfa","prix_total_fcfa","disponibilite","garantie_mois"]

class VendorQuoteSerializer(serializers.ModelSerializer):
    items = VendorQuoteItemSerializer(many=True)
    marchant_id = serializers.PrimaryKeyRelatedField(queryset=__import__('user').models.ProfilMarchand.objects.all(), source="marchant", write_only=True)
    entreprise = serializers.PrimaryKeyRelatedField(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = VendorQuote
        fields = ["id","reference","technical_request","marchant","marchant_id","entreprise","date_reponse","validite_jours","delai_livraison_jours","commentaire","statut","items","total"]
        read_only_fields = ["reference","date_reponse","entreprise","total"]

    def get_total(self, obj):
        return obj.total_materiel()

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        marchant = validated_data.pop("marchant")
        # entreprise from marchant if exists
        entreprise = getattr(marchant, "entreprise", None)
        vq = VendorQuote.objects.create(marchant=marchant, entreprise=entreprise, **validated_data)
        for it in items_data:
            VendorQuoteItem.objects.create(quote=vq, **it)
        return vq
