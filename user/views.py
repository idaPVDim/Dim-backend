from rest_framework import generics, permissions, viewsets, filters, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, logout, password_validation
from django.shortcuts import get_object_or_404

from .models import (
    ProfilClient,
    ProfilTechnicien,
    ProfilMarchand,
    Entreprise
)

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
    TokenLoginSerializer,
    ProfilClientSerializer,
    ProfilTechnicienSerializer,
    ProfilMarchandSerializer,
    EntrepriseSerializer,
)

User = get_user_model()


# -------------------------------------------------------
# AUTH : REGISTER, LOGIN, LOGOUT
# -------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"detail": "Déconnexion réussie."})


# -------------------------------------------------------
# PROFIL DU USER CONNECTÉ /users/me/
# -------------------------------------------------------

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrSelf
from .serializers import UserProfileSerializer

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get(self, request):
        """Get the current user's profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Update the current user's profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

from .serializers import EntrepriseSerializer

class MyEntrepriseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get(self, request):
        if request.user.role not in ["technicien", "marchand"]:
            return Response({"detail": "This role has no company"}, status=403)
        serializer = EntrepriseSerializer(request.user.entreprise)
        return Response(serializer.data)

    def patch(self, request):
        if request.user.role not in ["technicien", "marchand"]:
            return Response({"detail": "This role has no company"}, status=403)
        serializer = EntrepriseSerializer(request.user.entreprise, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# -------------------------------------------------------
# LISTE DES USERS (ADMIN)
# -------------------------------------------------------

class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()


# -------------------------------------------------------
# PERMISSION : ADMIN ou SOI-MÊME
# -------------------------------------------------------

class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


# -------------------------------------------------------
# USER VIEWSET (CRUD admin + /users/me/)
# -------------------------------------------------------

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email"]
    ordering_fields = ["email", "role"]

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return UserProfileSerializer
        if self.action == "create":
            return RegisterSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ["list", "create", "destroy"]:
            return [permissions.IsAdminUser()]
        if self.action in ["retrieve", "update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsAdminOrSelf()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == "GET":
            return Response(UserProfileSerializer(request.user).data)

        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=["put"], permission_classes=[permissions.IsAdminUser])
    def change_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["password"])
        user.save()

        return Response({"detail": "Mot de passe mis à jour."})


# -------------------------------------------------------
# PROFILS CLIENT / TECHNICIEN / MARCHAND (ADMIN)
# -------------------------------------------------------

class ProfilClientViewSet(viewsets.ModelViewSet):
    queryset = ProfilClient.objects.all()
    serializer_class = ProfilClientSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfilTechnicienViewSet(viewsets.ModelViewSet):
    queryset = ProfilTechnicien.objects.all()
    serializer_class = ProfilTechnicienSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfilMarchandViewSet(viewsets.ModelViewSet):
    queryset = ProfilMarchand.objects.all()
    serializer_class = ProfilMarchandSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------------------------------------
# ENTREPRISE CRUD (ADMIN)
# -------------------------------------------------------

class EntrepriseViewSet(viewsets.ModelViewSet):
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------------------------------------
# CHANGEMENT DE MOT DE PASSE
# -------------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[password_validation.validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
