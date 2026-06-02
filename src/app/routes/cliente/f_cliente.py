import uuid
from flask import  jsonify, render_template, redirect, url_for, request, session, flash
from flask_login import current_user, login_user
from datetime import datetime

from forms.adminForms.cliente_form import UsuarioClienteForm
from models.presentacion import Presentacion
from models.presentacion_usuario import PresentacionUsuario
from models.usuario import Usuario
from models.producto import Producto
from models.pedido import Pedido
from models.detalle_pedido import DetallePedido
from models.enums import RolEnum, TipoVCEnum
from models.acompanante import Acompanante
from models.stand import Stand
from utils.utils import correo_confirmacion_registro, createUsername, comprobarContraseña, generar_qr_imagen_64, inject_year, paginar
from extensions import db
from models.config import Config



# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONDE REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja el registro de un nuevo cliente, validando los datos del formulario, creando el usuario y sus acompañantes, 
# generando tokens QR únicos, y enviando un correo de confirmación.
def f_registro():
    if current_user.is_authenticated:
        flash("Este usuario ya se encuentra registrado.", "warning")
        return redirect(url_for("router_cliente.registro"))

    form = UsuarioClienteForm()

    comerciales = Usuario.query.filter_by(
        rol=RolEnum.comercial, estado=True
    ).order_by(Usuario.nombre_usuario).all()

    comerciales_js = [{"id": "", "nombre": "— Sin comercial —"}] + [
        {
            "id": c.id,
            "nombre": f"{c.nombre} {c.apellido1} {c.apellido2 or ''}".strip()
        }
        for c in comerciales
    ]

    if form.validate_on_submit():

        nombres_ac   = request.form.getlist("acompanante_nombre")
        apellidos_ac = request.form.getlist("acompanante_apellido")
        pernoctas_ac = request.form.getlist("acompanante_pernocta")

        if Usuario.query.filter_by(email=form.email.data).first():
            flash("El email ya está registrado.", "danger")
            return render_template("auth/registro_cliente.html", form=form, comerciales_js=comerciales_js,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR'])

        nombreUsuario = createUsername(form.nombre.data, form.apellido1.data, form.apellido2.data)

        if Usuario.query.filter_by(nombre_usuario=nombreUsuario).first():
            flash("El nombre de usuario ya existe.", "danger")
            return render_template("auth/registro_cliente.html", form=form, comerciales_js=comerciales_js,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR'])

        if not comprobarContraseña(form.password.data, form.confirmar_password.data):
            return render_template("auth/registro_cliente.html", form=form, comerciales_js=comerciales_js,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR'])

        qr_token = uuid.uuid4().hex
        while Usuario.query.filter_by(qr_token=qr_token).first():
            qr_token = uuid.uuid4().hex

        fecha_llegada_raw = form.fecha_llegada.data
        fecha_llegada = (
            datetime.fromisoformat(str(fecha_llegada_raw))
            if fecha_llegada_raw else None
        )

        new_user = Usuario(
            nombre         = form.nombre.data,
            apellido1      = form.apellido1.data,
            apellido2      = form.apellido2.data,
            nombre_usuario = nombreUsuario,
            email          = form.email.data,
            rol            = RolEnum.cliente,
            nombre_empresa = (form.nombre_empresa.data or "").strip() or None,
            cif_empresa    = (form.cif_empresa.data    or "").strip() or None,
            codigo         = (form.codigo.data         or "").strip() or None,
            comercial_id   = form.comercial_id.data    or None,
            fecha_llegada  = fecha_llegada,
            tipo_vc        = TipoVCEnum.V,
            qr_token       = qr_token,
            estado         = True,
            pernocta       = form.pernocta.data
        )
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
            db.session.flush()

            for i, (nombre_ac, apellido_ac) in enumerate(zip(nombres_ac, apellidos_ac)):
                nombre_ac   = nombre_ac.strip()
                apellido_ac = apellido_ac.strip()

                if not nombre_ac or not apellido_ac:
                    continue

                qr_token_ac = uuid.uuid4().hex
                while Acompanante.query.filter_by(qr_token=qr_token_ac).first():
                    qr_token_ac = uuid.uuid4().hex

                pernocta_ac = pernoctas_ac[i] == "1" if i < len(pernoctas_ac) else False

                db.session.add(Acompanante(
                    usuario_id = new_user.id,
                    nombre     = nombre_ac,
                    apellido   = apellido_ac,
                    qr_token   = qr_token_ac,
                    pernocta   = pernocta_ac
                ))

            db.session.commit()
            login_user(new_user)
            acompanantes_creados = Acompanante.query.filter_by(usuario_id=new_user.id).all()
            correo_confirmacion_registro(new_user, acompanantes_creados)
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for("router_index.home"))

        except Exception as e:
            db.session.rollback()
            flash("Error al registrar el usuario.", "danger")
            print(e)

    return render_template(
        "auth/registro_cliente.html",
        form=form,
        comerciales_js=comerciales_js,
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
        SHORT_YEAR=inject_year()['SHORT_YEAR']
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS INTERNOS
# ═══════════════════════════════════════════════════════════════════════════════



# Función que devuelve el carrito de la sesión, verificando primero si la plataforma está disponible según la fecha de apertura configurada.
def _obtener_carrito():
    """Devuelve el carrito de la sesión. Formato {producto_id: cantidad}"""
    if bloqueo := _check_fecha_apertura(): return bloqueo
    return session.get('carrito', {})



# Función que guarda el carrito en la sesión, verificando primero si la plataforma está disponible según la fecha de apertura configurada.
def _guardar_carrito(carrito):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    """Guarda el carrito en la sesión."""
    session['carrito'] = carrito
    session.modified = True



# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del dashboard del cliente, mostrando su información, el estado del carrito, los pedidos recientes 
# y las presentaciones inscritas, verificando primero si la plataforma está disponible según la fecha de apertura configurada.
def f_dashboard_cliente(cliente_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    cliente = Usuario.query.get(cliente_id)
    carrito = _obtener_carrito()
    pedidos = (
        Pedido.query
        .filter_by(cliente_id=cliente_id)
        .order_by(Pedido.fecha_pedido.desc())
        .limit(3)
        .all()
    )
    presentaciones_inscritas = PresentacionUsuario.query.filter_by(
        usuario_id=cliente_id
        ).count()
    
    return render_template(
        "cliente/cliente.html",
        cliente        = cliente,
        carrito        = carrito,
        total_carrito  = len(carrito),
        pedidos_recientes = pedidos,
        presentaciones_inscritas = presentaciones_inscritas,
        now            = datetime.now()
    )



# ═══════════════════════════════════════════════════════════════════════════════
# QR PERSONAL
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del QR personal del cliente, generando la imagen QR a partir del token asociado al cliente y sus acompañantes
def f_mi_qr(cliente_id):
    cliente = Usuario.query.get(cliente_id)

    if not cliente or not cliente.qr_token:
        flash("No tienes un QR asignado. Contacta con tu comercial.", "warning")
        return redirect(url_for("router_cliente.dashboard"))

    qr_base64 = generar_qr_imagen_64(cliente.qr_token)

    acompanantes = Acompanante.query.filter_by(usuario_id=cliente_id).all()
    acompanantes_qr = []
    for ac in acompanantes:
        acompanantes_qr.append({
            "nombre":    ac.nombre,
            "apellido":  ac.apellido,
            "qr_base64": generar_qr_imagen_64(ac.qr_token) if ac.qr_token else None
        })

    return render_template(
        "cliente/cliente_qr.html",
        cliente         = cliente,
        qr_base64       = qr_base64,
        acompanantes_qr = acompanantes_qr,
        now             = datetime.now(),
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR']
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CATÁLOGO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del catálogo de productos para el cliente, aplicando filtros de búsqueda y proveedor, paginación,
def f_catalogo_cliente():
    if bloqueo := _check_fecha_apertura(): return bloqueo
    busqueda     = request.args.get("busqueda", "").strip()
    proveedor_id = request.args.get("proveedor_id", type=int)
    page         = request.args.get("page", 1, type=int)
    per_page     = request.args.get("per_page", 20, type=int)
    formato      = request.args.get("formato", "")

    query = Producto.query

    if busqueda:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f'%{busqueda}%'),
                db.cast(Producto.id, db.String).ilike(f'%{busqueda}%')  # cast para buscar por ID numérico
            )
        )

    if proveedor_id:
        query = query.filter_by(proveedor_id=proveedor_id)

    query       = query.order_by(Producto.nombre)
    paginacion  = query.paginate(page=page, per_page=per_page, error_out=False)
    has_more    = paginacion.has_next

    if formato == "json":
        html = render_template("partials/_cards_productos_cliente.html", productos=paginacion.items)
        return jsonify({
            "html":     html,
            "has_more": has_more,
            "total":    paginacion.total,
            "loaded":   page * per_page
        })

    carrito = _obtener_carrito()

    return render_template(
        "cliente/cliente_catalogo.html",
        productos     = paginacion.items,
        proveedores   = Usuario.query.filter_by(rol=RolEnum.proveedor, estado=True).all(),
        busqueda      = busqueda,
        proveedor_id  = proveedor_id,
        carrito       = carrito,
        total_carrito = len(carrito),
        has_more      = has_more
    )      



# Función que maneja la visualización del detalle de un producto específico para el cliente, mostrando su información completa y el estado del carrito
def f_detalle_producto_cliente(producto_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    producto = Producto.query.get(producto_id)
    carrito = _obtener_carrito()

    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("router_cliente.catalogo"))

    return render_template(
        "cliente/cliente_catalogo.html",
        producto       = producto,
        carrito        = carrito,
        total_carrito  = len(carrito)
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CARRITO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del carrito de compras del cliente, mostrando los productos añadidos, sus cantidades, subtotales y el total general, 
# verificando primero si la plataforma está disponible según la fecha de apertura configurada.
def f_ver_carrito():
    if bloqueo := _check_fecha_apertura(): return bloqueo
    carrito = _obtener_carrito()
    items = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        if producto:
            subtotal = float(producto.precio) * cantidad
            total   += subtotal
            items.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal
        })

    return render_template(
        "cliente/cliente_carrito.html",
        items  = items,
        total  = float(total),
        now    = datetime.now()
    )


# Función que maneja la adición de un producto al carrito de compras del cliente, actualizando las cantidades si el producto ya está en el carrito,
# y verificando primero si la plataforma está disponible según la fecha de apertura configurada.
def f_añadir_al_carrito(request):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    producto_id = request.form.get("producto_id")
    cantidad = request.form.get("cantidad", 1)

    if not producto_id:
        flash("Producto no especificado.", "danger")
        return redirect(url_for("router_cliente.catalogo"))
    
    try:
        producto_id = str(int(producto_id))
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        flash("Datos inválidos.", "danger")
        return redirect(url_for("router_cliente.catalogo"))

    producto = Producto.query.get(int(producto_id))
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("router_cliente.catalogo"))

    carrito = _obtener_carrito()
    if producto_id in carrito:
        carrito[producto_id] += cantidad
    else:
        carrito[producto_id] = cantidad

    _guardar_carrito(carrito)
    flash(f"Se han añadido {cantidad} x {producto.nombre} al carrito.", "success")
    return redirect(url_for("router_cliente.catalogo"))



# Función que maneja la actualización de las cantidades de los productos en el carrito de compras del cliente, permitiendo modificar o eliminar productos
def f_actualizar_carrito(request):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    producto_id = request.form.get("producto_id")
    cantidad    = request.form.get("cantidad")

    try:
        producto_id = str(int(producto_id))
        cantidad    = int(cantidad)
    except (ValueError, TypeError):
        flash("Datos inválidos.", "danger")
        return redirect(url_for("router_cliente.carrito"))

    carrito = _obtener_carrito()

    if cantidad <= 0:
        carrito.pop(producto_id, None)
        flash("Producto eliminado del carrito.", "info")
    else:
        carrito[producto_id] = cantidad
        flash("Carrito actualizado.", "success")

    _guardar_carrito(carrito)
    return redirect(url_for("router_cliente.carrito"))



# Función que maneja la acción de vaciar completamente el carrito de compras del cliente, eliminando todos los productos añadidos 
# y verificando primero si la plataforma está disponible según la fecha de apertura configurada.
def f_vaciar_carrito():
    if bloqueo := _check_fecha_apertura(): return bloqueo
    _guardar_carrito({})
    flash("Carrito vaciado.", "info")
    return redirect(url_for("router_cliente.carrito"))
    

# ═══════════════════════════════════════════════════════════════════════════════
# PEDIDOS
# ═══════════════════════════════════════════════════════════════════════════════    


# Función que maneja la confirmación de un pedido por parte del cliente, creando el pedido y sus detalles en la base de datos a partir del carrito.
def f_confirmar_pedido(cliente_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    carrito = _obtener_carrito()

    if not carrito:
        flash("El carrito está vacío.", "warning")
        return redirect(url_for("router_cliente.carrito"))
    
    observaciones = request.form.get("observaciones", "").strip() or None


    nuevo_pedido = Pedido(
        cliente_id    = cliente_id,
        fecha_pedido  = datetime.now(),
        estado        = "pendiente",
        observaciones = observaciones   
    )
    db.session.add(nuevo_pedido)
    db.session.flush()  

    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        if not producto:
            continue

        detalle = DetallePedido(
            pedido_id       = nuevo_pedido.id,
            producto_id     = producto.id,
            cantidad        = cantidad,
            precio_unitario = producto.precio,
            subtotal        = producto.precio * cantidad
        )
        db.session.add(detalle)

    try:
        nuevo_pedido.recalcular_total()
        db.session.commit()
        _guardar_carrito({})
        flash("Pedido confirmado correctamente.", "success")
        return redirect(url_for("router_cliente.mis_pedidos"))
    except Exception as e:
        db.session.rollback()
        flash("Error al confirmar el pedido. Inténtalo de nuevo.", "danger")
        print(e)
        return redirect(url_for("router_cliente.carrito"))



# Función que maneja la visualización del listado de pedidos en el panel de cliente, mostrando los pedidos realizados por el cliente con sus detalles asociados.
def f_mis_pedidos(cliente_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    pedidos = (
        Pedido.query
        .filter_by(cliente_id=cliente_id)
        .order_by(Pedido.fecha_pedido.desc())
        .all()
    )
    return render_template(
        "cliente/cliente_carrito.html",
        pedidos = pedidos,
        now     = datetime.now()
    )


def f_detalle_pedido_cliente(pedido_id, cliente_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    pedido = Pedido.query.filter_by(id=pedido_id, cliente_id=cliente_id).first()

    if not pedido:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_cliente.mis_pedidos"))

    return render_template(
        "cliente/cliente_carrito.html",
        pedido = pedido,
        now    = datetime.now()
    )



# ═══════════════════════════════════════════════════════════════════════════════
# PRESENTACIONES
# ═══════════════════════════════════════════════════════════════════════════════    


# Función que maneja la visualización del listado de presentaciones disponibles para el cliente, mostrando su información y el estado de inscripción del cliente
def f_presentaciones_cliente():
    if bloqueo := _check_fecha_apertura(): return bloqueo
    """Listado de presentaciones con estado de inscripción del cliente."""
    page = request.args.get("page", 1, type=int)
 
    query = Presentacion.query.order_by(Presentacion.fecha_hora.asc())
    paginacion = paginar(query, page=page, per_page=10, orden=Presentacion.fecha_hora.asc())
 
    # IDs de presentaciones en las que ya está inscrito el cliente
    ids_inscritos = {
        pu.presentacion_id
        for pu in PresentacionUsuario.query.filter_by(usuario_id=current_user.id).all()
    }
 
    presentaciones = []
    for p in paginacion.items:
        inscritos = p.presentacion_usuarios.count()
        presentaciones.append({
            "id":            p.id,
            "tema":          p.tema,
            "descripcion":   p.descripcion or "",
            "fecha_hora":    p.fecha_hora.strftime("%d/%m/%Y %H:%M"),
            "aforo":         p.aforo,
            "inscritos":     inscritos,
            "plazas_libres": max(p.aforo - inscritos, 0),
            "organizador":   " ".join(filter(None, [
                p.organizador,
            ])) if p.organizador else "-",
            "inscrito":      p.id in ids_inscritos,
        })
 
    return render_template(
        "cliente/cliente_presentacion.html",
        paginacion=paginacion,
        presentaciones=presentaciones,
    )
 

# Función que maneja la inscripción del cliente en una presentación específica, verificando el aforo disponible y el estado de inscripción previo 
def f_inscribirse(presentacion_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    """Inscribe al cliente en una presentación."""
    presentacion = Presentacion.query.get_or_404(presentacion_id)
 
    # Comprobar si ya está inscrito
    ya_inscrito = PresentacionUsuario.query.filter_by(
        presentacion_id=presentacion_id,
        usuario_id=current_user.id,
    ).first()
 
    if ya_inscrito:
        flash("Ya estás inscrito en esta presentación.", "warning")
        return redirect(url_for("router_cliente.presentaciones"))
 
    # Comprobar aforo
    inscritos = presentacion.presentacion_usuarios.count()
    if inscritos >= presentacion.aforo:
        flash("No quedan plazas disponibles en esta presentación.", "danger")
        return redirect(url_for("router_cliente.presentaciones"))
 
    try:
        nueva_inscripcion = PresentacionUsuario(
            presentacion_id=presentacion_id,
            usuario_id=current_user.id,
        )
        db.session.add(nueva_inscripcion)
        db.session.commit()
        flash(f"Te has inscrito correctamente en «{presentacion.tema}».", "success")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al procesar la inscripción.", "danger")
 
    return redirect(url_for("router_cliente.presentaciones"))
 
 

 # Función que maneja la cancelación de la inscripción del cliente en una presentación específica, eliminando la inscripción de la base de datos
def f_cancelar_inscripcion(presentacion_id):
    if bloqueo := _check_fecha_apertura(): return bloqueo
    """Cancela la inscripción del cliente en una presentación."""
    inscripcion = PresentacionUsuario.query.filter_by(
        presentacion_id=presentacion_id,
        usuario_id=current_user.id,
    ).first_or_404()
 
    presentacion = Presentacion.query.get_or_404(presentacion_id)
 
    try:
        db.session.delete(inscripcion)
        db.session.commit()
        flash(f"Has cancelado tu inscripción en «{presentacion.tema}».", "success")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al cancelar la inscripción.", "danger")
 
    return redirect(url_for("router_cliente.presentaciones"))



# ═══════════════════════════════════════════════════════════════════════════════
# MAPA STANDS
# ═══════════════════════════════════════════════════════════════════════════════ 


# Función que maneja la visualización del mapa de stands para el cliente, mostrando la ubicación y estado de cada stand, así como el proveedor asociado si está ocupado
def f_ver_mapa():
    return render_template("cliente/cliente_mapa.html")


# Función que maneja la obtención de los datos del mapa de stands en formato JSON, incluyendo el estado de cada stand, el proveedor asociado si está ocupado,
#  y los IDs relacionados
def f_ver_mapa_data():
    stands = Stand.query.all()

    resultado = {}

    for stand in stands:

        proveedor = ""

        if (
            stand.solicitud and
            stand.solicitud.usuario and
            stand.solicitud.usuario.nombre_empresa
        ):
            proveedor = stand.solicitud.usuario.nombre_empresa

        resultado[stand.numero_stand] = {
            "estado": stand.estado.value,
            "proveedor": proveedor,
            "proveedor_id": stand.solicitud.usuario_id if stand.solicitud else None,
            "solicitud_id": stand.solicitud_id,
        }

    return jsonify(resultado)


# ═══════════════════════════════════════════════════════════════════════════════
# GUARD FECHA APERTURA
# ═══════════════════════════════════════════════════════════════════════════════


# Función que verifica si la plataforma está disponible según la fecha de apertura configurada, bloqueando el acceso a ciertas funcionalidades 
# si aún no ha llegado la fecha
def _check_fecha_apertura():
    config = Config.query.first()

    if config and config.fecha_forum and datetime.now() < config.fecha_forum:
        fecha_str = config.fecha_forum.strftime("%d/%m/%Y %H:%M")
        flash(
            f"La plataforma estará disponible a partir del {fecha_str}.",
            "warning"
        )
        return redirect(url_for("router_cliente.mi_qr"))

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# QR DETALLE_PRODUCTO Y CATALOGO PROVEEDOR
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la redirección al detalle de un producto específico a partir de un token QR, buscando el producto asociado al token y mostrando su información
def f_scan_producto_qr(token):
    """Recibe un qr_token y redirige al detalle del producto."""
    producto = Producto.query.filter_by(qr_token=token).first()
    if not producto:
        flash("Producto no encontrado o QR inválido.", "danger")
        return redirect(url_for("router_cliente.catalogo"))
    return redirect(url_for("router_cliente.detalle_producto", producto_id=producto.id))


# Función que maneja la redirección al catálogo de un proveedor específico a partir de un token QR, buscando el proveedor asociado al token y mostrando su catálogo
def f_scan_proveedor_qr(token):
    """Recibe un qr_token y redirige al catálogo del proveedor."""
    proveedor = Usuario.query.filter_by(qr_token=token, rol=RolEnum.proveedor).first()
    if not proveedor:
        flash("Proveedor no encontrado o QR inválido.", "danger")
        return redirect(url_for("router_cliente.catalogo"))
    return redirect(url_for("router_cliente.catalogo", proveedor_id=proveedor.id))