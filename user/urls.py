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
)

router = DefaultRouter()
# Admin CRUD
router.register(r'users', UserViewSet, basename='user')
router.register(r'profil-clients', ProfilClientViewSet, basename='profil-client')
router.register(r'profil-techniciens', ProfilTechnicienViewSet, basename='profil-technicien')
router.register(r'profil-marchands', ProfilMarchandViewSet, basename='profil-marchand')
router.register(r'entreprises', EntrepriseViewSet, basename='entreprise')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),

    # Current user profile
    path('users/me/', MeAPIView.as_view(), name='users-me'),
    path('users/me/entreprise/', MyEntrepriseAPIView.as_view(), name='users-me-entreprise'),

    # Include admin CRUD
    path('', include(router.urls)),
]
