from django.urls import path
from .views import DimensionnementPvAPIView

urlpatterns = [
    path('dimensionnement-pv/', DimensionnementPvAPIView.as_view(), name='dimensionnement-pv'),
]
