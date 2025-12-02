from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from .models import (
    ProfilClient,
    ProfilTechnicien,
    ProfilMarchand,
    Entreprise
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
#  PROFILS
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
        required=False
    )

    class Meta:
        model = ProfilTechnicien
        exclude = ("user",)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProfilMarchandSerializer(serializers.ModelSerializer):
    entreprise = EntrepriseSerializer(read_only=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        queryset=Entreprise.objects.all(),
        source="entreprise",
        write_only=True,
        required=False
    )

    class Meta:
        model = ProfilMarchand
        exclude = ("user",)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


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

        # Création automatique du profil selon le rôle
        if user.role == "client":
            ProfilClient.objects.create(user=user)

        elif user.role == "technicien":
            ProfilTechnicien.objects.create(user=user)

        elif user.role == "marchand":
            ProfilMarchand.objects.create(user=user)

        return user


# ────────────────────────────────────────────────
#  USER SIMPLE
# ────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "phone_number")


# ────────────────────────────────────────────────
#  USER + PROFILS DÉTAILLÉS
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
