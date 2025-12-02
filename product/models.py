from django.db import models
from user.models import ProfilMarchand
from django.utils import timezone
from datetime import datetime

# ==========================
# Catégorie de produits
# ==========================
class Categorie(models.Model):
    nom = models.CharField(max_length=150, unique=True, db_index=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='enfants'
    )

    def __str__(self):
        return f"{self.parent} > {self.nom}" if self.parent else self.nom


# ==========================
# Marque
# ==========================
class Marque(models.Model):
    nom = models.CharField(max_length=150, unique=True, db_index=True)

    def __str__(self):
        return self.nom


# ==========================
# Equipement / Produit
# ==========================
class Equipement(models.Model):
    MODE_CHOICES = (
        ('AC', 'Alternatif'),
        ('DC', 'Continu'),
        ('DC/AC', 'Hybride'),
    )

    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='equipements')
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipements')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type_equipement = models.CharField(max_length=150, blank=True)  # ex: monocristallin, Gel, MPPT

    # Caractéristiques électriques
    puissance_W = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_VA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_nominale_W = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_entree_DC_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_sortie_AC_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    frequence_Hz = models.PositiveIntegerField(null=True, blank=True)
    capacite_Ah = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energie_Wh = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Dimensions
    taille = models.CharField(max_length=100, blank=True)
    taille_mm = models.CharField(max_length=100, blank=True)
    poids_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Caractéristiques avancées
    efficacite_module_pourcent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    courant_puissance_max_Imp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    courant_court_circuit_ISC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_puissance_max_VMP = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_circuit_ouvert_VOC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_maximale_systeme_V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Cycle de vie
    cycle_vie_cycles = models.CharField(max_length=100, blank=True)
    ir_initiale_mOhm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Onduleur / stockage
    forme_onde = models.CharField(max_length=50, blank=True)
    rendement_pourcent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    courant_charge_A = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tension_systeme_V = models.CharField(max_length=50, blank=True)
    type_stockage = models.CharField(max_length=255, blank=True)

    # Panneau PV
    puissance_PV_max_12V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_PV_max_24V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    puissance_PV_max_48V = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Documents et données supplémentaires
    caracteristiques_additionnelles = models.JSONField(blank=True, null=True)
    description_technique = models.TextField(blank=True)

    # Mode
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, blank=True)

    # ==========================
    # Gestion marchant
    # ==========================
    marchant = models.ForeignKey(ProfilMarchand, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipements')
    prix_unitaire_fcfa = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantite_stock = models.PositiveIntegerField(default=0)
    est_disponible = models.BooleanField(default=True)

    #date_creation = models.DateTimeField(auto_now_add=True, default=timezone.now)
    #date_modification = models.DateTimeField(auto_now=True, default=timezone.now)

    def __str__(self):
        return f"{self.nom} ({self.marque.nom if self.marque else 'Sans marque'}) - {self.marchant.nom_boutique if self.marchant else 'Sans marchant'})"
