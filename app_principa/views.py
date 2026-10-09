import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Usuario, Producto, Pedido, DetallePedido


def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('password')
        Usuario.objects.create(nombre=nombre, usuario=usuario, contrasenia=contrasenia)
        return redirect('login')
    return render(request, 'app_principa/registro.html')


def controlDEpedido(request):
    return render(request, 'app_principa/controlDEpedido.html')


def seleccion(request):
    return render(request, 'app_principa/seleccion.html')


def TpBANFIELD(request):
    return render(request, 'app_principa/TpBANFIELD.html')


def login_view(request):
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')
        try:
            user = Usuario.objects.get(usuario=usuario, contrasenia=contrasenia)
            request.session['usuario_id'] = user.id
            return redirect('seleccion')
        except Usuario.DoesNotExist:
            error = 'Usuario o contraseña incorrectos'
    return render(request, 'app_principa/login.html', {'error': error})


def productos(request, categoria):
    titulos = {
        'pizza': 'Pizzas',
        'empanada': 'Empanadas',
        'factura': 'Facturas',
        'bebida': 'Bebidas',
        'combinado': 'Promos',
    }
    lista = Producto.objects.filter(categoria=categoria)
    return render(request, 'app_principa/productos.html', {
        'productos': lista,
        'titulo': titulos.get(categoria, 'Productos'),
        'categoria_actual': categoria,
    })


# ---------- Carrito ----------

def estado_del_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    for p in Producto.objects.filter(id__in=list(carrito)):
        cantidad = carrito[str(p.id)]
        subtotal = p.precio * cantidad
        total += subtotal
        items.append({
            'id': p.id,
            'nombre': p.nombre,
            'cantidad': cantidad,
            'subtotal': float(subtotal),
        })
    return {'items': items, 'total': float(total)}


def carrito_estado(request):
    return JsonResponse(estado_del_carrito(request))


@require_POST
def carrito_agregar(request):
    datos = json.loads(request.body)
    try:
        producto = Producto.objects.get(id=datos.get('id'))
    except (Producto.DoesNotExist, ValueError, TypeError):
        return JsonResponse(estado_del_carrito(request))
    carrito = request.session.get('carrito', {})
    clave = str(producto.id)
    carrito[clave] = carrito.get(clave, 0) + 1
    request.session['carrito'] = carrito
    return JsonResponse(estado_del_carrito(request))


@require_POST
def carrito_quitar(request):
    datos = json.loads(request.body)
    carrito = request.session.get('carrito', {})
    carrito.pop(str(datos.get('id')), None)
    request.session['carrito'] = carrito
    return JsonResponse(estado_del_carrito(request))


@require_POST
def carrito_comprar(request):
    try:
        usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Tenés que iniciar sesión para comprar.'}, status=401)

    carrito = request.session.get('carrito', {})
    if not carrito:
        return JsonResponse({'ok': False, 'error': 'El carrito está vacío.'}, status=400)

    pedido = Pedido.objects.create(usuario=usuario)
    for producto in Producto.objects.filter(id__in=list(carrito)):
        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=carrito[str(producto.id)],
        )
    request.session['carrito'] = {}
    return JsonResponse({'ok': True, 'pedido': pedido.id})
# Create your views here.
