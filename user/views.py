from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, logout
from rest_framework.authtoken.models import Token
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
    TokenLoginSerializer,
)
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    ProfilClientSerializer,
    ProfilTechnicienSerializer,
    RegisterSerializer,
)
from .models import ProfilClient, ProfilTechnicien
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

User = get_user_model()



class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TokenLoginSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            print("Login validation error:", e.detail)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()  # supprime le token d’authentification
        logout(request)  # optionnel, si session aussi utilisée
        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)




class IsAdminOrSelf(permissions.BasePermission):
    """
    Autorise uniquement l'admin ou l'utilisateur lui même.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD complet avec permissions :
    - List & Create = admin uniquement
    - Retrieve, Update, Partial_update = admin ou propriétaire
    - Delete = admin uniquement
    """
    queryset = User.objects.all().order_by('email')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email']
    ordering_fields = ['email', 'role']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserProfileSerializer
        elif self.action == 'create':
            return RegisterSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            permission_classes = [IsAuthenticated, IsAdminOrSelf]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        GET /users/me/ : récupérer son profil
        PUT/PATCH /users/me/ : modifier son profil
        """
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        serializer = UserProfileSerializer(request.user, data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser])
    def change_password(self, request, pk=None):
        """
        PUT /users/{id}/change_password/
        Permet à un admin de changer le mot de passe d'un utilisateur.
        """
        user = get_object_or_404(User, pk=pk)
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'detail': 'Mot de passe mis à jour.'}, status=status.HTTP_200_OK)


class ProfilClientViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les profils clients.
    Accessible uniquement aux admins.
    """
    queryset = ProfilClient.objects.all()
    serializer_class = ProfilClientSerializer
    permission_classes = [IsAdminUser]


class ProfilTechnicienViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les profils techniciens.
    Accessible uniquement aux admins.
    """
    queryset = ProfilTechnicien.objects.all()
    serializer_class = ProfilTechnicienSerializer
    permission_classes = [IsAdminUser]

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, validators=[password_validation.validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs