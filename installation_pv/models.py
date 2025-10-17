from django.db import models
from installation.models import Installation


class DimensionnementPV(models.Model):
    installation = models.OneToOneField(Installation, on_delete=models.CASCADE, related_name='dimensionnement')

    # Données d'entrée (JSON): liste appareils + paramètres environnementaux
    donnees_appareils = models.JSONField()
    irradiation = models.DecimalField(max_digits=4, decimal_places=2, default=5.5)
    facteur_rendement = models.DecimalField(max_digits=3, decimal_places=2, default=0.6)
    tension_batterie = models.DecimalField(max_digits=4, decimal_places=2, default=24.0)
    capacite_batterie = models.DecimalField(max_digits=6, decimal_places=2, default=100.0)
    jours_autonomie = models.PositiveIntegerField(default=2)
    profondeur_decharge = models.DecimalField(max_digits=3, decimal_places=2, default=0.8)

    # Résultats calculs stockés en JSON
    resultat_calculs = models.JSONField(blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dimensionnement PV pour Installation {self.installation.id}"

    class Meta:
        verbose_name = "Dimensionnement photovoltaïque"
        verbose_name_plural = "Dimensionnements photovoltaïques"
