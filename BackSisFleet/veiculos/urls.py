from django.urls import path
from .views import VeiculosView

urlpatterns = [
    path('', VeiculosView.as_view(), name='veiculos'),
]