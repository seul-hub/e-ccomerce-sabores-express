from django.contrib import admin 
from .models import Usuario,Pedido,DetallePedido,Producto
admin.site.register(Usuario)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Producto)

# Register your models here.
