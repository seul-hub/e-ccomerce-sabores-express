from django.db import models


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True)
    contrasenia = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario


class Producto(models.Model):
    CATEGORIAS = [
        ('empanada', 'Empanada'),
        ('pizza', 'Pizza'),
        ('factura', 'Factura'),
        ('combinado', 'Combinado'),
        ('bebida', 'Bebida'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.CharField(max_length=200, blank=True, help_text="Nombre del archivo de imagen, ej: pizza_muzzarella.jpg")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
# Create your models here.
