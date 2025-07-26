from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

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
        extra_fields.setdefault('is_active', True)  # facultatif mais conseillé

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superuser doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superuser doit avoir is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Supprime le champ username
    email = models.EmailField(_('email address'), unique=True)

    ROLE_CHOICES = (
        ('client', 'Client'),
        ('technicien', 'Technicien'),
        ('admin', 'Administrateur'),
    )
    first_name = models.CharField(_('prénom'), max_length=150, blank=True)
    last_name = models.CharField(_('nom'), max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'      # Définit le champ email comme identifiant principal
    REQUIRED_FIELDS = []          # Plus besoin de username ou autre champ obligatoire

    objects = UserManager()       # Manager personnalisé adapté

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['email']


class ProfilClient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_client')
    address = models.CharField(max_length=255, blank=True, null=True)
    consommation_annuelle_moyenne_kwh = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Profil Client: {self.user.email}"


class ProfilTechnicien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_technicien')
    certifications = models.TextField(blank=True, null=True)
    zone_couverture = models.CharField(max_length=255, blank=True, null=True)
    is_certified = models.BooleanField(default=False)
    id_document = models.FileField(upload_to='technician_docs/ids/', blank=True, null=True)
    formation_document = models.FileField(upload_to='technician_docs/formations/', blank=True, null=True)
    certification_docs = models.FileField(upload_to='technician_docs/certs/', blank=True, null=True)
    autorisation_docs = models.FileField(upload_to='technician_docs/autorisations/', blank=True, null=True)
    autres_docs = models.FileField(upload_to='technician_docs/autres/', blank=True, null=True)

    def __str__(self):
        return f"Profil Technicien: {self.user.email}"
