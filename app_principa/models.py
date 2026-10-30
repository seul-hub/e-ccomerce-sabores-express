from decimal import Decimal

from django.db import models


class Usuario(models.Model):
    ROLES = [
        ('Cliente', 'Cliente'),
        ('Gerente', 'Gerente'),
        ('Administrador', 'Administrador'),
        ('Cajero', 'Cajero'),
        ('Repositor', 'Repositor'),
    ]

    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True)
    contrasenia = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES, default='Cliente')

    # Domicilio y teléfono registrados: sirven para rellenar el formulario de pago
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.usuario


class Producto(models.Model):
    CATEGORIAS = [
        ('empanada', 'Empanada'),
        ('pizza', 'Pizza'),
        ('factura', 'Factura'),
        ('combinado', 'Promo'),
        ('bebida', 'Bebida'),
    ]
    DESCUENTOS = [
        (0, 'Sin descuento'),
        (2, '2%'),
        (6, '6%'),
        (10, '10%'),
        (15, '15%'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    imagen = models.CharField(max_length=500, blank=True, help_text="Link (URL) de la foto del producto")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    stock = models.IntegerField(default=0)

    precio_costo = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Lo que te cuesta a vos hacer el producto")
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=40, help_text="Ej: 40 significa 40% de ganancia")
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    descuento = models.IntegerField(choices=DESCUENTOS, default=0)

    # Estos dos se calculan solos al guardar
    precio_neto = models.DecimalField(max_digits=8, decimal_places=2, default=0, editable=False)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0, editable=False, help_text="Precio público: se calcula solo")

    def save(self, *args, **kwargs):
        centavo = Decimal('0.01')
        costo = Decimal(self.precio_costo)
        ganancia = Decimal(self.porcentaje_ganancia)
        iva = Decimal(self.iva)
        descuento = Decimal(self.descuento)

        neto = (costo * (1 + ganancia / 100)).quantize(centavo)
        neto_con_descuento = (neto * (1 - descuento / 100)).quantize(centavo)

        self.precio_neto = neto
        self.precio = (neto_con_descuento * (1 + iva / 100)).quantize(centavo)
        super().save(*args, **kwargs)

    @property
    def neto_con_descuento(self):
        descuento = Decimal(self.descuento)
        return (self.precio_neto * (1 - descuento / 100)).quantize(Decimal('0.01'))

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    FORMAS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('mercadopago', 'Mercado Pago'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)

    # Datos de entrega del momento de la compra (no cambian si el cliente edita su perfil después)
    nombre_apellido = models.CharField(max_length=150, blank=True)
    domicilio = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    forma_pago = models.CharField(max_length=20, choices=FORMAS_PAGO, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)

    # Se guardan los precios del momento de la compra, así los reportes no cambian si después cambia el precio
    precio_neto = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    @property
    def neto_total(self):
        return self.precio_neto * self.cantidad

    @property
    def total(self):
        return self.precio_unitario * self.cantidad

    @property
    def iva_total(self):
        return self.total - self.neto_total

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
