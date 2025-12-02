from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

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
        if password:
            user.set_password(password)
        else:
            raise ValueError(_('Le mot de passe doit être renseigné'))
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

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['email']

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

    # Fidélité et recommandations
    points_fidelite = models.PositiveIntegerField(default=0)
    nombre_recommandations = models.PositiveIntegerField(default=0)

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
        null=True,
        blank=True,
        default=None,
    )


    # Documents
    id_document = models.FileField(upload_to='technician_docs/ids/', blank=True, null=True)
    formation_document = models.FileField(upload_to='technician_docs/formations/', blank=True, null=True)
    certification_docs = models.FileField(upload_to='technician_docs/certs/', blank=True, null=True)
    autorisation_docs = models.FileField(upload_to='technician_docs/autorisations/', blank=True, null=True)
    autres_docs = models.FileField(upload_to='technician_docs/autres/', blank=True, null=True)

    # Statistiques et notes
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    nombre_avis = models.PositiveIntegerField(default=0)
    installations_realisees = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profil Technicien: {self.user.email}"


# ==========================
# Profil Marchant
# ==========================

class ProfilMarchand(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_marchand')
    nom_boutique = models.CharField(max_length=255)
    adresse_boutique = models.CharField(max_length=255, blank=True, null=True)
    description_boutique = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)

    # Statistiques et promotions
    nombre_produits = models.PositiveIntegerField(default=0)
    ventes_totales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    points_fidelite_clients = models.PositiveIntegerField(default=0)  # fidélité liée aux clients acheteurs

    def __str__(self):
        return f"Profil Marchant: {self.nom_boutique} ({self.user.email})"


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


# user/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    """
    Conversation entre deux utilisateurs (private chat).
    Unique per pair (order-independent).
    """
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="conversations_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="conversations_user2", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user1', 'user2'),)

    def __str__(self):
        return f"Conversation {self.id} - {self.user1.email} <-> {self.user2.email}"

    @classmethod
    def get_or_create_between(cls, a, b):
        # ensure consistent ordering to match unique_together
        if a.id < b.id:
            u1, u2 = a, b
        else:
            u1, u2 = b, a
        obj, created = cls.objects.get_or_create(user1=u1, user2=u2)
        return obj, created


class Message(models.Model):
    MESSAGE_TYPES = (("text", "text"), ("image", "image"), ("file", "file"), ("system", "system"))
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default="text")
    file = models.FileField(upload_to="messages/files/", null=True, blank=True)
    image = models.ImageField(upload_to="messages/images/", null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Msg {self.id} in conv {self.conversation.id} by {self.sender.email}"
