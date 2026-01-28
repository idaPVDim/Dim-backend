from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters
from .models import Categorie, Marque, Equipement
from .serializers import CategorieSerializer, MarqueSerializer, EquipementSerializer
from .permissions import IsMarchandOwner
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom']
    permission_classes = [AllowAny]  # ✅ Accessible à tous


class MarqueViewSet(viewsets.ModelViewSet):
    queryset = Marque.objects.all()
    serializer_class = MarqueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom']
    permission_classes = [AllowAny]  # ✅ Accessible à tous


# ============================
# VUE POUR TOUS LES ÉQUIPEMENTS (clients, public)
# ============================
class EquipementPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vue publique pour voir tous les équipements disponibles.
    Accessible sans authentification ou avec n'importe quel utilisateur.
    """
    serializer_class = EquipementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description', 'type_equipement', 'marque__nom']
    ordering_fields = ['nom', 'prix_unitaire_fcfa', 'puissance_W']
    filterset_fields = ['categorie', 'marque', 'type_equipement', 'mode', 'est_disponible']
    
    def get_queryset(self):
        """
        Retourne tous les équipements disponibles.
        Optionnel: filtrer seulement ceux qui sont en stock.
        """
        queryset = Equipement.objects.filter(est_disponible=True)
        
        # Filtres additionnels depuis les paramètres URL
        marque = self.request.query_params.get('marque', None)
        categorie = self.request.query_params.get('categorie', None)
        prix_min = self.request.query_params.get('prix_min', None)
        prix_max = self.request.query_params.get('prix_max', None)
        
        if marque:
            queryset = queryset.filter(marque__nom__icontains=marque)
        if categorie:
            queryset = queryset.filter(categorie__nom__icontains=categorie)
        if prix_min:
            queryset = queryset.filter(prix_unitaire_fcfa__gte=prix_min)
        if prix_max:
            queryset = queryset.filter(prix_unitaire_fcfa__lte=prix_max)
            
        return queryset.select_related('categorie', 'marque', 'marchant')


# ============================
# VUE POUR LES MARCHANDS (gestion de leurs produits)
# ============================
class EquipementMarchandViewSet(ModelViewSet):
    """
    Vue privée pour que les marchands gèrent leurs propres équipements.
    """
    serializer_class = EquipementSerializer
    permission_classes = [IsAuthenticated, IsMarchandOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description', 'type_equipement']
    ordering_fields = ['nom', 'prix_unitaire_fcfa', 'quantite_stock']
    filterset_fields = ['categorie', 'marque', 'est_disponible']

    def get_queryset(self):
        """
        Retourne uniquement les équipements du marchand connecté.
        """
        user = self.request.user
        if hasattr(user, "profil_marchand"):
            return Equipement.objects.filter(
                marchant=user.profil_marchand
            ).select_related('categorie', 'marque')
        return Equipement.objects.none()

    def perform_create(self, serializer):
        """
        Associe automatiquement l'équipement au marchand connecté.
        """
        serializer.save(marchant=self.request.user.profil_marchand)

    # ---------------------------
    # 🔵 1) SET STOCK
    # ---------------------------
    @action(detail=True, methods=['post'])
    def set_stock(self, request, pk=None):
        equipement = self.get_object()
        try:
            stock = int(request.data.get("quantite_stock"))
        except:
            return Response({"error": "Valeur de stock invalide."}, status=400)

        equipement.quantite_stock = stock
        equipement.est_disponible = stock > 0  # Mettre à jour la disponibilité
        equipement.save()
        return Response({"message": "Stock mis à jour.", "stock": stock})

    # ---------------------------
    # 🟢 2) AUGMENTER STOCK
    # ---------------------------
    @action(detail=True, methods=['post'])
    def increase_stock(self, request, pk=None):
        equipement = self.get_object()

        try:
            qty = int(request.data.get("qty"))
        except:
            return Response({"error": "Valeur invalide."}, status=400)

        equipement.quantite_stock += qty
        equipement.est_disponible = equipement.quantite_stock > 0
        equipement.save()

        return Response({
            "message": "Stock augmenté.",
            "nouveau_stock": equipement.quantite_stock
        })

    # ---------------------------
    # 🔴 3) RÉDUIRE / CONSOMMER STOCK
    # ---------------------------
    @action(detail=True, methods=['post'])
    def decrease_stock(self, request, pk=None):
        equipement = self.get_object()

        try:
            qty = int(request.data.get("qty"))
        except:
            return Response({"error": "Valeur invalide."}, status=400)

        if qty > equipement.quantite_stock:
            return Response(
                {"error": "Stock insuffisant."},
                status=400
            )

        equipement.quantite_stock -= qty
        equipement.est_disponible = equipement.quantite_stock > 0
        equipement.save()

        return Response({
            "message": "Stock réduit.",
            "nouveau_stock": equipement.quantite_stock
        })


# ============================
# VUE POUR ADMIN (tous les équipements)
# ============================
class EquipementAdminViewSet(viewsets.ModelViewSet):
    """
    Vue pour les administrateurs - accès à tous les équipements.
    """
    queryset = Equipement.objects.all().select_related('categorie', 'marque', 'marchant')
    serializer_class = EquipementSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description', 'marchant__nom_boutique']
    ordering_fields = ['nom', 'prix_unitaire_fcfa', 'quantite_stock']