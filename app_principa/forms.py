from django import forms

from .models import Producto, Usuario


class ProductoForm(forms.ModelForm):
    stock = forms.IntegerField(min_value=0, label='Stock')
    precio_costo = forms.DecimalField(min_value=0, max_digits=8, decimal_places=2, label='Precio de costo')
    porcentaje_ganancia = forms.DecimalField(min_value=0, max_digits=5, decimal_places=2, label='Ganancia (%)')
    iva = forms.DecimalField(min_value=0, max_value=100, max_digits=5, decimal_places=2, label='IVA (%)')

    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'imagen', 'descripcion', 'stock',
            'precio_costo', 'porcentaje_ganancia', 'iva', 'descuento',
        ]
        labels = {
            'nombre': 'Nombre del producto',
            'categoria': 'Categoría',
            'imagen': 'Imagen (link)',
            'descripcion': 'Descripción',
            'descuento': 'Descuento',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['usuario', 'nombre', 'rol', 'contrasenia']
        labels = {
            'usuario': 'Nombre de usuario',
            'nombre': 'Nombre y apellido',
            'rol': 'Rol',
            'contrasenia': 'Contraseña',
        }
        widgets = {
            'contrasenia': forms.PasswordInput(render_value=True),
        }
