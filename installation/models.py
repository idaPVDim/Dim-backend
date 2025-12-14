from django.db import models
from user.models import ProfilClient, ProfilTechnicien, Entreprise
from product.models import Equipement
from django.conf import settings

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


class Devis(models.Model):

    TYPES = (
        ("DEMANDE_TECHNICIEN_A_VENDEUR", "Demande du technicien au vendeur"),
        ("REPONSE_VENDEUR_A_TECHNICIEN", "Réponse du vendeur au technicien"),
        ("DEVIS_FINAL_AU_CLIENT", "Devis final envoyé au client"),
    )

    STATUTS = (
        ("EN_ATTENTE", "En attente"),
        ("ENVOYE", "Envoyé"),
        ("ACCEPTE", "Accepté"),
        ("REFUSE", "Refusé"),
        ("TERMINE", "Terminé"),
    )

    type_devis = models.CharField(max_length=40, choices=TYPES , default="DEMANDE_TECHNICIEN_A_VENDEUR")
    statut = models.CharField(max_length=20, choices=STATUTS, default="EN_ATTENTE")

    # Qui crée le devis ?
    emetteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="devis_emis",
        null=True, blank=True
    )

    # Qui reçoit ?
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devis_recus",
        null=True, blank=True
    )

    titre_projet = models.CharField(max_length=200, default="Projet d'installation photovoltaïque")

    # Informations client (pour le devis final)
    nom_client = models.CharField(max_length=200, blank=True, null=True)
    telephone_client = models.CharField(max_length=30, blank=True, null=True)
    localisation_client = models.CharField(max_length=255, blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def est_devis_final(self):
        return self.type_devis == "DEVIS_FINAL_AU_CLIENT"

    def __str__(self):
        return f"Devis #{self.id} - {self.titre_projet}"

class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name="lignes")
    equipement = models.ForeignKey(Equipement, on_delete=models.SET_NULL, null=True)

    quantite = models.PositiveIntegerField(default=1)

    # Prix renseigné uniquement par le vendeur
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    prix_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    disponibilite = models.CharField(max_length=100, blank=True, null=True)  # ex : Disponible / Rupture
    garantie_mois = models.PositiveIntegerField(null=True, blank=True)

    commentaires = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.equipement} x {self.quantite}"

class ServiceDevisFinal(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name="services")
    
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.nom


class ConditionsDevis(models.Model):
    devis = models.OneToOneField(Devis, on_delete=models.CASCADE, related_name="conditions")

    validite_jours = models.PositiveIntegerField(default=7)
    garantie_installation_mois = models.PositiveIntegerField(default=3)
    modalites_paiement = models.TextField(default="50% avant installation, 50% après mise en service")

    def __str__(self):
        return f"Conditions du devis #{self.devis.id}"

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
