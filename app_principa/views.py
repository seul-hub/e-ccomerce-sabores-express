from django.shortcuts import render, redirect
from .models import Usuario


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
            return redirect('seleccion')  # Redirige a la página de selección después del inicio de sesión exitoso
        except Usuario.DoesNotExist:
            error = 'Usuario o contraseña incorrectos'
    return render(request, 'app_principa/login.html', {'error': error})

# Create your views here.
