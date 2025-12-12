# market/models.py
from django.db import models
from django.conf import settings
from installation.models import Installation
from product.models import Equipement
from user.models import ProfilTechnicien, ProfilMarchand, Entreprise, ProfilClient
from django.utils import timezone
import uuid

def generate_request_ref():
    return f"REQ-{uuid.uuid4().hex[:8].upper()}"

class TechnicalRequest(models.Model):
    """
    Demande technique (liste d'items) créée par un technicien (ou dérivée d'une installation).
    Envoyée ensuite aux marchands pour obtenir des offres.
    """
    reference = models.CharField(max_length=64, unique=True, default=generate_request_ref)
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE, related_name="technical_requests", null=True, blank=True)
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="technical_requests_created")
    technicien = models.ForeignKey(ProfilTechnicien, on_delete=models.SET_NULL, null=True, blank=True, related_name="technical_requests")
    titre = models.CharField(max_length=255, default="Demande matériel")
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)  # quand la requête a été envoyée aux marchands
    statut = models.CharField(max_length=30, default="draft", choices=(
        ("draft", "Brouillon"),
        ("sent", "Envoyée"),
        ("closed", "Fermée"),
    ))

    # si on veut cibler des marchands spécifiques, on stocke ici (ManyToMany)
    destinataires = models.ManyToManyField(ProfilMarchand, blank=True, related_name="requests_received")

    def __str__(self):
        return f"{self.reference} - {self.titre}"

class TechnicalRequestItem(models.Model):
    request = models.ForeignKey(TechnicalRequest, on_delete=models.CASCADE, related_name="items")
    equipement = models.ForeignKey(Equipement, on_delete=models.SET_NULL, null=True, blank=True)
    nom_libre = models.CharField(max_length=255, blank=True, null=True)  # si non lié à un produit précis
    quantite = models.PositiveIntegerField(default=1)
    caracteristiques = models.JSONField(blank=True, null=True)  # ex: {"vc":"100Wc","tension":"12V"}
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantite} x {self.equipement or self.nom_libre}"

class VendorQuote(models.Model):
    """
    Réponse du marchand à une TechnicalRequest (ou TargetedRequest)
    """
    reference = models.CharField(max_length=64, unique=True, default=lambda: f"VQ-{uuid.uuid4().hex[:8].upper()}")
    technical_request = models.ForeignKey(TechnicalRequest, on_delete=models.CASCADE, related_name="vendor_quotes")
    marchant = models.ForeignKey(ProfilMarchand, on_delete=models.CASCADE, related_name="vendor_quotes")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.SET_NULL, null=True, blank=True, related_name="vendor_quotes")
    date_reponse = models.DateTimeField(auto_now_add=True)
    validite_jours = models.PositiveIntegerField(default=7)
    delai_livraison_jours = models.PositiveIntegerField(default=7)
    commentaire = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=30, default="pending", choices=(
        ("pending", "En attente"),
        ("sent", "Envoyée"),
        ("accepted", "Acceptée"),
        ("rejected", "Rejetée"),
    ))

    def total_materiel(self):
        return sum([i.total() for i in self.items.all()])

    def __str__(self):
        return f"VendorQuote {self.reference} by {self.marchant.nom_boutique}"

class VendorQuoteItem(models.Model):
    quote = models.ForeignKey(VendorQuote, on_delete=models.CASCADE, related_name="items")
    technical_item = models.ForeignKey(TechnicalRequestItem, on_delete=models.SET_NULL, null=True, blank=True)
    equipement = models.ForeignKey(Equipement, on_delete=models.SET_NULL, null=True, blank=True)
    nom_libre = models.CharField(max_length=255, blank=True, null=True)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire_fcfa = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    prix_total_fcfa = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    disponibilite = models.CharField(max_length=100, blank=True, null=True)
    garantie_mois = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.prix_unitaire_fcfa is not None:
            self.prix_total_fcfa = self.prix_unitaire_fcfa * self.quantite
        super().save(*args, **kwargs)

    def total(self):
        return self.prix_total_fcfa or 0

    def __str__(self):
        return f"{self.quantite} x {self.equipement or self.nom_libre} @ {self.prix_unitaire_fcfa}"

class SelectedVendorQuote(models.Model):
    """
    Quand le technicien sélectionne une proposition d'un marchand pour la convertir en Devis client.
    """
    technical_request = models.OneToOneField(TechnicalRequest, on_delete=models.CASCADE, related_name="selected_quote", null=True, blank=True)
    vendor_quote = models.ForeignKey(VendorQuote, on_delete=models.CASCADE, related_name="+")
    date_selected = models.DateTimeField(auto_now_add=True)
    selected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Selected {self.vendor_quote.reference} for {self.technical_request.reference}"
