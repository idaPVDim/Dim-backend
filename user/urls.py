from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    MeAPIView,
    MyEntrepriseAPIView,
    UserViewSet,
    ProfilClientViewSet,
    ProfilTechnicienViewSet,
    ProfilMarchandViewSet,
    EntrepriseViewSet,
    RatingViewSet,  # ⭐ Nouveau pour la gestion des avis
)

router = DefaultRouter()

# USERS CRUD & actions
router.register(r'users', UserViewSet, basename='user')

# Profils spéciaux (admin only)
router.register(r'profil-clients',       ProfilClientViewSet, basename='profil-client')
router.register(r'profil-techniciens',   ProfilTechnicienViewSet, basename='profil-technicien')
router.register(r'profil-marchands',     ProfilMarchandViewSet, basename='profil-marchand')

# Entreprises (admin)
router.register(r'entreprises', EntrepriseViewSet, basename='entreprise')

# Ratings (utilisateurs peuvent noter marchands / techniciens)
router.register(r'ratings', RatingViewSet, basename='rating')


urlpatterns = [
    # AUTHENTICATION
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),

    # USER PROFILE (self)
    path('users/me/', MeAPIView.as_view(), name='users-me'),
    path('users/me/profile/', ProfileView.as_view(), name='users-me-profile'),
    path('users/me/entreprise/', MyEntrepriseAPIView.as_view(), name='users-me-entreprise'),

    # ROUTER (CRUD ADMIN + USERS)
    path('', include(router.urls)),
]
