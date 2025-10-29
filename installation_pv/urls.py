from django.urls import path
from .views import DimensionnementPVListCreateView, DimensionnementPVDetailView

urlpatterns = [
    path('dimensionnements-pv/', DimensionnementPVListCreateView.as_view(), name='dimensionnementpv-list-create'),
    path('dimensionnements-pv/<int:pk>/', DimensionnementPVDetailView.as_view(), name='dimensionnementpv-detail'),
]
