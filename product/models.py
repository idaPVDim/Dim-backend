from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=150, unique=True, db_index=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='enfants'
    )

    def __str__(self):
        return f"{self.parent} > {self.nom}" if self.parent else self.nom


class Marque(models.Model):
    nom = models.CharField(max_length=150, unique=True, db_index=True)

    def __str__(self):
        return self.nom


class Equipement(models.Model):
    MODE_CHOICES = (
        ('AC', 'Alternatif'),
        ('DC', 'Continu'),
        ('DC/AC', 'Hybride'),
    )

    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='equipements')
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipements')
    nom = models.CharField(max_length=255)
    type_equipement = models.CharField(max_length=150, blank=True)  # ex: monocristallin, Gel, MPPT
    description = models.TextField(blank=True)

    # Champs communs
    puissance_W = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_VA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_nominale_W = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # pour certaines données
    tension_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # tension générale
    tension_entree_DC_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_sortie_AC_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    frequence_Hz = models.PositiveIntegerField(null=True, blank=True)

    capacite_Ah = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energie_Wh = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    taille = models.CharField(max_length=100, blank=True)  # ex: taille_mm, volume, dimensions
    taille_mm = models.CharField(max_length=100, blank=True)

    efficacite_module_pourcent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    courant_puissance_max_Imp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    courant_court_circuit_ISC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    tension_puissance_max_VMP = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_circuit_ouvert_VOC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_maximale_systeme_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    tolerance_puissance_W = models.CharField(max_length=50, blank=True)
    temperature_module_fonctionnement_C = models.CharField(max_length=50, blank=True)
    calibre_max_fusibles_serie_A = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    cycle_vie_cycles = models.CharField(max_length=100, blank=True)  # ex: 500-800 cycles
    ir_initiale_mOhm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # résistance interne
    poids_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    forme_onde = models.CharField(max_length=50, blank=True)  # ex: Pur Sinus
    rendement_pourcent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    courant_charge_A = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tension_systeme_V = models.CharField(max_length=50, blank=True)  # ex: "12/24 (Auto-détection)"
    tension_max_PV_V = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    puissance_PV_max_12V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_PV_max_24V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_PV_max_48V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    caracteristiques_additionnelles = models.JSONField(blank=True, null=True)  # liste de caractéristiques

    conditions_test = models.CharField(max_length=255, blank=True)
    type_stockage = models.CharField(max_length=255, blank=True)

    description_technique = models.TextField(blank=True)  # Description technique longue


    mode = models.CharField(max_length=10, choices=MODE_CHOICES, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.marque.nom if self.marque else 'Sans marque'})"
