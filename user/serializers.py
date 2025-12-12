from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from .models import (
    ProfilClient,
    ProfilTechnicien,
    ProfilMarchand,
    Entreprise,
    Rating,
)

User = get_user_model()


# ────────────────────────────────────────────────
#  ENTREPRISE
# ────────────────────────────────────────────────

class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entreprise
        fields = "__all__"


# ────────────────────────────────────────────────
#  PROFILS (AVEC RATING)
# ────────────────────────────────────────────────

class ProfilClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilClient
        exclude = ("user",)


class ProfilTechnicienSerializer(serializers.ModelSerializer):
    entreprise = EntrepriseSerializer(read_only=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        queryset=Entreprise.objects.all(),
        source="entreprise",
        write_only=True,
        required=False,
    )

    class Meta:
        model = ProfilTechnicien
        exclude = ("user",)


class ProfilMarchandSerializer(serializers.ModelSerializer):
    entreprise = EntrepriseSerializer(read_only=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        queryset=Entreprise.objects.all(),
        source="entreprise",
        write_only=True,
        required=False,
    )

    class Meta:
        model = ProfilMarchand
        exclude = ("user",)


# ────────────────────────────────────────────────
#  REGISTER (INSCRIPTION)
# ────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "role", "phone_number")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # auto-create profile based on role
        if user.role == "client":
            ProfilClient.objects.create(user=user)

        elif user.role == "technicien":
            ProfilTechnicien.objects.create(user=user)

        elif user.role == "marchand":
            ProfilMarchand.objects.create(user=user)

        return user

# -------------------------------------------------------
# CHANGEMENT DE MOT DE PASSE
# -------------------------------------------------------
from django.contrib.auth import get_user_model, logout, password_validation
from django.shortcuts import get_object_or_404

from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[password_validation.validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attr
# ────────────────────────────────────────────────
#  USER SIMPLE
# ────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "phone_number")


# ────────────────────────────────────────────────
#  USER + PROFIL COMPLET
# ────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    profil_client = ProfilClientSerializer(read_only=True)
    profil_technicien = ProfilTechnicienSerializer(read_only=True)
    profil_marchand = ProfilMarchandSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "profil_client",
            "profil_technicien",
            "profil_marchand",
        )
        read_only_fields = ("email", "role")


# ────────────────────────────────────────────────
#  LOGIN
# ────────────────────────────────────────────────

class TokenLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])

        if not user:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")

        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")

        attrs["user"] = user
        return attrs


# ────────────────────────────────────────────────
#  RATING (NOUVEAU)
# ────────────────────────────────────────────────

class RatingSerializer(serializers.ModelSerializer):
    auteur = UserSerializer(read_only=True)

    technicien_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfilTechnicien.objects.all(), source="technicien",
        write_only=True, required=False
    )
    marchand_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfilMarchand.objects.all(), source="marchand",
        write_only=True, required=False
    )
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfilClient.objects.all(), source="client",
        write_only=True, required=False
    )

    class Meta:
        model = Rating
        fields = [
            "id",
            "note",
            "commentaire",
            "date_creation",
            "auteur",
            "technicien_id",
            "marchand_id",
            "client_id",
        ]

    def validate(self, data):

        # empêcher de noter plusieurs cibles à la fois
        targets = ["technicien", "marchand", "client"]
        filled = [t for t in targets if data.get(t) is not None]

        if len(filled) != 1:
            raise serializers.ValidationError("Vous devez noter exactement UN profil à la fois.")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["auteur"] = user

        return super().create(validated_data)


# ────────────────────────────────────────────────
#  RATING LIST POUR PROFILS
# ────────────────────────────────────────────────

class RatingShortSerializer(serializers.ModelSerializer):
    auteur = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ("id", "note", "commentaire", "date_creation", "auteur")
