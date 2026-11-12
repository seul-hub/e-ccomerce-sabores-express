import calendar
import json
from datetime import date, timedelta
from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import F, ProtectedError, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProductoForm, UsuarioForm
from .models import DetallePedido, Pedido, Producto, Usuario


# ---------- Roles ----------

# A qué página va cada rol cuando inicia sesión
RUTA_INICIAL = {
    'Cliente': 'seleccion',
    'Gerente': 'reportes',
    'Administrador': 'reportes',
    'Repositor': 'abm_productos',
    'Cajero': 'control-pedido',
}

# Quiénes pueden usar el panel del cajero
ROLES_CAJA = ('Cajero', 'Gerente', 'Administrador')


def solo_roles(*roles):
    """Deja entrar a la página solo a los roles indicados."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if request.session.get('rol') not in roles:
                return redirect('login')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


# ---------- Tienda ----------

def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('password')
        email = request.POST.get('email')
        # Opcionales: solo se guardan si registro.html tiene esos inputs
        direccion = (request.POST.get('direccion') or '').strip()
        telefono = (request.POST.get('telefono') or '').strip()
        try:
            Usuario.objects.create(
                nombre=nombre,
                usuario=usuario,
                email = email,
                contrasenia=contrasenia,
                direccion=direccion,
                telefono=telefono,
            )
        except IntegrityError:
            return render(request, 'app_principa/registro.html', {'error': 'Ese nombre de usuario ya existe.'})
        return redirect('login')
    return render(request, 'app_principa/registro.html')


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
        except Usuario.DoesNotExist:
            error = 'Usuario o contraseña incorrectos'
        else:
            request.session['usuario_id'] = user.id
            request.session['rol'] = user.rol
            return redirect(RUTA_INICIAL.get(user.rol, 'seleccion'))
    return render(request, 'app_principa/login.html', {'error': error})


def salir(request):
    request.session.flush()
    return redirect('login')


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


def buscar(request):
    texto = request.GET.get('q', '').strip()
    if texto:
        lista = Producto.objects.filter(
            Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
        )
        titulo = 'Resultados para "' + texto + '"'
    else:
        lista = Producto.objects.all()
        titulo = 'Todos los productos'
    return render(request, 'app_principa/productos.html', {
        'productos': lista,
        'titulo': titulo,
        'categoria_actual': '',
        'texto_busqueda': texto,
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


def carrito_datos(request):
    """Datos registrados del usuario, para rellenar el formulario de pago."""
    try:
        usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Tenés que iniciar sesión para comprar.'}, status=401)
    return JsonResponse({'ok': True, 'domicilio': usuario.direccion, 'telefono': usuario.telefono})


def checkout(request):
    """Ventana que simula el Checkout de Mercado Pago."""
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'app_principa/checkout.html')


@require_POST
def carrito_comprar(request):
    try:
        usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Tenés que iniciar sesión para comprar.'}, status=401)

    carrito = request.session.get('carrito', {})
    productos_en_carrito = Producto.objects.in_bulk([int(clave) for clave in carrito])
    items = [
        (productos_en_carrito[int(clave)], cantidad)
        for clave, cantidad in carrito.items()
        if int(clave) in productos_en_carrito
    ]
    if not items:
        return JsonResponse({'ok': False, 'error': 'El carrito está vacío.'}, status=400)

    # Control de stock: no se puede comprar más de lo que hay
    for producto, cantidad in items:
        if cantidad > producto.stock:
            mensaje = 'No hay stock suficiente de ' + producto.nombre + ' (quedan ' + str(producto.stock) + ').'
            return JsonResponse({'ok': False, 'error': mensaje}, status=400)

    # Datos de entrega que vienen del formulario emergente
    try:
        datos = json.loads(request.body or '{}')
    except ValueError:
        datos = {}
    domicilio = (datos.get('domicilio') or '').strip()
    telefono = (datos.get('telefono') or '').strip()
    guardar_domicilio = bool(datos.get('guardar_domicilio'))

    if not (domicilio and telefono):
        return JsonResponse({'ok': False, 'error': 'Completá el domicilio y el teléfono.'}, status=400)

    with transaction.atomic():
        pedido = Pedido.objects.create(
            usuario=usuario,
            nombre_apellido=usuario.nombre,
            domicilio=domicilio,
            telefono=telefono,
            forma_pago='mercadopago',
        )
        for producto, cantidad in items:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_neto=producto.neto_con_descuento,
                precio_unitario=producto.precio,
            )
            Producto.objects.filter(id=producto.id).update(stock=F('stock') - cantidad)

        if guardar_domicilio:
            usuario.direccion = domicilio
            usuario.save(update_fields=['direccion'])

    request.session['carrito'] = {}
    return JsonResponse({'ok': True, 'pedido': pedido.id})


# ---------- Cajero: control de pedidos ----------

@solo_roles(*ROLES_CAJA)
def controlDEpedido(request):
    """Página del cajero. Las filas y los contadores los carga el JS desde cajero_estado."""
    return render(request, 'app_principa/controlDEpedido.html')


def datos_cajero():
    """Pedidos abiertos (Espera... y En preparacion) y contadores del día."""
    hoy = timezone.localdate()

    abiertos = (
        Pedido.objects.filter(estado__in=['espera', 'preparacion'])
        .select_related('usuario')
        .prefetch_related('items__producto')
        .order_by('fecha')
    )
    lista = []
    for pedido in abiertos:
        lista.append({
            'id': pedido.id,
            'fecha': timezone.localtime(pedido.fecha).strftime('%d/%m/%Y %H:%M'),
            'forma_pago': pedido.get_forma_pago_display() or '-',
            'cliente': pedido.nombre_apellido or pedido.usuario.nombre,
            'domicilio': pedido.domicilio or '-',
            'telefono': pedido.telefono or '-',
            'estado': pedido.estado,
            'estado_texto': pedido.get_estado_display(),
            'total': float(pedido.total),
            'items': [
                {
                    'producto': item.producto.nombre,
                    'cantidad': item.cantidad,
                    'subtotal': float(item.total),
                }
                for item in pedido.items.all()
            ],
        })

    # "Turno" = el día de hoy
    del_dia = Pedido.objects.filter(fecha__date=hoy)
    finalizados_hoy = del_dia.filter(estado='finalizado').prefetch_related('items')
    facturado = sum((pedido.total for pedido in finalizados_hoy), Decimal('0'))

    return {
        'pedidos': lista,
        'resumen': {
            'recibidos': del_dia.count(),
            'en_preparacion': Pedido.objects.filter(estado='preparacion').count(),
            'facturado': float(facturado),
        },
    }


@solo_roles(*ROLES_CAJA)
def cajero_estado(request):
    return JsonResponse({'ok': True, **datos_cajero()})


def _cambiar_estado(pedido_id, estados_permitidos, nuevo_estado, devolver_stock=False):
    """Cambia el estado de un pedido validando de qué estado viene."""
    with transaction.atomic():
        pedido = get_object_or_404(Pedido.objects.select_for_update(), id=pedido_id)
        if pedido.estado not in estados_permitidos:
            mensaje = 'El pedido #' + str(pedido.id) + ' está en "' + pedido.get_estado_display() + '" y no admite esta acción.'
            return JsonResponse({'ok': False, 'error': mensaje, **datos_cajero()}, status=409)

        if devolver_stock:
            for item in pedido.items.all():
                Producto.objects.filter(id=item.producto_id).update(stock=F('stock') + item.cantidad)

        pedido.estado = nuevo_estado
        pedido.save(update_fields=['estado'])
    return JsonResponse({'ok': True, **datos_cajero()})


@solo_roles(*ROLES_CAJA)
@require_POST
def cajero_preparar(request, pedido_id):
    """Espera... -> En preparacion."""
    return _cambiar_estado(pedido_id, ['espera'], 'preparacion')


@solo_roles(*ROLES_CAJA)
@require_POST
def cajero_finalizar(request, pedido_id):
    """Cualquier estado (menos Cancelado) -> Finalizado."""
    return _cambiar_estado(pedido_id, ['espera', 'preparacion'], 'finalizado')


@solo_roles(*ROLES_CAJA)
@require_POST
def cajero_cancelar(request, pedido_id):
    """Solo desde Espera... -> Cancelado, devolviendo el stock."""
    return _cambiar_estado(pedido_id, ['espera'], 'cancelado', devolver_stock=True)


# ---------- Gestión: reportes ----------

@solo_roles('Gerente', 'Administrador')
def reportes(request):
    hoy = timezone.localdate()
    # Solo cuentan las ventas finalizadas por el cajero
    todas = DetallePedido.objects.select_related('pedido', 'producto').filter(pedido__estado='finalizado')

    def total_de(lineas):
        return sum((linea.total for linea in lineas), Decimal('0'))

    # Tarjetas: día, semana (últimos 7 días), mes y año
    ventas_dia = total_de(todas.filter(pedido__fecha__date=hoy))
    ventas_semana = total_de(todas.filter(pedido__fecha__date__gte=hoy - timedelta(days=6)))
    lineas_mes = list(todas.filter(pedido__fecha__year=hoy.year, pedido__fecha__month=hoy.month))
    ventas_mes = total_de(lineas_mes)
    ventas_anio = total_de(todas.filter(pedido__fecha__year=hoy.year))

    # Gráfico: ventas de cada día del mes
    dias_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    ventas_por_dia = [0.0] * dias_del_mes
    for linea in lineas_mes:
        dia = timezone.localtime(linea.pedido.fecha).day
        ventas_por_dia[dia - 1] += float(linea.total)

    # Filtros del listado: producto y fechas
    def leer_fecha(texto, por_defecto):
        try:
            return date.fromisoformat(texto)
        except (TypeError, ValueError):
            return por_defecto

    desde = leer_fecha(request.GET.get('desde'), hoy.replace(day=1))
    hasta = leer_fecha(request.GET.get('hasta'), hoy)
    producto_id = request.GET.get('producto', '')

    filtradas = todas.filter(pedido__fecha__date__gte=desde, pedido__fecha__date__lte=hasta)
    if producto_id.isdigit():
        filtradas = filtradas.filter(producto_id=int(producto_id))
    lineas = list(filtradas.order_by('-pedido__fecha'))

    subtotal_neto = sum((linea.neto_total for linea in lineas), Decimal('0'))
    total_facturado = sum((linea.total for linea in lineas), Decimal('0'))
    unidades = sum(linea.cantidad for linea in lineas)

    return render(request, 'app_principa/reportes.html', {
        'ventas_dia': ventas_dia,
        'ventas_semana': ventas_semana,
        'ventas_mes': ventas_mes,
        'ventas_anio': ventas_anio,
        'datos_grafico': {'dias': list(range(1, dias_del_mes + 1)), 'ventas': ventas_por_dia},
        'productos': Producto.objects.order_by('nombre'),
        'producto_id': producto_id,
        'desde': desde.isoformat(),
        'hasta': hasta.isoformat(),
        'lineas': lineas,
        'subtotal_neto': subtotal_neto,
        'iva_total': total_facturado - subtotal_neto,
        'total_facturado': total_facturado,
        'unidades': unidades,
    })


# ---------- Gestión: productos ----------

@solo_roles('Gerente', 'Administrador', 'Repositor')
def abm_productos(request):
    editar_id = request.GET.get('editar', '')
    instancia = Producto.objects.filter(id=int(editar_id)).first() if editar_id.isdigit() else None
    form = ProductoForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto guardado.')
        return redirect('abm_productos')
    return render(request, 'app_principa/abm_productos.html', {
        'form': form,
        'productos': Producto.objects.order_by('categoria', 'nombre'),
        'editando': instancia,
    })


@solo_roles('Gerente', 'Administrador', 'Repositor')
@require_POST
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        producto.delete()
        messages.success(request, 'Producto eliminado.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: el producto tiene ventas registradas. Dejale el stock en 0.')
    return redirect('abm_productos')


# ---------- Gestión: usuarios ----------

@solo_roles('Gerente', 'Administrador')
def abm_usuarios(request):
    editar_id = request.GET.get('editar', '')
    instancia = Usuario.objects.filter(id=int(editar_id)).first() if editar_id.isdigit() else None
    form = UsuarioForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario guardado.')
        return redirect('abm_usuarios')
    return render(request, 'app_principa/abm_usuarios.html', {
        'form': form,
        'usuarios': Usuario.objects.order_by('rol', 'usuario'),
        'editando': instancia,
    })


@solo_roles('Gerente', 'Administrador')
@require_POST
def eliminar_usuario(request, usuario_id):
    if usuario_id == request.session.get('usuario_id'):
        messages.error(request, 'No podés eliminar tu propio usuario.')
        return redirect('abm_usuarios')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    try:
        usuario.delete()
        messages.success(request, 'Usuario eliminado.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: el usuario tiene pedidos registrados.')
    return redirect('abm_usuarios')