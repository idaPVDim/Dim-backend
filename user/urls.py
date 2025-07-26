from django.urls import path
from .views import RegisterView, ProfileView, UserListView, LoginView, LogoutView

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, ProfilClientViewSet, ProfilTechnicienViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profil-clients', ProfilClientViewSet, basename='profilclient')
router.register(r'profil-techniciens', ProfilTechnicienViewSet, basename='profiltechnicien')
urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/users/', UserListView.as_view(), name='user-list'),
     path('api/', include(router.urls)),
]
