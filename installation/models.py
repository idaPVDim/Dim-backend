from django.db import models
from user.models import ProfilClient, ProfilTechnicien
from product.models import Equipement

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
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='installations')
    technicien = models.ForeignKey(ProfilTechnicien, on_delete=models.SET_NULL, null=True, blank=True, related_name='installations')
    consommation_energetique = models.DecimalField(max_digits=12, decimal_places=2)
    province = models.CharField(max_length=100)
    budget_client = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    surface_disponible_m2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    contraintes_specifiques = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    equipements_proposes = models.ManyToManyField(Equipement, through='InstallationEquipement')

    def __str__(self):
        return f"Installation {self.id} pour {self.client.user.username} ({self.get_status_display()})"

class InstallationEquipement(models.Model):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.equipement.nom} (Installation {self.installation.id})"

class SchemaInstallation(models.Model):
    installation = models.OneToOneField(Installation, on_delete=models.CASCADE, related_name='schema')
    fichier_schema = models.FileField(upload_to='schemas/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schéma Installation {self.installation.id}"

class Devis(models.Model):
    installation = models.OneToOneField(Installation, on_delete=models.CASCADE, related_name='devis')
    cout_achat_equipements = models.DecimalField(max_digits=12, decimal_places=2)
    cout_installation_main_oeuvre = models.DecimalField(max_digits=12, decimal_places=2)
    cout_maintenance_estime_an = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    fichier_devis_pdf = models.FileField(upload_to='devis_pdfs/', blank=True, null=True)

    def __str__(self):
        return f"Devis Installation {self.installation.id} - Total {self.montant_total}"

class ComparaisonEconomique(models.Model):
    devis = models.OneToOneField(Devis, on_delete=models.CASCADE, related_name='comparaison')
    cout_electricite_traditionnelle_estime_an = models.DecimalField(max_digits=12, decimal_places=2)
    economies_potentielles_annuelles = models.DecimalField(max_digits=12, decimal_places=2)
    duree_retour_investissement_annees = models.PositiveIntegerField()

    def __str__(self):
        return f"Comparaison Economique Devis {self.devis.id}"
