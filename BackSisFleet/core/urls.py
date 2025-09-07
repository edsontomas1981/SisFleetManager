from django.urls import path
from .views import HelloView, RegisterView,SolicitarRecuperacaoSenhaView, RedefinirSenhaView

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
    path('register/', RegisterView.as_view(), name='register'),  # opcional
    path("recuperar-senha/", SolicitarRecuperacaoSenhaView.as_view(), name="recuperar-senha"),
    path("redefinir-senha/", RedefinirSenhaView.as_view(), name="redefinir-senha"),
]
