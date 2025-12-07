from rest_framework import generics, permissions, viewsets, filters, status
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
    Entreprise,
    Rating,
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
    RatingSerializer,
)
from .permissions import IsAdminOrSelf

User = get_user_model()


# -----------------------
# Register / Login / Logout
# -----------------------
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
        # delete token if exists
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        logout(request)
        return Response({"detail": "Déconnexion réussie."})


# -----------------------
# User profile (current user) - we'll use /users/me/ action in UserViewSet
# -----------------------
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


# -----------------------
# Ratings endpoints
# -----------------------
class RateUserAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        rater = self.request.user
        # optionally prevent rating self
        rated = serializer.validated_data['rated']
        if rated == rater:
            raise serializers.ValidationError("Vous ne pouvez pas noter vous-même.")
        # Save
        serializer.save(rater=rater)
        # Update rated user stats (simple recalculation)
        ratings = Rating.objects.filter(rated=rated)
        total = sum(r.score for r in ratings)
        avg = round(total / ratings.count(), 2) if ratings.exists() else 0
        # Update profil if technicien
        try:
            prof = rated.profil_technicien
            prof.note_moyenne = avg
            prof.nombre_avis = ratings.count()
            prof.save()
        except Exception:
            # not a technicien or no profil -> ignore
            pass


class RatingsGivenAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(rater=self.request.user)


class RatingsReceivedAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(rated=self.request.user)


# -----------------------
# User ViewSet for admin + /users/me/
# -----------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "first_name", "last_name"]
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
        class ChangePasswordSerializer(serializers.Serializer):
            password = serializers.CharField(write_only=True, validators=[password_validation.validate_password])
            password2 = serializers.CharField(write_only=True)
            def validate(self, attrs):
                if attrs["password"] != attrs["password2"]:
                    raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
                return attrs

        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["password"])
        user.save()
        return Response({"detail": "Mot de passe mis à jour."})


# -----------------------
# Profile viewsets (admin)
# -----------------------
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


class EntrepriseViewSet(viewsets.ModelViewSet):
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [permissions.IsAdminUser]


# -----------------------
# Admin Rating viewset (optional)
# -----------------------
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
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
