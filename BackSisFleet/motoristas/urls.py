from django.urls import path
from .views.motoristas import MotoristasView
from .views.app_motoristas import AppMotoristasView

urlpatterns = [
    path('', MotoristasView.as_view(), name='motoristas'),
    path('app/', AppMotoristasView.as_view(), name='app_motoristas'),
]
