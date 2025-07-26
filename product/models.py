from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='enfants',
        null=True,
        blank=True,
        help_text="Catégorie parente (vide si catégorie racine)"
    )

    class Meta:
        verbose_name_plural = 'Catégories'
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.nom}"
        return self.nom


class Marque(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Equipement(models.Model):
    MODE_CHOICES = (
        ('AC', 'Alternatif (AC)'),
        ('DC', 'Continu (DC)'),
        ('DC/AC', 'Continu / Alternatif (Hybride)'),
    )

    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='equipements')
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipements')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Champs standard (électroménagers et solaires)
    puissance_W = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Puissance nominale en Watts"
    )
    tension_V = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Tension nominale en Volts"
    )
    frequence_Hz = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Fréquence en Hz (pour AC uniquement)"
    )

    # Champs spécifiques à certains types (batteries, onduleurs...)
    capacite_Ah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Capacité en Ampère-heures (batteries)"
    )
    taille = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Taille, volume ou puissance (ex: 180L, 1.5CV, 32 pouces)"
    )
    type_equipement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Type précis (ex: Gel, MPPT, Hybride)"
    )

    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        help_text="Mode d'alimentation"
    )

    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        ordering = ['categorie', 'nom']

    def __str__(self):
        marque = f" ({self.marque})" if self.marque else ""
        return f"{self.nom}{marque}"
