from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('control-pedido',views.controlDEpedido, name='control-pedido'),
    path('seleccion',views.seleccion, name='seleccion'),
    path('TpBANFIELD',views.TpBANFIELD, name='TpBANFIELD'),
    path('login/', views.login_view, name='login'), 
]