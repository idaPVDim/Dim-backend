from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import User, ProfilClient, ProfilTechnicien


# --- Inline Admin profils ---

class ProfilClientInline(admin.StackedInline):
    model = ProfilClient
    can_delete = False
    verbose_name = "Profil Client"
    verbose_name_plural = "Profil Client"
    fk_name = 'user'
    extra = 0
    readonly_fields = []

    fieldsets = (
        (None, {
            'fields': ('address', 'consommation_annuelle_moyenne_kwh'),
        }),
    )


class ProfilTechnicienInline(admin.StackedInline):
    model = ProfilTechnicien
    can_delete = False
    verbose_name = "Profil Technicien"
    verbose_name_plural = "Profil Technicien"
    fk_name = 'user'
    extra = 0
    readonly_fields = ['preview_id_document', 'preview_formation_document',
                       'preview_certification_docs', 'preview_autorisation_docs', 'preview_autres_docs']

    fieldsets = (
        (None, {
            'fields': (
                'certifications',
                'zone_couverture',
                'is_certified',
            ),
        }),
        ('Documents', {
            'fields': (
                'id_document',
                'preview_id_document',
                'formation_document',
                'preview_formation_document',
                'certification_docs',
                'preview_certification_docs',
                'autorisation_docs',
                'preview_autorisation_docs',
                'autres_docs',
                'preview_autres_docs',
            ),
            'description': 'Téléchargez les documents liés au technicien.',
        }),
    )

    # Méthodes pour afficher un lien ou aperçu des fichiers uploadés
    def _link_to_file(self, file_field):
        if file_field:
            url = file_field.url
            filename = file_field.name.split('/')[-1]
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, filename)
        return "(Aucun fichier)"

    def preview_id_document(self, obj):
        return self._link_to_file(obj.id_document)
    preview_id_document.short_description = "Document d'identité"

    def preview_formation_document(self, obj):
        return self._link_to_file(obj.formation_document)
    preview_formation_document.short_description = "Document de formation"

    def preview_certification_docs(self, obj):
        return self._link_to_file(obj.certification_docs)
    preview_certification_docs.short_description = "Documents de certification"

    def preview_autorisation_docs(self, obj):
        return self._link_to_file(obj.autorisation_docs)
    preview_autorisation_docs.short_description = "Documents d'autorisation"

    def preview_autres_docs(self, obj):
        return self._link_to_file(obj.autres_docs)
    preview_autres_docs.short_description = "Autres documents"


# --- UserAdmin personnalisé ---

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfilClientInline, ProfilTechnicienInline]

    ordering = ['email']
    list_display = ('email', 'full_name', 'role', 'phone_number', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    readonly_fields = ('date_joined', 'last_login')

    # Champs à afficher dans le formulaire création utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone_number', 'password1', 'password2'),
        }),
    )

    # Champs à afficher dans le formulaire modification utilisateur
    fieldsets = (
        (None, {'fields': ('email', 'password')}),

        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'phone_number', 'role')}),

        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),

        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    full_name.short_description = 'Nom complet'
    full_name.admin_order_field = 'last_name'

    # Permet d'afficher un lien rapide vers la page détail du profil client / technicien
    def get_inline_instances(self, request, obj=None):
        # Montrer l'inline adapté selon le rôle de l'utilisateur
        inlines = []
        if obj:
            if obj.role == 'client':
                inlines.append(ProfilClientInline(self.model, self.admin_site))
            elif obj.role == 'technicien':
                inlines.append(ProfilTechnicienInline(self.model, self.admin_site))
        return inlines


# --- Admin pour les profils pour pouvoir modifier séparément si besoin ---

@admin.register(ProfilClient)
class ProfilClientAdmin(admin.ModelAdmin):
    list_display = ( 'address', 'consommation_annuelle_moyenne_kwh')
    search_fields = ('user__email', 'address')
    readonly_fields = ['user']

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email utilisateur'
    user_email.admin_order_field = 'user__email'


@admin.register(ProfilTechnicien)
class ProfilTechnicienAdmin(admin.ModelAdmin):
    list_display = ( 'zone_couverture', 'is_certified')
    search_fields = ( 'zone_couverture', 'certifications')
    list_filter = ('is_certified',)
    readonly_fields = ['user', 'preview_id_document', 'preview_formation_document',
                      'preview_certification_docs', 'preview_autorisation_docs', 'preview_autres_docs']

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'certifications',
                'zone_couverture',
                'is_certified',
            ),
        }),
        ('Documents', {
            'fields': (
                'id_document', 'preview_id_document',
                'formation_document', 'preview_formation_document',
                'certification_docs', 'preview_certification_docs',
                'autorisation_docs', 'preview_autorisation_docs',
                'autres_docs', 'preview_autres_docs',
            )
        }),
    )

    def _link_to_file(self, file_field):
        if file_field:
            url = file_field.url
            filename = file_field.name.split('/')[-1]
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, filename)
        return "(Aucun fichier)"

    def preview_id_document(self, obj):
        return self._link_to_file(obj.id_document)
    preview_id_document.short_description = "Document d'identité"

    def preview_formation_document(self, obj):
        return self._link_to_file(obj.formation_document)
    preview_formation_document.short_description = "Document de formation"

    def preview_certification_docs(self, obj):
        return self._link_to_file(obj.certification_docs)
    preview_certification_docs.short_description = "Documents de certification"

    def preview_autorisation_docs(self, obj):
        return self._link_to_file(obj.autorisation_docs)
    preview_autorisation_docs.short_description = "Documents d'autorisation"

    def preview_autres_docs(self, obj):
        return self._link_to_file(obj.autres_docs)
    preview_autres_docs.short_description = "Autres documents"
