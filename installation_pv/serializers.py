from rest_framework import serializers

class AppareilSerializer(serializers.Serializer):
    puissance_nominale_W = serializers.FloatField()
    nombre = serializers.IntegerField()
    temps_utilisation_h = serializers.FloatField()

class DimensionnementPvSerializer(serializers.Serializer):
    appareils = AppareilSerializer(many=True)
    irradiation = serializers.FloatField(default=5.5)
    facteur_rendement = serializers.FloatField(default=0.6)
    tension_batterie = serializers.FloatField(default=24)
    capacite_batterie = serializers.FloatField(default=100)
    jours_autonomie = serializers.IntegerField(default=2)
    profondeur_decharge = serializers.FloatField(default=0.8)

    consommation_energie = serializers.FloatField(read_only=True)
    consommation_securisee = serializers.FloatField(read_only=True)
    puissance_crete = serializers.FloatField(read_only=True)
    tension_systeme = serializers.FloatField(read_only=True)
    nombre_panneaux = serializers.IntegerField(read_only=True)
    panneaux_serie = serializers.IntegerField(read_only=True)
    panneaux_parallele = serializers.IntegerField(read_only=True)
    capacite_stockage = serializers.FloatField(read_only=True)
    nombre_batteries = serializers.IntegerField(read_only=True)
    batteries_serie = serializers.IntegerField(read_only=True)
    batteries_parallele = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        appareils = validated_data.pop('appareils')
        Ir = validated_data.get('irradiation', 5.5)
        K = validated_data.get('facteur_rendement', 0.6)
        U_bat = validated_data.get('tension_batterie', 24)
        C_bat = validated_data.get('capacite_batterie', 100)
        n_j = validated_data.get('jours_autonomie', 2)
        d = validated_data.get('profondeur_decharge', 0.8)

        # 1. Calcul Ec
        Ec = sum(app['puissance_nominale_W'] * app['nombre'] * app['temps_utilisation_h'] for app in appareils)
        Ec_sec = Ec * 1.25

        # 2. Puissance crête Pc
        Pc = Ec_sec / (Ir * 1000 * K)

        # 3. Tension système
        if Pc <= 500:
            Us = 12
        elif Pc <= 2000:
            Us = 24
        elif Pc <= 10000:
            Us = 48
        else:
            Us = 96

        # 4. Nombre panneaux
        Pu = 150
        Np = int(-(-Pc // Pu))

        # 5. Série / parallèle panneaux
        Up = 12
        ns = round(Us / Up)
        np = int(-(-Np // ns))

        # 6. Capacité stockage
        Ct = (n_j * Ec_sec) / (Us * d)

        # 7. Batteries nombre total
        Nb = int(-(-Ct // C_bat))

        # 8. Batteries série/parallèle
        nbs = round(Us / U_bat)
        nbp = int(-(-Nb // nbs))

        return {
            'consommation_energie': Ec,
            'consommation_securisee': Ec_sec,
            'puissance_crete': Pc,
            'tension_systeme': Us,
            'nombre_panneaux': Np,
            'panneaux_serie': ns,
            'panneaux_parallele': np,
            'capacite_stockage': Ct,
            'nombre_batteries': Nb,
            'batteries_serie': nbs,
            'batteries_parallele': nbp,
        }
