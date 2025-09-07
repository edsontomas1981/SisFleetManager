# home/urls.py
from django.urls import path
from .views.teste import TesteView

urlpatterns = [
    path('teste/', TesteView.as_view(), name='teste'),
]
