from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('control-pedido', views.controlDEpedido, name='control-pedido'),
    path('seleccion', views.seleccion, name='seleccion'),
    path('productos/<str:categoria>/', views.productos, name='productos'),
    path('TpBANFIELD', views.TpBANFIELD, name='TpBANFIELD'),
    path('login/', views.login_view, name='login'),
    path('carrito/estado/', views.carrito_estado, name='carrito_estado'),
    path('carrito/agregar/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/quitar/', views.carrito_quitar, name='carrito_quitar'),
    path('carrito/comprar/', views.carrito_comprar, name='carrito_comprar'),
]