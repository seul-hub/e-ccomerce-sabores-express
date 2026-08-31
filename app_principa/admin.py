from django.contrib import admin
from .models import Usuario, Pedido, DetallePedido, Producto


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_costo', 'porcentaje_ganancia', 'precio')


admin.site.register(Usuario)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Producto, ProductoAdmin)