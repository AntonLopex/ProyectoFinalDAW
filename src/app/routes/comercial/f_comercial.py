from datetime import datetime
import secrets
import string
from sqlalchemy import exists
from flask import flash, json, jsonify, render_template, redirect, request, url_for
from flask_login import current_user, login_user
from sqlalchemy import select
from forms.adminForms.comercial_form import UsuarioComercialForm
from models.acompanante import Acompanante
from models.control_es import ControlES
from models.detalle_pedido import DetallePedido
from models.usuario import Usuario
from models.pedido import Pedido
from models.enums import RolEnum
from models.producto import Producto
from extensions import db
from werkzeug.security import generate_password_hash
import uuid

from utils.utils import comprobarContraseña, correo_confirmacion_registro, createUsername, generar_qr_imagen_64, inject_year



# ═══════════════════════════════════════════════════════════════════════════════
# GUARDAS
# ═══════════════════════════════════════════════════════════════════════════════

# Función que verifica si un cliente específico pertenece al comercial actual, comprobando la relación en la base de datos entre el cliente y el comercial,
#  y asegurándose de que el cliente tenga el rol adecuado
def es_cliente_del_comercial(cliente_id, comercial_id):
    return Usuario.query.filter_by(
        id=cliente_id,
        comercial_id=comercial_id,
        rol=RolEnum.cliente
    ).first() is not None



# Función que verifica si un pedido específico es accesible para el comercial actual, comprobando que el pedido esté asociado a un cliente que pertenece al comercial
def es_pedido_accesible(pedido_id, comercial_id):
    return (
        Pedido.query
        .join(Usuario, Pedido.cliente_id == Usuario.id)
        .filter(
            Pedido.id == pedido_id,
            Usuario.comercial_id == comercial_id
        )
        .first() is not None
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLIENTES
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del listado de clientes asociados al comercial actual, mostrando información relevante de cada cliente y su estado de acceso
def f_obtener_mis_clientes(comercial_id, request):
    page = request.args.get("page", 1, type=int)

    query = (
        Usuario.query
        .filter_by(comercial_id=comercial_id, rol=RolEnum.cliente, estado=True)
        .order_by(Usuario.fecha_alta.desc())
    )

    paginado = query.paginate(page=page, per_page=10, error_out=False)

    def esta_dentro(cliente):
        return db.session.scalar(
            select(
                exists().where(
                    ControlES.usuario_id == cliente.id,
                    ControlES.hora_salida == None
                )
            )
        )

    clientes_con_estado = [(c, esta_dentro(c)) for c in paginado.items]

    return render_template(
        "comercial/comercial_cliente.html",
        clientes_con_estado=clientes_con_estado,
        paginacion=paginado
    )



# Función que maneja la visualización del detalle de un cliente específico asociado al comercial actual, 
# mostrando información detallada del cliente y su estado de acceso
def f_obtener_detalle_cliente(cliente_id, comercial_id):
    if not es_cliente_del_comercial(cliente_id, comercial_id):
        return render_template("comercial/clientes.html", error="Cliente no encontrado.")
    cliente = Usuario.query.get(cliente_id)
    return render_template("comercial/comercial_cliente.html", cliente=cliente)



# Función que maneja la creación de un nuevo cliente asociado al comercial actual, validando los datos ingresados 
# y asegurándose de que el email no esté registrado previamente, generando un código cliente único y un token QR, y guardando la información en la base de datos
def f_crear_cliente(data, comercial_id):
    if Usuario.query.filter_by(email=data.get("email")).first():
        return render_template("comercial/comercial_cliente.html", error="El email ya está registrado.")

    qr_token = uuid.uuid4().hex
    while Usuario.query.filter_by(qr_token=qr_token).first():
        qr_token = uuid.uuid4().hex

    base = (
        data.get("nombre", "")[:1] +
        data.get("apellido1", "")[:1] +
        data.get("apellido2", "")[:1]
    ).upper()
    nombre_usuario = base
    contador = 1
    while Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
        nombre_usuario = f"{base}{contador}"
        contador += 1

    password_aleatoria = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    nuevo_cliente = Usuario(
        nombre         = data.get("nombre"),
        apellido1      = data.get("apellido1"),
        apellido2      = data.get("apellido2"),
        nombre_usuario = nombre_usuario,
        email          = data.get("email"),
        password_hash  = generate_password_hash(password_aleatoria),
        rol            = RolEnum.cliente,
        nombre_empresa = data.get("nombre_empresa"),
        cif_empresa    = data.get("cif_empresa"),
        codigo         = None,
        comercial_id   = comercial_id,
        qr_token       = qr_token,
        estado         = True
    )

    try:
        db.session.add(nuevo_cliente)
        db.session.commit()
        return redirect(url_for("router_comercial.mis_clientes"))
    except Exception as e:
        db.session.rollback()
        return render_template("comercial/comercial_cliente.html", error=f"Error al crear el cliente: {str(e)}")


# Función que maneja la actualización de la información de un cliente específico asociado al comercial actual, 
# validando que el cliente pertenezca al comercial, y actualizando los campos editables en la base de datos, manejando posibles errores durante el proceso
def f_actualizar_cliente(cliente_id, data, comercial_id):
    if not es_cliente_del_comercial(cliente_id, comercial_id):
        return render_template("comercial/comercial_cliente.html", error="Cliente no encontrado.")

    cliente = Usuario.query.get(cliente_id)

    campos_editables = [
        "nombre", "apellido1", "apellido2",
        "nombre_empresa", "cif_empresa", "direccion_empresa"
    ]

    for campo in campos_editables:
        if campo in data:
            setattr(cliente, campo, data[campo])

    try:
        db.session.commit()
        return redirect(url_for("router_comercial.mis_clientes"))
    except Exception as e:
        db.session.rollback()
        return render_template("comercial/comercial_cliente.html", error=f"Error al actualizar el cliente: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# PEDIDOS
# ═══════════════════════════════════════════════════════════════════════════════ 
 

 # Función que maneja la visualización del listado de pedidos asociados a los clientes del comercial actual, 
 # con filtros opcionales por fecha y cliente, mostrando información relevante de cada pedido
def f_obtener_pedidos_por_comercial(comercial_id, fecha_inicio=None, fecha_fin=None, cliente_id=None):
    """Devuelve la lista de pedidos del comercial con filtros opcionales."""
 
    # Validación de cliente antes de filtrar
    if cliente_id:
        if not es_cliente_del_comercial(cliente_id, comercial_id):
            return render_template(
                "comercial/comercial_pedido.html",
                error="El cliente no pertenece a este comercial.",
                pedidos=[],
            )
 
    query = (
        Pedido.query
        .join(Usuario, Pedido.cliente_id == Usuario.id)
        .filter(Usuario.comercial_id == comercial_id)
    )
 
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
 
    if fecha_inicio:
        query = query.filter(Pedido.fecha_pedido >= fecha_inicio)
 
    if fecha_fin:
        query = query.filter(Pedido.fecha_pedido <= fecha_fin)
 
    pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()
    return render_template("comercial/comercial_pedido.html", pedidos=pedidos, productos=[])
 
 

# Función que maneja la visualización del detalle de un pedido específico asociado a los clientes del comercial actual,
#  mostrando información detallada del pedido, sus líneas, y el catálogo de productos para posibles
def f_editar_pedido(pedido_id, comercial_id):
    """Procesa el formulario de edición del pedido (POST)."""
 
    if not es_pedido_accesible(pedido_id, comercial_id):
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_comercial.mis_pedidos"))
 
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_comercial.mis_pedidos"))
 
    if pedido.estado == "cancelado":
        flash("No se puede editar un pedido cancelado.", "danger")
        return redirect(url_for("router_comercial.detalle_pedido", pedido_id=pedido_id))
 
    # ── Parsear líneas ───────────────────────────────────────────
    try:
        lineas_data = json.loads(request.form.get("lineas_json", "[]"))
    except (ValueError, TypeError):
        flash("Datos de líneas inválidos.", "danger")
        return redirect(url_for("router_comercial.detalle_pedido", pedido_id=pedido_id))
 
    if not lineas_data:
        flash("El pedido debe tener al menos una línea.", "danger")
        return redirect(url_for("router_comercial.detalle_pedido", pedido_id=pedido_id))
 
    # ── Validar que los productos existen ────────────────────────
    ids_producto = [int(l["producto_id"]) for l in lineas_data]
    productos_map = {
        p.id: p
        for p in Producto.query.filter(Producto.id.in_(ids_producto)).all()
    }
 
    if len(productos_map) != len(set(ids_producto)):
        flash("Uno o más productos no existen.", "danger")
        return redirect(url_for("router_comercial.detalle_pedido", pedido_id=pedido_id))
 
    for l in lineas_data:
        if int(l.get("cantidad", 0)) < 1:
            flash("Todas las cantidades deben ser mayor que 0.", "danger")
            return redirect(url_for("router_comercial.detalle_pedido", pedido_id=pedido_id))
 
    # ── Reemplazar líneas del pedido ─────────────────────────────
    DetallePedido.query.filter_by(pedido_id=pedido_id).delete()
 
    total = 0.0
    for l in lineas_data:
        producto = productos_map[int(l["producto_id"])]
        cantidad = int(l["cantidad"])
        precio   = float(producto.precio)   # siempre precio actual del catálogo
        subtotal = round(precio * cantidad, 2)
 
        db.session.add(DetallePedido(
            pedido_id       = pedido_id,
            producto_id     = producto.id,
            cantidad        = cantidad,
            precio_unitario = precio,
            subtotal        = subtotal,
        ))
        total += subtotal
 
    pedido.total         = round(total, 2)
    pedido.observaciones = request.form.get("observaciones", "").strip() or None
 
    db.session.commit()
 
    flash("Pedido actualizado correctamente.", "success")
    return redirect(url_for("router_comercial.detalle_pedido", pedido_id=pedido_id))
 


 # Función que maneja la visualización del detalle de un pedido específico asociado a los clientes del comercial actual,
 #  mostrando información detallada del pedido, sus líneas, y el catálogo de productos para posibles ediciones
def f_obtener_detalle_pedido(pedido_id, comercial_id):
    if not es_pedido_accesible(pedido_id, comercial_id):
        return render_template("comercial/comercial_pedido.html", error="Pedido no encontrado.")

    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return render_template("comercial/comercial_pedido.html", error="Pedido no encontrado.")

    productos_raw = Producto.query.order_by(Producto.nombre).all()

    # Convertir a dicts simples para que tojson pueda serializarlos
    productos = [
        {
            "id":        p.id,
            "nombre":    p.nombre,
            "precio":    float(p.precio),
            "proveedor": (p.proveedor.nombre_empresa or p.proveedor.nombre) if p.proveedor else "",
        }
        for p in productos_raw
    ]

    return render_template(
        "comercial/comercial_pedido.html",
        pedido    = pedido,
        productos = productos,
    )
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# CATALOGO
# ═══════════════════════════════════════════════════════════════════════════════ 
 

 # Función que maneja la visualización del listado de productos disponibles en el catálogo, con filtros opcionales por búsqueda y proveedor,
 #  y soporte para paginación y carga dinámica mediante AJAX
def f_catalogo_productos():
    busqueda     = request.args.get("busqueda", "").strip()
    proveedor_id = request.args.get("proveedor_id", type=int)
    page         = request.args.get("page", 1, type=int)
    per_page     = request.args.get("per_page", 20, type=int)
    formato      = request.args.get("formato", "")
 
    query = Producto.query
 
    if busqueda:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f"%{busqueda}%"),
                db.cast(Producto.id, db.String).ilike(f"%{busqueda}%"),
            )
        )
 
    if proveedor_id:
        query = query.filter_by(proveedor_id=proveedor_id)
 
    query      = query.order_by(Producto.nombre)
    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    has_more   = paginacion.has_next
 
    if formato == "json":
        html = render_template(
            "partials/_cards_productos_comercial.html",
            productos = paginacion.items,
        )
        return jsonify({
            "html":     html,
            "has_more": has_more,
            "total":    paginacion.total,
            "loaded":   page * per_page,
        })
 
    return render_template(
        "comercial/catalogo_producto.html",
        productos    = paginacion.items,
        proveedores  = Usuario.query.filter_by(rol=RolEnum.proveedor, estado=True).all(),
        busqueda     = busqueda,
        proveedor_id = proveedor_id,
        has_more     = has_more,
    )
 


# Función que maneja la visualización del detalle de un producto específico, mostrando información detallada del producto, su proveedor, y su código QR 
def f_detalle_producto(producto_id):
    producto = db.session.get(Producto, producto_id)
 
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("router_comercial.catalogo"))
 
    return render_template("comercial/catalogo_producto.html", producto=producto)


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD Y REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del dashboard principal del comercial, mostrando información relevante y actualizada sobre sus clientes,
#  pedidos, y otras métricas clave
def f_comercial():
    return render_template("comercial/comercial.html", now=datetime.now())



# Función que maneja el proceso de registro de un nuevo comercial, validando los datos ingresados, asegurándose de que el email no esté registrado previamente,
#  generando un nombre de usuario único, un token QR, y guardando la información
def f_registo_comercial():
    if current_user.is_authenticated:
        flash("Este usuario ya se encuentra registrado.", "warning")
        return redirect(url_for("router_index.register"))

    form = UsuarioComercialForm()

    if form.validate_on_submit():

        # nombre_empresa y cif_empresa no están en el WTForm, se leen del request
        company     = request.form.get("company", "").strip() or None
        company_cif = request.form.get("company_cif", "").strip() or None

        if Usuario.query.filter_by(email=form.email.data).first():
            flash("El email ya está registrado.", "danger")
            return render_template("auth/registro_comercial.html", form=form,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        username = createUsername(form.nombre.data, form.apellido1.data, form.apellido2.data)

        if Usuario.query.filter_by(nombre_usuario=username).first():
            flash("El nombre de usuario ya existe.", "danger")
            return render_template("auth/registro_comercial.html", form=form,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        if not comprobarContraseña(form.password.data, form.confirmar_password.data):
            return render_template("auth/registro_comercial.html", form=form,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        qr_token = uuid.uuid4().hex
        while Usuario.query.filter_by(qr_token=qr_token).first():
            qr_token = uuid.uuid4().hex

        new_user = Usuario(
            nombre         = form.nombre.data,
            apellido1      = form.apellido1.data,
            apellido2      = form.apellido2.data,
            nombre_usuario = username,
            email          = form.email.data,
            nombre_empresa = company,
            cif_empresa    = company_cif,
            rol            = "comercial",
            qr_token       = qr_token,
            estado         = True
        )
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
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
        "auth/registro_comercial.html",
        form=form,
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
        SHORT_YEAR=inject_year()['SHORT_YEAR']
    )


# Función que maneja la visualización del código QR del comercial, generando la imagen a partir del token QR almacenado en la base de datos,
#  y mostrando información relevante del comercial

def f_mi_qr_comercial(comercial_id):
    comercial = Usuario.query.get(comercial_id)

    if not comercial or not comercial.qr_token:
        flash("No tienes un QR asignado. Contacta con administración.", "warning")
        return redirect(url_for("router_comercial.dashboard"))

    qr_base64 = generar_qr_imagen_64(comercial.qr_token)

    return render_template(
        "comercial/comercial_qr.html",
        comercial         = comercial,
        qr_base64       = qr_base64,
        now             = datetime.now(),
        CURRENT_YEAR    = inject_year()['CURRENT_YEAR'],
        SHORT_YEAR      = inject_year()['SHORT_YEAR']
    )