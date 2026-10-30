from .models import Pedido, Usuario


def usuario_actual(request):
    """Deja disponibles en todos los templates:
    - usuario_actual: el usuario en sesión (None si no hay)
    - pedidos_usuario: sus pedidos, del más nuevo al más viejo

    Las consultas son perezosas: solo se ejecutan en las páginas
    cuyo template recorre `pedidos_usuario`.
    """
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.filter(id=usuario_id).first() if usuario_id else None

    pedidos = Pedido.objects.none()
    if usuario:
        pedidos = (
            Pedido.objects.filter(usuario=usuario)
            .prefetch_related('items')
            .order_by('-fecha')
        )

    return {'usuario_actual': usuario, 'pedidos_usuario': pedidos}
