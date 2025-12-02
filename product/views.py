from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from .models import Categorie, Marque, Equipement
from .serializers import CategorieSerializer, MarqueSerializer, EquipementSerializer
from .permissions import IsMarchandOwner
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser ,AllowAny
class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom']


class MarqueViewSet(viewsets.ModelViewSet):
    queryset = Marque.objects.all()
    serializer_class = MarqueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    permission_classes = [IsAuthenticated]
    ordering_fields = ['nom']


from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class EquipementViewSet(ModelViewSet):
    serializer_class = EquipementSerializer
    permission_classes = [IsAuthenticated, IsMarchandOwner]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profil_marchand"):
            return Equipement.objects.filter(marchant=user.profil_marchand)
        return Equipement.objects.none()

    def perform_create(self, serializer):
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
        equipement.save()

        return Response({
            "message": "Stock réduit.",
            "nouveau_stock": equipement.quantite_stock
        })

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Equipement
from .serializers import EquipementSerializer


class StockViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Equipement.objects.get(pk=pk, marchant=self.request.user.profil_marchand)
        except Equipement.DoesNotExist:
            return None

    # ============================
    # 1) FIXER LE STOCK
    # ============================
    @action(methods=["post"], detail=True)
    def set(self, request, pk=None):
        equip = self.get_object(pk)
        if not equip:
            return Response({"detail": "Equipement introuvable."}, status=404)

        qty = request.data.get("quantite_stock")
        if qty is None:
            return Response({"detail": "Champ quantite_stock requis."}, status=400)

        equip.quantite_stock = int(qty)
        equip.save()
        return Response({"message": "Stock mis à jour.", "stock": equip.quantite_stock})

    # ============================
    # 2) AUGMENTER LE STOCK
    # ============================
    @action(methods=["post"], detail=True)
    def increase(self, request, pk=None):
        equip = self.get_object(pk)
        if not equip:
            return Response({"detail": "Equipement introuvable."}, status=404)

        qty = int(request.data.get("qty", 0))
        equip.quantite_stock += qty
        equip.save()
        return Response({"message": "Stock augmenté.", "stock": equip.quantite_stock})

    # ============================
    # 3) DIMINUER LE STOCK
    # ============================
    @action(methods=["post"], detail=True)
    def decrease(self, request, pk=None):
        equip = self.get_object(pk)
        if not equip:
            return Response({"detail": "Equipement introuvable."}, status=404)

        qty = int(request.data.get("qty", 0))
        if qty > equip.quantite_stock:
            return Response({"detail": "Stock insuffisant."}, status=400)

        equip.quantite_stock -= qty
        equip.save()
        return Response({"message": "Stock diminué.", "stock": equip.quantite_stock})
