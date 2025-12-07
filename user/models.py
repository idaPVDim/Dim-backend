from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Avg

# ==========================
# Gestion des utilisateurs
# ==========================

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse e-mail doit être renseignée'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if not password:
            raise ValueError(_('Le mot de passe doit être renseigné'))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superuser doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superuser doit avoir is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    ROLE_CHOICES = (
        ('client', 'Client'),
        ('technicien', 'Technicien'),
        ('marchant', 'Marchant'),
        ('admin', 'Administrateur'),
    )

    first_name = models.CharField(_('prénom'), max_length=150, blank=True)
    last_name = models.CharField(_('nom'), max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


# ==========================
# Entreprise
# ==========================

class Entreprise(models.Model):
    nom = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nom


# ==========================
# Profil Client
# ==========================

class ProfilClient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_client')
    address = models.CharField(max_length=255, blank=True, null=True)
    consommation_annuelle_moyenne_kwh = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ratings
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    nombre_avis = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profil Client: {self.user.email}"


# ==========================
# Profil Technicien
# ==========================

class ProfilTechnicien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_technicien')
    certifications = models.TextField(blank=True, null=True)
    zone_couverture = models.CharField(max_length=255, blank=True, null=True)
    is_certified = models.BooleanField(default=False)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        null=True, blank=True,
        default=None,
    )

    # Documents
    id_document = models.FileField(upload_to='technician_docs/ids/', blank=True, null=True)
    formation_document = models.FileField(upload_to='technician_docs/formations/', blank=True, null=True)
    certification_docs = models.FileField(upload_to='technician_docs/certs/', blank=True, null=True)
    autorisation_docs = models.FileField(upload_to='technician_docs/autorisations/', blank=True, null=True)
    autres_docs = models.FileField(upload_to='technician_docs/autres/', blank=True, null=True)

    # rating
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    nombre_avis = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profil Technicien: {self.user.email}"


# ==========================
# Profil Marchand
# ==========================

class ProfilMarchand(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_marchand')
    nom_boutique = models.CharField(max_length=255)
    adresse_boutique = models.CharField(max_length=255, blank=True, null=True)
    description_boutique = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)

    # rating
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    nombre_avis = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profil Marchand: {self.nom_boutique} ({self.user.email})"


# ==========================
# Ratings (PlayStore-style)
# ==========================

class Rating(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # notes de 1 à 5

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_donnes"
    )

    # Cibles possibles
    technicien = models.ForeignKey(
        ProfilTechnicien,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="ratings_recus"
    )

    marchand = models.ForeignKey(
        ProfilMarchand,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="ratings_recus"
    )

    client = models.ForeignKey(
        ProfilClient,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="ratings_recus"
    )

    note = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Rating {self.note} par {self.auteur.email}"



# ==========================
# Recommandations clients
# ==========================

class Recommandation(models.Model):
    client_origine = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='recommandations_envoyees')
    client_recommande = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='recommandations_recues')
    date_creation = models.DateTimeField(auto_now_add=True)
    points_attribues = models.PositiveIntegerField(default=0)

    
    est_valide = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_origine.user.email} recommande {self.client_recommande.user.email}"


# ==========================
# Garanties
# ==========================

class Garantie(models.Model):
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='garanties')
    technicien = models.ForeignKey(ProfilTechnicien, on_delete=models.SET_NULL, null=True, blank=True, related_name='garanties')
    installation_id = models.PositiveIntegerField()  # liaison avec Installation
    description = models.TextField(blank=True, null=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    est_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Garantie Installation {self.installation_id} - Client {self.client.user.email}"

