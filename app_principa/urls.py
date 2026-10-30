from django.urls import path
from . import views

urlpatterns = [


    # Tienda
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('', views.login_view),
    path('salir/', views.salir, name='salir'),
    path('control-pedido', views.controlDEpedido, name='control-pedido'),
    path('seleccion', views.seleccion, name='seleccion'),
    path('productos/<str:categoria>/', views.productos, name='productos'),
    path('buscar/', views.buscar, name='buscar'),
    path('TpBANFIELD', views.TpBANFIELD, name='TpBANFIELD'),

    # Carrito
    path('carrito/estado/', views.carrito_estado, name='carrito_estado'),
    path('carrito/agregar/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/quitar/', views.carrito_quitar, name='carrito_quitar'),
    path('carrito/datos/', views.carrito_datos, name='carrito_datos'),
    path('carrito/comprar/', views.carrito_comprar, name='carrito_comprar'),
    path('checkout/', views.checkout, name='checkout'),

    # Gestión (personal del local)
    path('gestion/reportes/', views.reportes, name='reportes'),
    path('gestion/productos/', views.abm_productos, name='abm_productos'),
    path('gestion/productos/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('gestion/usuarios/', views.abm_usuarios, name='abm_usuarios'),
    path('gestion/usuarios/<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
]
