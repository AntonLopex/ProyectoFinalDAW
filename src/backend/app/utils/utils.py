from usuarios.models import Usuario

def generate_username(nombre, apellidos):
    # 1. Crear base tipo ALL
    parts = (nombre + " " + apellidos).split()

    base = "".join([p[0].upper() for p in parts if p])

    return base

def generate_unique_username(nombre, apellidos):
    base = "".join([p[0].upper() for p in (nombre + " " + apellidos).split()])

    username = base
    counter = 1

    while Usuario.objects.filter(nombre_usuario=username).exists():
        username = f"{base}{counter}"
        counter += 1

    return username

def get_logged_user(request):

    usuario_id = request.session.get(
        "usuario_id"
    )

    if not usuario_id:
        return None

    try:

        return Usuario.objects.get(
            id=usuario_id
        )

    except Usuario.DoesNotExist:

        return None