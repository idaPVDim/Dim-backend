from rest_framework import serializers
from .models import EquipementDimensionnement, DimensionnementPV, DevisProduit
from product.models import Equipement

class EquipementDimensionnementSerializer(serializers.ModelSerializer):
    equipement_nom = serializers.ReadOnlyField(source='equipement.nom')
    puissance_nominale_w = serializers.ReadOnlyField(source='equipement.puissance_nominale_W')

    class Meta:
        model = EquipementDimensionnement
        fields = ['id', 'equipement', 'equipement_nom', 'quantite', 'temps_utilisation_h', 'puissance_nominale_w', 'source']

    def validate_equipement(self, value):
        if not Equipement.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Équipement inconnu.")
        return value

class DimensionnementPVSerializer(serializers.ModelSerializer):
    equipements = EquipementDimensionnementSerializer(many=True)
    consommation_totale = serializers.SerializerMethodField()
    
    class Meta:
        model = DimensionnementPV
        fields = '__all__'

    def get_consommation_totale(self, obj):
        return obj.consommation_totale_journaliere()

    def validate(self, data):
        avec_stockage = data.get('avec_stockage', getattr(self.instance, 'avec_stockage', True))
        if avec_stockage:
            champs_requis = ['capacite_unitaire_batterie_ah', 'tension_unitaire_batterie_v', 'autonomie_jours', 'profondeur_decharge']
            for champ in champs_requis:
                if not data.get(champ) and not (self.instance and getattr(self.instance, champ, None)):
                    raise serializers.ValidationError({champ: "Champ requis lorsque stockage activé."})
        return data

    def create(self, validated_data):
        equipements_data = validated_data.pop('equipements')
        dimensionnement = DimensionnementPV.objects.create(**validated_data)
        # Créer les équipements
        for equip_data in equipements_data:
            EquipementDimensionnement.objects.create(dimensionnement=dimensionnement, **equip_data)
        # Faire calcul automatique
        dimensionnement = self.calculer_dimensionnement(dimensionnement)
        dimensionnement.save()
        return dimensionnement

    def update(self, instance, validated_data):
        equipements_data = validated_data.pop('equipements', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if equipements_data is not None:
            instance.equipements.all().delete()
            for equip_data in equipements_data:
                EquipementDimensionnement.objects.create(dimensionnement=instance, **equip_data)
        instance = self.calculer_dimensionnement(instance)
        instance.save()
        return instance

    def calculer_dimensionnement(self, dimensionnement):
        # Calcul consommation sécurisée
        consommation = dimensionnement.consommation_totale_journaliere()
        consommation_securisee = consommation * 1.25

        # Données environnementales
        installation = dimensionnement.installation
        irradiation = float(installation.province.irradiation)
        facteur_rendement = float(dimensionnement.facteur_rendement)

        # Puissance crête en Wc
        puissance_crete = consommation_securisee / (irradiation * 1000 * facteur_rendement)
        dimensionnement.puissance_crete_wc = puissance_crete

        # Tension champ
        if puissance_crete < 500:
            tension_champ = 12
        elif puissance_crete < 2000:
            tension_champ = 24
        elif puissance_crete < 10000:
            tension_champ = 48
        else:
            tension_champ = 96
        dimensionnement.tension_champ_v = tension_champ

        # Nombre panneaux
        Pu = dimensionnement.puissance_unitaire_panneau_w
        Up = dimensionnement.tension_unitaire_panneau_volt
        nombre_total_panneaux = round(puissance_crete / Pu)
        ns = int(tension_champ / Up)
        np = round(nombre_total_panneaux / ns) if ns > 0 else 1

        dimensionnement.nombre_total_panneaux = nombre_total_panneaux
        dimensionnement.nombre_panneaux_serie = ns
        dimensionnement.nombre_panneaux_parallele = np

        # Dimensionnement batterie si besoin
        if dimensionnement.avec_stockage:
            U_bat = dimensionnement.tension_unitaire_batterie_v
            C_bat = dimensionnement.capacite_unitaire_batterie_ah
            nj = dimensionnement.autonomie_jours
            d = float(dimensionnement.profondeur_decharge)

            Ct = (nj * consommation_securisee) / (tension_champ * d)
            Nbat = int(round(Ct / C_bat) * (tension_champ / U_bat))
            nbs = int(tension_champ / U_bat)
            nbp = int(round(Nbat / nbs)) if nbs > 0 else 1

            dimensionnement.capacite_batterie_ah = Ct
            dimensionnement.nombre_total_batteries = Nbat
            dimensionnement.nombre_batteries_serie = nbs
            dimensionnement.nombre_batteries_parallele = nbp
        else:
            dimensionnement.capacite_batterie_ah = None
            dimensionnement.nombre_total_batteries = None
            dimensionnement.nombre_batteries_serie = None
            dimensionnement.nombre_batteries_parallele = None

        return dimensionnement

class DevisProduitSerializer(serializers.ModelSerializer):
    equipement_nom = serializers.ReadOnlyField(source='equipement.nom')

    class Meta:
        model = DevisProduit
        fields = ['id', 'equipement', 'equipement_nom', 'quantite', 'prix_unitaire_fcfa', 'prix_total_fcfa']
