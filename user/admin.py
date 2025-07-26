from django.contrib import admin
from django.utils.translation import gettext_lazy as _
# IMPORTANT : Adaptez ces imports selon votre installation django-unfold (underscore dans le nom)
from unfold.admin import ModelAdmin, StackedInline, TabularInline
# Si vous n'avez pas django-unfold, utilisez :
# from django.contrib.admin import ModelAdmin, StackedInline, TabularInline

from user.models import User, ProfilClient, ProfilTechnicien
from installation.models import Installation, InstallationEquipement, SchemaInstallation, Devis, ComparaisonEconomique
from product.models import Categorie, Marque, Equipement
from maintenance.models import Incident, Maintenance, QuestionMaintenance, ReponseMaintenance

# ======== USER + PROFILS ========

class ProfilClientInline(StackedInline):
    model = ProfilClient
    fk_name = 'user'
    extra = 0
    fieldsets = (
        (_('Profil Client'), {
            'fields': ('address', 'consommation_annuelle_moyenne_kwh'),
            'classes': ('collapse',),
        }),
    )
    unfolding_fields = ('address', 'consommation_annuelle_moyenne_kwh')


class ProfilTechnicienInline(StackedInline):
    model = ProfilTechnicien
    fk_name = 'user'
    extra = 0
    fieldsets = (
        (_('Profil Technicien'), {
            'fields': (
                'certifications', 'zone_couverture', 'is_certified',
                'id_document', 'formation_document', 'certification_docs',
                'autorisation_docs', 'autres_docs',
            ),
            'classes': ('collapse',),
        }),
    )
    unfolding_fields = ('is_certified',)


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (_('Informations utilisateur'), {
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone_number', 'password'),
        }),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined'),
        }),
    )
    unfolding_fields = ('first_name', 'last_name', 'phone_number', 'role')

    inlines = [ProfilClientInline, ProfilTechnicienInline]

    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} utilisateur(s) activé(s).")
    activate_users.short_description = "Activer les utilisateurs sélectionnés"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} utilisateur(s) désactivé(s).")
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"


# ======== PRODUCT ========

class SousCategorieInline(TabularInline):
    model = Categorie
    fk_name = 'parent'
    extra = 0
    fields = ('nom', 'parent')
    show_change_link = True


@admin.register(Categorie)
class CategorieAdmin(ModelAdmin):
    list_display = ('nom', 'parent')
    search_fields = ('nom',)
    list_filter = ('parent',)
    ordering = ('nom',)
    inlines = [SousCategorieInline]
    fieldsets = (
        (None, {
            'fields': ('nom', 'parent'),
        }),
    )
    unfolding_fields = ('parent',)

@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
    ordering = ('nom',)


@admin.register(Equipement)
class EquipementAdmin(ModelAdmin):
    list_display = ('nom', 'categorie', 'marque', 'mode', 'puissance_W', 'tension_V')
    list_filter = ('categorie', 'marque', 'mode')
    search_fields = ('nom', 'categorie__nom', 'marque__nom')
    ordering = ('categorie', 'nom')

    fieldsets = (
        (_('Informations générales'), {
            'fields': ('nom', 'categorie', 'marque', 'description'),
        }),
        (_('Caractéristiques techniques'), {
            'classes': ('collapse',),
            'fields': (
                'puissance_W', 'tension_V', 'frequence_Hz',
                'capacite_Ah', 'taille', 'type_equipement',
                'mode',
            ),
        }),
    )
    unfolding_fields = ('categorie', 'marque', 'mode')


# ======== INSTALLATION ========

class InstallationEquipementInline(TabularInline):
    model = InstallationEquipement
    extra = 0
    autocomplete_fields = ['equipement']
    fields = ('equipement', 'quantite')


class SchemaInstallationInline(StackedInline):
    model = SchemaInstallation
    extra = 0
    readonly_fields = ('date_creation',)
    fieldsets = (
        (None, {
            'fields': ('fichier_schema', 'description', 'date_creation'),
            'classes': ('collapse',),
        }),
    )


class DevisInline(StackedInline):
    model = Devis
    extra = 0
    readonly_fields = ('date_creation',)
    fieldsets = (
        (None, {
            'fields': ('cout_achat_equipements', 'cout_installation_main_oeuvre',
                       'cout_maintenance_estime_an', 'montant_total', 'fichier_devis_pdf', 'date_creation'),
            'classes': ('collapse',),
        }),
    )


class ComparaisonEconomiqueInline(StackedInline):
    model = ComparaisonEconomique
    extra = 0
    fieldsets = (
        (None, {
            'fields': ('cout_electricite_traditionnelle_estime_an', 'economies_potentielles_annuelles', 'duree_retour_investissement_annees'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Installation)
class InstallationAdmin(ModelAdmin):
    list_display = ('id', 'client', 'technicien', 'status', 'date_creation', 'date_derniere_mise_a_jour')
    list_filter = ('status', 'province')
    search_fields = ('client__user__email', 'client__user__first_name', 'technicien__user__email', 'province')
    ordering = ('-date_creation',)

    fieldsets = (
        (_('Infos générales'), {
            'fields': ('client', 'technicien', 'consommation_energetique', 'province', 'budget_client',
                       'surface_disponible_m2', 'contraintes_specifiques', 'status'),
        }),
    )
    inlines = [InstallationEquipementInline, SchemaInstallationInline, DevisInline]


# ======== INCIDENTS ET MAINTENANCE ========

class MaintenanceInline(StackedInline):
    model = Maintenance
    extra = 0
    fk_name = 'incident'
    readonly_fields = ('date_intervention_reelle',)
    fieldsets = (
        (_('Détails Maintenance'), {
            'fields': ('technicien', 'solution_proposee', 'cout_estime', 'temps_estime_heure',
                       'date_intervention_prevue', 'date_intervention_reelle', 'rapport_intervention_pdf'),
            'classes': ('collapse',),
        }),
    )


class ReponseMaintenanceInline(TabularInline):
    model = ReponseMaintenance
    extra = 0
    fields = ('question', 'reponse', 'date_reponse', 'repondu_par_client', 'repondu_par_technicien')
    readonly_fields = ('date_reponse',)
    show_change_link = True


@admin.register(Incident)
class IncidentAdmin(ModelAdmin):
    list_display = ('id', 'installation', 'client', 'status', 'date_signalisation')
    list_filter = ('status',)
    search_fields = ('installation__id', 'client__user__email', 'description')
    ordering = ('-date_signalisation',)

    fieldsets = (
        (_('Informations Incident'), {
            'fields': ('installation', 'client', 'description', 'status'),
        }),
    )
    inlines = [MaintenanceInline, ReponseMaintenanceInline]


@admin.register(Maintenance)
class MaintenanceAdmin(ModelAdmin):
    list_display = ('id', 'incident', 'technicien', 'date_intervention_prevue', 'date_intervention_reelle')
    list_filter = ('technicien',)
    search_fields = ('incident__id', 'technicien__user__email')
    ordering = ('-date_intervention_prevue',)


@admin.register(QuestionMaintenance)
class QuestionMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('texte_question', 'type_question')
    list_filter = ('type_question',)
    search_fields = ('texte_question',)


@admin.register(ReponseMaintenance)
class ReponseMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('incident', 'question', 'date_reponse', 'repondu_par_client', 'repondu_par_technicien')
    readonly_fields = ('date_reponse',)
    list_filter = ('repondu_par_client', 'repondu_par_technicien')
    search_fields = ('incident__id', 'question__texte_question')


# Si besoin, vous pouvez aussi créer des actions personnalisées pour vos modèles,
# des filtres additionnels, des champs en readonly conditionnels, etc.

