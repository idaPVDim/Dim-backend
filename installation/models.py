from django.db import models
from user.models import ProfilClient, ProfilTechnicien, Entreprise
from product.models import Equipement


# ==========================================================
# PROVINCE
# ==========================================================
class Province(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    irradiation = models.DecimalField(max_digits=4, decimal_places=1 ,default=0)  # kWh/m²/jour

    def __str__(self):
        return self.nom


# ==========================================================
# INSTALLATION
# ==========================================================
class Installation(models.Model):

    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('proposed', 'Proposition envoyée'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
        ('installed', 'Installée'),
        ('canceled', 'Annulée'),
    )

    SOURCE_CHOICES = (
        ('client', 'Fournies par le client'),
        ('technicien', 'Renseignement manuel par technicien'),
    )

    client = models.ForeignKey(
        ProfilClient,
        on_delete=models.CASCADE,
        related_name='installations'
    )

    technicien = models.ForeignKey(
        ProfilTechnicien,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='installations'
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name='installations'
    )

    source_donnees = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='client'
    )

    budget_client = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    surface_disponible_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contraintes_specifiques = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_mise_a_jour = models.DateTimeField(auto_now=True)

    # équipements proposés définitifs
    equipements_proposes = models.ManyToManyField(
        Equipement,
        through='InstallationEquipement'
    )

    def __str__(self):
        return f"Installation {self.id} – {self.client.user.username}"


# ==========================================================
# INSTALLATION → EQUIPEMENTS
# ==========================================================
class InstallationEquipement(models.Model):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    # origine : client ou technicien
    source = models.CharField(
        max_length=20,
        choices=(('client', 'Client'), ('technicien', 'Technicien')),
        default='client'
    )

    def __str__(self):
        return f"{self.quantite} × {self.equipement.nom} ({self.source})"


# ==========================================================
# SCHÉMA
# ==========================================================
class SchemaInstallation(models.Model):
    installation = models.OneToOneField(
        Installation,
        on_delete=models.CASCADE,
        related_name='schema'
    )
    fichier_schema = models.FileField(upload_to='schemas/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schéma Installation {self.installation.id}"


# ==========================================================
# DEVIS → lié à Installation + Entreprise du technicien
# ==========================================================
class Devis(models.Model):

    # chaque installation a un seul devis
    installation = models.OneToOneField(
        Installation,
        on_delete=models.CASCADE,
        related_name='devis'
    )

    # on récupère automatiquement l'entreprise via installation.technicien.entreprise
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.PROTECT,
        related_name='devis',
        default=None,
    )

    numero_devis = models.CharField(max_length=50, unique=True ,default='DEVIS-XXXX')

    cout_achat_equipements = models.DecimalField(max_digits=12, decimal_places=2)
    cout_installation_main_oeuvre = models.DecimalField(max_digits=12, decimal_places=2)
    cout_maintenance_estime_an = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    montant_total = models.DecimalField(max_digits=12, decimal_places=2)

    fichier_devis_pdf = models.FileField(upload_to='devis_pdfs/', null=True, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Devis {self.numero_devis} – Installation {self.installation.id}"


# ==========================================================
# COMPARAISON ÉCONOMIQUE
# ==========================================================
class ComparaisonEconomique(models.Model):
    devis = models.OneToOneField(
        Devis,
        on_delete=models.CASCADE,
        related_name='comparaison'
    )

    cout_electricite_traditionnelle_estime_an = models.DecimalField(max_digits=12, decimal_places=2)
    economies_potentielles_annuelles = models.DecimalField(max_digits=12, decimal_places=2)
    duree_retour_investissement_annees = models.PositiveIntegerField()

    def __str__(self):
        return f"Comparaison – Devis {self.devis.numero_devis}"
