from django.db import models
from installation.models import Installation
from product.models import Equipement

class EquipementDimensionnement(models.Model):
    """
    Equipement utilisé pour le dimensionnement, lié à une installation,
    avec traçabilité de la source (client ou technicien).
    """
    SOURCE_CHOICES = (
        ('client', 'Client'),
        ('technicien', 'Technicien'),
    )

    installation = models.ForeignKey(Installation, on_delete=models.CASCADE, related_name='equipements_dimensionnement')
    equipement = models.ForeignKey(Equipement, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    temps_utilisation_h = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temps d'utilisation par jour en heures")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='client')

    def consommation_journaliere(self):
        return self.equipement.puissance_nominale_W * self.quantite * float(self.temps_utilisation_h)

    def __str__(self):
        return f"{self.quantite} x {self.equipement.nom} ({self.source}) - Installation {self.installation.id}"

class DimensionnementPV(models.Model):
    installation = models.OneToOneField(Installation, on_delete=models.CASCADE, related_name='dimensionnement_pv')

    facteur_rendement = models.DecimalField(max_digits=4, decimal_places=2, default=0.6)

    puissance_unitaire_panneau_w = models.PositiveIntegerField(default=150)
    tension_unitaire_panneau_v = models.PositiveIntegerField(default=12)
    surface_disponible_m2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    budget_estime = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    avec_stockage = models.BooleanField(default=True)

    capacite_unitaire_batterie_ah = models.PositiveIntegerField(null=True, blank=True)
    tension_unitaire_batterie_v = models.PositiveIntegerField(null=True, blank=True)
    autonomie_jours = models.PositiveIntegerField(null=True, blank=True)
    profondeur_decharge = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    puissance_crete_wc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_champ_v = models.PositiveIntegerField(null=True, blank=True)
    nombre_total_panneaux = models.PositiveIntegerField(null=True, blank=True)
    nombre_panneaux_serie = models.PositiveIntegerField(null=True, blank=True)
    nombre_panneaux_parallele = models.PositiveIntegerField(null=True, blank=True)

    capacite_batterie_ah = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nombre_total_batteries = models.PositiveIntegerField(null=True, blank=True)
    nombre_batteries_serie = models.PositiveIntegerField(null=True, blank=True)
    nombre_batteries_parallele = models.PositiveIntegerField(null=True, blank=True)

    puissance_onduleur_w = models.PositiveIntegerField(null=True, blank=True)
    tension_onduleur_v = models.PositiveIntegerField(null=True, blank=True)

    tension_regulateur_v = models.PositiveIntegerField(null=True, blank=True)
    courant_regulateur_a = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    longueur_cable_m = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    section_cable_mm2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def consommation_totale_journaliere(self):
        return sum(equip.consommation_journaliere() for equip in self.installation.equipements_dimensionnement.all())

    def __str__(self):
        return f"Dimensionnement PV Installation #{self.installation.id}"

class DevisProduit(models.Model):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE, related_name='devis_produits')
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire_fcfa = models.DecimalField(max_digits=12, decimal_places=2)
    prix_total_fcfa = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.prix_total_fcfa = self.prix_unitaire_fcfa * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite} x {self.equipement.nom} ({self.prix_total_fcfa} F CFA)"
