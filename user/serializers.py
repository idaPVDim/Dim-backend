from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProfilClient, ProfilTechnicien
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'role', 'phone_number')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Créer profil selon rôle
        if user.role == 'client':
            ProfilClient.objects.create(user=user)
        elif user.role == 'technicien':
            ProfilTechnicien.objects.create(user=user)
        return user


class ProfilClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilClient
        exclude = ('user',)


class ProfilTechnicienSerializer(serializers.ModelSerializer):
    id_document = serializers.FileField(required=False, allow_null=True)
    formation_document = serializers.FileField(required=False, allow_null=True)
    certification_docs = serializers.FileField(required=False, allow_null=True)
    autorisation_docs = serializers.FileField(required=False, allow_null=True)
    autres_docs = serializers.FileField(required=False, allow_null=True)
    is_certified = serializers.BooleanField(required=False)

    class Meta:
        model = ProfilTechnicien
        exclude = ('user',)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance




class UserProfileSerializer(serializers.ModelSerializer):
    profil_client = ProfilClientSerializer(read_only=True)
    profil_technicien = ProfilTechnicienSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('email',  'first_name', 'last_name', 'role', 'phone_number', 'profil_client', 'profil_technicien')
        read_only_fields = ('email', 'role')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email',  'first_name', 'last_name','role', 'phone_number')
class TokenLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Email ou mot de passe incorrect.')
            if not user.is_active:
                raise serializers.ValidationError('Compte désactivé.')
        else:
            raise serializers.ValidationError('Email et mot de passe sont requis.')

        attrs['user'] = user
        return attrs