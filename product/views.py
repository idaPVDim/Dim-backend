from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from .models import Categorie, Marque, Equipement
from .serializers import CategorieSerializer, MarqueSerializer, EquipementSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser
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


class EquipementViewSet(viewsets.ModelViewSet):
    queryset = Equipement.objects.select_related('categorie', 'marque').all()
    serializer_class = EquipementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description', 'type_equipement', 'categorie__nom', 'marque__nom']
    ordering_fields = ['nom', 'categorie__nom', 'marque__nom', 'puissance_W', 'tension_V']
