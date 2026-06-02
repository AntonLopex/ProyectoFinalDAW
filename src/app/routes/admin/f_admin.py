import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import uuid
from flask_login import current_user
import pandas as pd
from io import StringIO
import qrcode
import io
from reportlab.platypus import HRFlowable, PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle, Image, Paragraph
from flask_mail import Message
import os
 
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from extensions import mail 


from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file, url_for, current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, subqueryload
from extensions import db
from flask import  Response, json, jsonify, render_template, redirect, request, send_file, url_for, flash
from sqlalchemy import func
from forms.adminForms.cliente_form import UsuarioClienteForm
from forms.adminForms.proveedor_form import UsuarioProveedorForm
from forms.adminForms.comercial_form import UsuarioComercialForm
from forms.adminForms.control_form import UsuarioControlForm    
from models.acompanante import Acompanante
from models.config import Config
from models.control_es import ControlES
from models.detalle_pedido import DetallePedido
from models.detalle_solicitud_mobiliario import DetalleSolicitudMobiliario
from models.detalle_solicitud_stand import DetalleSolicitudStand
from models.extra import Extra
from models.historial_stand import HistorialStand
from models.incidencia import Incidencia
from models.mobiliario import Mobiliario
from models.pedido import Pedido
from models.presentacion import Presentacion
from models.presentacion_usuario import PresentacionUsuario
from models.producto import Producto
from models.stand import Stand
from models.solicitud import Solicitud
from models.usuario import Usuario
from utils.utils import comprobarContraseña, correo_confirmacion_registro, generar_qr_imagen_64, paginar, createUsername,inject_year, registrar_historial
from models.enums import EstadoStandEnum, RolEnum, TipoVCEnum
  


#Función que renderiza el dashboard del admin con la información de la tabla Config  y el número de incidencias pendientes   
def f_adminDashboard():
    config = Config.query.first()
    incidencias_pendientes = Incidencia.query.filter_by(estado="pendiente").count()
    now = datetime.now()
    return render_template("admin/adminDashboard.html", config=config, incidencias_pendientes=incidencias_pendientes, now=now)



#Función que devuelve el número de incidencias pendientes en formato JSON para actualizar el contador en tiempo real en el dashboard del admin
def f_contar_incidencias_pendientes():
    total = Incidencia.query.filter_by(estado="pendiente").count()
    return jsonify({
        "ok": True,
        "total": total
    })


#/=========================================================\
# Funciones para el panel de administración USUARIO CONTROL #
#\=========================================================/

#Función que renderiza la página de listado de usuarios de control con filtros de búsqueda, ordenación y paginación.
def f_listarUsuariosControl():
    # --- Filtros desde query string ---
    busqueda  = request.args.get('busqueda', '').strip()
    orden_dir = request.args.get('orden_dir', 'desc')
    page      = request.args.get('page', 1, type=int)

    query = Usuario.query.filter(Usuario.rol == RolEnum.control)

    # Filtro: nombre completo o nombre_usuario
    if busqueda:
        nombre_completo_expr = func.concat(
            func.coalesce(Usuario.nombre, ''), ' ',
            func.coalesce(Usuario.apellido1, ''), ' ',
            func.coalesce(Usuario.apellido2, '')
        )
        query = query.filter(
            db.or_(
                nombre_completo_expr.ilike(f"%{busqueda}%"),
                Usuario.nombre_usuario.ilike(f"%{busqueda}%"),
            )
        )

    orden = Usuario.id.asc() if orden_dir == 'asc' else Usuario.id.desc()

    form = UsuarioControlForm()
    paginacion = paginar(query, page=page, per_page=10, orden=orden)

    usuarios = []
    for u in paginacion.items:
        nombre_completo = " ".join(filter(None, [
            u.nombre, u.apellido1, u.apellido2
        ])).strip()

        usuarios.append({
            "id":             u.id,
            "nombre_completo": nombre_completo,
            "nombre_usuario": u.nombre_usuario,
            "email":          u.email,
            "fecha_alta":     u.fecha_alta.strftime("%d/%m/%Y, %H:%M") if u.fecha_alta else "-"
        })

    return render_template(
        "admin/listados/listadoControl.html",
        paginacion=paginacion,
        usuarios=usuarios,
        form=form,
        busqueda=busqueda,
        orden_dir=orden_dir,
    )


# Función que maneja la creación de un nuevo usuario de control, validando el formulario, verificando duplicados y enviando correo de confirmación.
def f_crearUsuarioControl():
    form = UsuarioControlForm()

    if form.validate_on_submit():
        nombreUsuario = createUsername(form.nombre.data, form.apellido1.data, form.apellido2.data)

        if Usuario.query.filter_by(email=form.email.data).first():
            flash("El email ya está registrado", "danger")
            return render_template("admin/formularios/formControl.html", form=form)

        if Usuario.query.filter_by(nombre_usuario=nombreUsuario).first():
            flash("El nombre de usuario ya existe", "danger")
            return render_template("admin/formularios/formControl.html", form=form)

        if not comprobarContraseña(form.password.data, form.confirmar_password.data):
            return render_template("admin/formularios/formControl.html", form=form)

        usuario = Usuario(
            nombre=form.nombre.data,
            apellido1=form.apellido1.data,
            apellido2=form.apellido2.data,
            nombre_usuario=nombreUsuario,
            email=form.email.data,
            rol=RolEnum.control
        )

        usuario.set_password(form.password.data)

        try:
            db.session.add(usuario)
            db.session.commit()

            # ── Correo de confirmación ─────────────────────────
            enviado = correo_confirmacion_registro(usuario)

            if enviado:
                flash("Usuario de control creado correctamente. Se ha enviado el correo de confirmación.", "success")
            else:
                flash("Usuario de control creado, pero hubo un error al enviar el correo de confirmación.", "warning")

            return redirect(url_for("router_admin.listarUsuariosControl"))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al crear el usuario de control", "danger")

    return render_template("admin/formularios/formControl.html", form=form)


# Función que devuelve los datos de un usuario de control específico en formato JSON para rellenar el formulario de edición.
def f_obtenerUsuarioControl(id):

    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido1": usuario.apellido1,
        "apellido2": usuario.apellido2,
        "nombre_usuario": usuario.nombre_usuario,
        "email": usuario.email
    })


 # Función que maneja la edición de un usuario de control, validando los datos, verificando duplicados y actualizando la base de datos.   
def f_editarUsuarioControl():

    usuario_id = request.form.get("id")

    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosControl"))

    # ── datos del formulario ─────────────────────
    nombre = request.form.get("nombre")
    apellido1 = request.form.get("apellido1")
    apellido2 = request.form.get("apellido2")
    username = request.form.get("usuario")
    email = request.form.get("email")

    # ── validación email duplicado ───────────────
    if Usuario.query.filter(
        Usuario.email == email,
        Usuario.id != usuario_id
    ).first():
        flash("El email ya está en uso", "danger")
        return redirect(url_for("router_admin.listarUsuariosControl"))

    # ── validación username duplicado ────────────
    if Usuario.query.filter(
        Usuario.nombre_usuario == username,
        Usuario.id != usuario_id
    ).first():
        flash("El nombre de usuario ya existe", "danger")
        return redirect(url_for("router_admin.listarUsuariosControl"))

    # ── actualización en BD ──────────────────────
    usuario.nombre = nombre
    usuario.apellido1 = apellido1
    usuario.apellido2 = apellido2
    usuario.nombre_usuario = createUsername(nombre, apellido1, apellido2)
    usuario.email = email

    try:
        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
        

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al actualizar el usuario", "danger")

    return redirect(url_for("router_admin.listarUsuariosControl"))


# Función que devuelve los datos básicos de un usuario de control específico en formato JSON para mostrar en el modal de confirmación de eliminación.
def f_obtenerUsuarioEliminar(id):

    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "nombre_completo": f"{usuario.nombre} {usuario.apellido1} {usuario.apellido2}",
    })

# Función que maneja la eliminación de un usuario de control, verificando su existencia y eliminándolo de la base de datos.    
def f_eliminarUsuarioControl():

    usuario_id = request.form.get("id")

    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosControl"))

    try:
        db.session.delete(usuario)
        db.session.commit()

        flash("Usuario eliminado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al eliminar el usuario", "danger")

    return redirect(url_for("router_admin.listarUsuariosControl"))

    
#/===========================================================\
# Funciones para el panel de administración USUARIO COMERCIAL #
#\===========================================================/

# Función que renderiza la página de listado de usuarios comerciales con filtros de búsqueda, ordenación y paginación, 
# mostrando también el número de clientes asignados a cada comercial.
def f_listarUsuariosComercial():
    # --- Filtros desde query string ---
    busqueda  = request.args.get('busqueda', '').strip()
    orden_dir = request.args.get('orden_dir', 'desc')
    page      = request.args.get('page', 1, type=int)

    subquery = db.session.query(
        Usuario.comercial_id,
        func.count(Usuario.id).label("total_clientes")
    ).filter(
        Usuario.rol == RolEnum.cliente
    ).group_by(
        Usuario.comercial_id
    ).subquery()

    query = db.session.query(Usuario, subquery.c.total_clientes)\
        .outerjoin(subquery, Usuario.id == subquery.c.comercial_id)\
        .filter(Usuario.rol == RolEnum.comercial)

    # Filtro: nombre completo (nombre + apellidos) o nombre_usuario
    if busqueda:
        nombre_completo_expr = func.concat(
            func.coalesce(Usuario.nombre, ''), ' ',
            func.coalesce(Usuario.apellido1, ''), ' ',
            func.coalesce(Usuario.apellido2, '')
        )
        query = query.filter(
            db.or_(
                nombre_completo_expr.ilike(f"%{busqueda}%"),
                Usuario.nombre_usuario.ilike(f"%{busqueda}%"),
            )
        )

    orden = Usuario.id.asc() if orden_dir == 'asc' else Usuario.id.desc()

    paginacion = paginar(query, page=page, per_page=10, orden=orden)

    usuarios = []
    for comercial, total_clientes in paginacion.items:
        nombre_completo = " ".join(filter(None, [
            comercial.nombre,
            comercial.apellido1,
            comercial.apellido2
        ])).strip()

        usuarios.append({
            "id":             comercial.id,
            "nombre_completo": nombre_completo,
            "nombre":         comercial.nombre,
            "apellido1":      comercial.apellido1,
            "apellido2":      comercial.apellido2,
            "nombre_usuario": comercial.nombre_usuario,
            "email":          comercial.email,
            "fecha_alta":     comercial.fecha_alta.strftime("%d/%m/%Y, %H:%M") if comercial.fecha_alta else "-",
            "num_clientes":   total_clientes or 0
        })

    return render_template(
        "admin/listados/listadoComerciales.html",
        paginacion=paginacion,
        usuarios=usuarios,
        busqueda=busqueda,
        orden_dir=orden_dir,
    )

# Función que devuelve la lista de clientes asignados a un comercial específico en formato JSON para mostrar en el modal de edición del comercial.
def f_api_clientes_comercial(comercial_id):
    
    page = request.args.get("page", 1, type=int)

    query = Usuario.query.filter(
        Usuario.comercial_id == comercial_id,
        Usuario.rol == RolEnum.cliente
    )

    paginacion = paginar(
        query,
        page=page,
        per_page=5,
        orden=Usuario.id.desc()
    )

    clientes = []

    for cliente in paginacion.items:

        cliente_nombre = " ".join(filter(None, [
            cliente.nombre,
            cliente.apellido1,
            cliente.apellido2
        ])).strip()

        clientes.append({
            "id": cliente.id,
            "nombre_completo": cliente_nombre,
            "empresa": cliente.nombre_empresa or "-"
        })

    return jsonify({
        "clientes": clientes,
        "page": paginacion.page,
        "pages": paginacion.pages,
        "total": paginacion.total
    })


# Función que maneja la edición de un usuario comercial, validando los datos, verificando duplicados, actualizando la base de datos 
# y reasignando clientes según lo seleccionado en el formulario.
def f_editarUsuarioComercial(id):

    usuario = Usuario.query.get(id)

    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosComercial"))

    # ── datos del formulario ─────────────────────
    nombre        = request.form.get("nombre")
    apellido1     = request.form.get("apellido1")
    apellido2     = request.form.get("apellido2")
    username_form = request.form.get("usuario")
    email         = request.form.get("email")
    clientes_ids  = request.form.getlist("clientes")  # lista de IDs como strings

    # ── validación básica ────────────────────────
    if not nombre or not apellido1 or not email:
        flash("Faltan campos obligatorios", "danger")
        return redirect(url_for("router_admin.listarUsuariosComercial"))

    # ── detectar cambio en nombre/apellidos ──────
    nombre_cambio = (
        nombre    != usuario.nombre    or
        apellido1 != usuario.apellido1 or
        apellido2 != usuario.apellido2
    )

    # ── email duplicado ──────────────────────────
    if Usuario.query.filter(
        Usuario.email == email,
        Usuario.id    != id
    ).first():
        flash("El email ya está en uso", "danger")
        return redirect(url_for("router_admin.listarUsuariosComercial"))

    # ── lógica username ──────────────────────────
    if nombre_cambio:
        new_username = createUsername(nombre, apellido1, apellido2)

        if Usuario.query.filter(
            Usuario.nombre_usuario == new_username,
            Usuario.id             != id
        ).first():
            flash("El username generado ya existe, ajusta los datos", "danger")
            return redirect(url_for("router_admin.listarUsuariosComercial"))

        usuario.nombre_usuario = new_username

    else:
        if username_form and username_form != usuario.nombre_usuario:

            if Usuario.query.filter(
                Usuario.nombre_usuario == username_form,
                Usuario.id             != id
            ).first():
                flash("El nombre de usuario ya existe", "danger")
                return redirect(url_for("router_admin.listarUsuariosComercial"))

            usuario.nombre_usuario = username_form

    # ── actualización datos base ─────────────────
    usuario.nombre    = nombre
    usuario.apellido1 = apellido1
    usuario.apellido2 = apellido2
    usuario.email     = email

    # ── reasignación de clientes ─────────────────
    # Desasignar todos los clientes actuales de este comercial
    Usuario.query.filter_by(comercial_id=id).update({"comercial_id": None})

    # Asignar los clientes seleccionados
    if clientes_ids:
        Usuario.query.filter(
            Usuario.id.in_([int(cid) for cid in clientes_ids])
        ).update({"comercial_id": id}, synchronize_session="fetch")

    try:
        db.session.commit()
        flash("Usuario actualizado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al actualizar el usuario", "danger")

    return redirect(url_for("router_admin.listarUsuariosComercial"))


# Función que maneja la eliminación de un usuario comercial, verificando su existencia, desasignando sus clientes y eliminándolo de la base de datos.
def f_eliminarUsuarioComercial(id):
    comercial = db.session.get(Usuario, id)

    if not comercial:
        flash("Comercial no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosComercial"))

    if comercial.rol != RolEnum.comercial:
        flash("El usuario no es un comercial", "danger")
        return redirect(url_for("router_admin.listarUsuariosComercial"))

    try:

        # ── 1. desasignar clientes ───────────────────────────
        db.session.query(Usuario).filter(
            Usuario.comercial_id == id
        ).update(
            {Usuario.comercial_id: None},
            synchronize_session=False
        )

        # ── 2. eliminar comercial ────────────────────────────
        db.session.delete(comercial)

        db.session.commit()

        flash("Comercial eliminado correctamente", "success")
        return redirect(url_for("router_admin.listarUsuariosComercial"))

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al eliminar el comercial", "danger")

    return render_template("admin/listados/listadoComerciales.html")


# Función que maneja la creación de un nuevo usuario comercial, validando el formulario, verificando duplicados, 
# asignando clientes seleccionados y enviando correo de confirmación.
def f_crearUsuarioComercial():

    form = UsuarioComercialForm()

    if form.validate_on_submit():

        try:

            # ── 1. crear comercial ─────────────────────────────
            nuevo = Usuario(
                nombre=form.nombre.data,
                apellido1=form.apellido1.data,
                apellido2=form.apellido2.data,
                email=form.email.data,
                rol=RolEnum.comercial
            )

            nuevo.nombre_usuario = createUsername(
                form.nombre.data,
                form.apellido1.data,
                form.apellido2.data
            )

            nuevo.set_password(form.password.data)

            # ── qr_token único ─────────────────────────────────
            qr_token = uuid.uuid4().hex
            while Usuario.query.filter_by(qr_token=qr_token).first():
                qr_token = uuid.uuid4().hex
            nuevo.qr_token = qr_token

            db.session.add(nuevo)
            db.session.flush()

            # ── 2. asignar clientes seleccionados ──────────────
            if form.clientes.data:

                cliente_ids = [int(c) for c in form.clientes.data]

                clientes = Usuario.query.filter(
                    Usuario.id.in_(cliente_ids),
                    Usuario.rol == RolEnum.cliente,
                    Usuario.comercial_id.is_(None)
                ).all()

                for cliente in clientes:
                    cliente.comercial_id = nuevo.id

            db.session.commit()

            # ── Correo de confirmación ─────────────────────────
            enviado = correo_confirmacion_registro(nuevo)

            if enviado:
                flash("Comercial creado correctamente. Se ha enviado el correo de confirmación.", "success")
            else:
                flash("Comercial creado, pero hubo un error al enviar el correo de confirmación.", "warning")

            return redirect(url_for("router_admin.listarUsuariosComercial"))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al crear el comercial", "danger")

    return render_template(
        "admin/formularios/formComerciales.html",
        form=form
    )

# Función que devuelve la lista de clientes sin comercial asignado que coinciden con un término de búsqueda en formato JSON
# para mostrar en el select2 del formulario de edición/creación de comerciales.    
def f_buscar_clientes_libres():

    term = request.args.get("q", "")

    clientes = Usuario.query.filter(
        Usuario.rol == RolEnum.cliente,
        Usuario.comercial_id.is_(None),
        Usuario.nombre_empresa.ilike(f"%{term}%")
    ).all()

    return jsonify({
        "results": [
            {
                "id": c.id,
                "text": c.nombre_empresa or "-"
            }
            for c in clientes
        ]
    })
    
#/=========================================================\
# Funciones para el panel de administración USUARIO CLIENTE #
#\=========================================================/

# Función que renderiza la página de listado de usuarios clientes con filtros de búsqueda, ordenación y paginación, 
# mostrando también el comercial asignado a cada cliente.
def f_listarUsuariosCliente():
    # --- Filtros desde query string ---
    busqueda  = request.args.get('busqueda', '').strip()
    orden_dir = request.args.get('orden_dir', 'desc')  # 'asc' | 'desc'
    page      = request.args.get('page', 1, type=int)
    formato   = request.args.get('formato', '')

    query = Usuario.query.filter(Usuario.rol == RolEnum.cliente)

    # Filtro: nombre_usuario / cif_empresa / codigo
    # Heurística: >5 chars → busca en CIF además de usuario
    if busqueda:
        if len(busqueda) > 5:
            query = query.filter(
                db.or_(
                    Usuario.nombre_usuario.ilike(f"%{busqueda}%"),
                    Usuario.cif_empresa.ilike(f"%{busqueda}%"),
                )
            )
        else:
            query = query.filter(
                db.or_(
                    Usuario.nombre_usuario.ilike(f"%{busqueda}%"),
                    Usuario.codigo.ilike(f"%{busqueda}%"),
                )
            )

    # Orden por fecha de alta (o ID como fallback)
    if orden_dir == 'asc':
        orden = db.case((Usuario.fecha_alta.isnot(None), Usuario.fecha_alta), else_=None).asc().nullslast() if hasattr(db, 'case') else Usuario.id.asc()
        orden = Usuario.fecha_alta.asc().nullslast() if hasattr(Usuario.fecha_alta, 'nullslast') else Usuario.id.asc()
        orden = Usuario.id.asc()
    else:
        orden = Usuario.id.desc()

    # Orden correcto con SQLAlchemy
    orden = Usuario.id.asc() if orden_dir == 'asc' else Usuario.id.desc()

    paginacion = paginar(query, page=page, per_page=10, orden=orden)

    comerciales = Usuario.query.filter(Usuario.rol == RolEnum.comercial).all()

    usuarios = []
    for u in paginacion.items:
        nombre_comercial = ""
        if u.comercial:
            nombre_comercial = " ".join(filter(None, [
                u.comercial.nombre,
                u.comercial.apellido1,
                u.comercial.apellido2,
            ])).strip()

        usuarios.append({
            "id":             u.id,
            "nombre":         u.nombre or "",
            "apellido1":      u.apellido1 or "",
            "apellido2":      u.apellido2 or "",
            "nombre_completo": " ".join(filter(None, [
                u.nombre, u.apellido1, u.apellido2
            ])).strip(),
            "nombre_usuario": u.nombre_usuario,
            "codigo":         u.codigo or "-",
            "cif_empresa":    u.cif_empresa or "-",
            "nombre_empresa": u.nombre_empresa or "-",
            "email":          u.email,
            "fecha_alta":     u.fecha_alta.strftime("%d/%m/%Y, %H:%M") if u.fecha_alta else "-",
            "comercial":      nombre_comercial or "-",
            "comercial_id":   u.comercial_id or "",
            # ── nuevo ──
            "pernocta":       bool(u.pernocta),
        })

    # ── Respuesta JSON para fetch del botón orden / búsqueda ──
    if formato == 'json':
        html_filas = render_template(
            "admin/listados/_filas_clientes.html",
            usuarios=usuarios,
        )
        return jsonify({"html": html_filas})

    return render_template(
        "admin/listados/listadoClientes.html",
        paginacion=paginacion,
        usuarios=usuarios,
        busqueda=busqueda,
        orden_dir=orden_dir,
        comerciales=comerciales,
    )


# Función que maneja la eliminación de un usuario cliente, verificando su existencia y eliminándolo de la base de datos, incluyendo sus acompañantes asociados.
def f_eliminarUsuarioCliente(id):
    usuario_id = id

    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosCliente"))

    try:
        for acompanante in usuario.acompanantes:
            db.session.delete(acompanante)

        db.session.delete(usuario)
        db.session.commit()

        flash("Usuario eliminado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al eliminar el usuario", "danger")

    return redirect(url_for("router_admin.listarUsuariosCliente"))


# Función que maneja la edición de un usuario cliente, validando los datos, verificando duplicados, 
# actualizando la base de datos y reasignando acompañantes según lo seleccionado en el formulario.
def f_editarUsuarioCliente(id):
    usuario = Usuario.query.get(id)
 
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosCliente"))
 
    # ── datos del formulario ─────────────────────
    nombre            = (request.form.get("nombre")        or "").strip()
    apellido1         = (request.form.get("apellido1")     or "").strip()
    apellido2         = (request.form.get("apellido2")     or "").strip()
    username_form     = (request.form.get("usuario")       or "").strip()
    email             = (request.form.get("email")         or "").strip()
    empresa           = (request.form.get("empresa")       or "").strip()
    cif               = (request.form.get("cif")           or "").strip()
    codigo            = (request.form.get("codigo")        or "").strip()
    fecha_llegada_str = (request.form.get("fecha_llegada") or "").strip()
    comercial_id_str  = (request.form.get("comercial_id")  or "").strip()
    comercial_id      = int(comercial_id_str) if comercial_id_str.isdigit() else None
 
    # ── pernocta del cliente ─────────────────────
    pernocta = request.form.get("pernocta") == "1"
 
    # ── acompañantes ─────────────────────────────
    nombres_acomp   = request.form.getlist("acompanante_nombre")
    apellidos_acomp = request.form.getlist("acompanante_apellido")
 
    # ── validación básica ────────────────────────
    if not nombre or not apellido1 or not email:
        flash("Faltan campos obligatorios", "danger")
        return redirect(url_for("router_admin.listarUsuariosCliente"))
 
    # ── email duplicado ──────────────────────────
    if Usuario.query.filter(
        Usuario.email == email,
        Usuario.id != id
    ).first():
        flash("El email ya está en uso", "danger")
        return redirect(url_for("router_admin.listarUsuariosCliente"))
 
    # ── detectar cambio de nombre ────────────────
    nombre_cambio = (
        nombre    != usuario.nombre    or
        apellido1 != usuario.apellido1 or
        apellido2 != usuario.apellido2
    )
 
    # ── username ─────────────────────────────────
    if nombre_cambio:
        new_username = createUsername(nombre, apellido1, apellido2)
 
        if Usuario.query.filter(
            Usuario.nombre_usuario == new_username,
            Usuario.id != id
        ).first():
            flash("El username generado ya existe", "danger")
            return redirect(url_for("router_admin.listarUsuariosCliente"))
 
        usuario.nombre_usuario = new_username
 
    elif username_form and username_form != usuario.nombre_usuario:
        if Usuario.query.filter(
            Usuario.nombre_usuario == username_form,
            Usuario.id != id
        ).first():
            flash("El nombre de usuario ya existe", "danger")
            return redirect(url_for("router_admin.listarUsuariosCliente"))
 
        usuario.nombre_usuario = username_form
 
    # ── fecha de llegada ─────────────────────────
    if fecha_llegada_str:
        try:
            usuario.fecha_llegada = datetime.strptime(fecha_llegada_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Formato de fecha inválido", "danger")
            return redirect(url_for("router_admin.listarUsuariosCliente"))
    else:
        usuario.fecha_llegada = None
 
    # ── actualizar datos ─────────────────────────
    usuario.nombre        = nombre
    usuario.apellido1     = apellido1
    usuario.apellido2     = apellido2
    usuario.email         = email
    usuario.nombre_empresa = empresa
    usuario.cif_empresa   = cif
    usuario.codigo        = codigo
    usuario.comercial_id  = comercial_id
    usuario.pernocta      = pernocta
 
    # ── acompañantes: borrar existentes y recrear ─
    Acompanante.query.filter_by(usuario_id=usuario.id).delete()
 
    for i, (nombre_ac, apellido_ac) in enumerate(zip(nombres_acomp, apellidos_acomp)):
        nombre_ac   = nombre_ac.strip()
        apellido_ac = apellido_ac.strip()
 
        if not nombre_ac:
            continue
 
        # pernocta individual por índice
        pernocta_ac = request.form.get(f"acompanante_pernocta_{i}") == "1"
 
        qr_token_ac = uuid.uuid4().hex
        while Acompanante.query.filter_by(qr_token=qr_token_ac).first():
            qr_token_ac = uuid.uuid4().hex
 
        db.session.add(Acompanante(
            usuario_id = usuario.id,
            nombre     = nombre_ac,
            apellido   = apellido_ac,
            qr_token   = qr_token_ac,
            pernocta   = pernocta_ac,
        ))
 
    try:
        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
 
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al actualizar el usuario", "danger")
 
    return redirect(url_for("router_admin.listarUsuariosCliente"))


# Función que maneja la creación de un nuevo usuario cliente, validando el formulario, verificando duplicados, 
# creando el usuario y sus acompañantes, asignando comercial y enviando correo de confirmación.
def f_crearUsuarioCliente():

    form = UsuarioClienteForm()
    comerciales = Usuario.query.filter_by(rol=RolEnum.comercial, estado=True).all()
    
    comerciales_js = [{"id": "", "nombre": "— Sin comercial —"}] + [
        {
            "id": c.id,
            "nombre": f"{c.nombre} {c.apellido1} {c.apellido2 or ''}".strip()
        }
        for c in comerciales
    ]

    if form.validate_on_submit():
        
        nombreUsuario = createUsername(
            form.nombre.data, form.apellido1.data, form.apellido2.data
        )

        if Usuario.query.filter_by(email=form.email.data).first():
            flash("El email ya está registrado", "danger")
            return render_template("admin/formularios/formCliente.html", form=form, comerciales_js=comerciales_js)

        if Usuario.query.filter_by(nombre_usuario=nombreUsuario).first():
            flash("El nombre de usuario ya existe", "danger")
            return render_template("admin/formularios/formCliente.html", form=form, comerciales_js=comerciales_js)

        if not comprobarContraseña(form.password.data, form.confirmar_password.data):
            return render_template("admin/formularios/formCliente.html", form=form, comerciales_js=comerciales_js)

        qr_token = uuid.uuid4().hex
        while Usuario.query.filter_by(qr_token=qr_token).first():
            qr_token = uuid.uuid4().hex

        fecha_llegada_raw = form.fecha_llegada.data if hasattr(form, 'fecha_llegada') else None
        fecha_llegada = (
            datetime.fromisoformat(str(fecha_llegada_raw))
            if fecha_llegada_raw else None
        )

        # Los checkboxes de acompañantes se leen antes de crear el usuario
        # porque getlist necesita el request completo
        nombres_ac   = request.form.getlist("acompanante_nombre")
        apellidos_ac = request.form.getlist("acompanante_apellido")
        pernoctas_ac = request.form.getlist("acompanante_pernocta")  # ← nuevo

        usuario = Usuario(
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
            pernocta       = form.pernocta.data  # ← nuevo
        )
        usuario.set_password(form.password.data)

        try:
            db.session.add(usuario)
            db.session.flush()

            for i, (nombre_ac, apellido_ac) in enumerate(zip(nombres_ac, apellidos_ac)):
                nombre_ac   = nombre_ac.strip()
                apellido_ac = apellido_ac.strip()

                if not nombre_ac or not apellido_ac:
                    continue

                qr_token_ac = uuid.uuid4().hex
                while Acompanante.query.filter_by(qr_token=qr_token_ac).first():
                    qr_token_ac = uuid.uuid4().hex

                pernocta_ac = pernoctas_ac[i] == "1" if i < len(pernoctas_ac) else False  # ← nuevo

                db.session.add(Acompanante(
                    usuario_id  = usuario.id,
                    nombre      = nombre_ac,
                    apellido    = apellido_ac,
                    qr_token    = qr_token_ac,
                    pernocta    = pernocta_ac  # ← nuevo
                ))

            db.session.commit()

            acompanantes_creados = Acompanante.query.filter_by(usuario_id=usuario.id).all()
            enviado = correo_confirmacion_registro(usuario, acompanantes_creados)

            if enviado:
                flash("Cliente creado correctamente. Se ha enviado el correo de confirmación.", "success")
            else:
                flash("Cliente creado, pero hubo un error al enviar el correo de confirmación.", "warning")

            return redirect(url_for("router_admin.listarUsuariosCliente"))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al crear el cliente", "danger")

    return render_template("admin/formularios/formCliente.html", form=form, comerciales_js=comerciales_js)


# Función que devuelve los datos de un usuario cliente específico en formato JSON para rellenar el formulario de edición,
#  incluyendo su comercial asignado y acompañantes asociados.
def f_obtenerUsuarioCliente(id):
    """Devuelve JSON para el modal de edición/eliminación."""
    usuario = db.session.get(Usuario, id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id":             usuario.id,
        "nombre":         usuario.nombre         or "",
        "apellido1":      usuario.apellido1      or "",
        "apellido2":      usuario.apellido2      or "",
        "nombre_usuario": usuario.nombre_usuario or "",
        "email":          usuario.email          or "",
        "nombre_empresa": usuario.nombre_empresa or "",
        "cif_empresa":    usuario.cif_empresa    or "",
        "codigo":         usuario.codigo         or "",
        "nombre_completo": " ".join(filter(None, [
            usuario.nombre, usuario.apellido1, usuario.apellido2
        ])).strip()
    })


#/===========================================================\
# Funcion para IMPORTAR PRODUCTOS CSV #
#\===========================================================/    

# Función que genera un token UUID único para el QR del producto, asegurando que no haya colisiones en la base de datos.
def generar_qr_token():
    """Genera un token UUID único para el QR del producto."""
    return str(uuid.uuid4())

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).strip().lower()

def f_descargar_plantilla_productos():
    """
    Genera y descarga un CSV con la plantilla para importar productos.
    Cabeceras: id, nombre, descripcion, precio, imagen_url, qr_token, proveedor
    """
    output = StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    # Fila 1: Cabeceras
    writer.writerow([
        "id",           # Código lógico del producto (no el ID autoincremental)
        "nombre",       # Nombre visible del producto
        "descripcion",  # Descripción textual del producto
        "precio",       # Precio en formato numérico
        "imagen_url",   # URL de la imagen del producto
        "qr_token",     # Identificador único para el QR
        "codigo_proveedor"     # Código del proveedor
    ])


    data = output.getvalue().encode("utf-8")
    output.close()

    return Response(
        data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment;filename=plantilla_productos.csv"
        }
    )
    
def f_importar_productos(archivo):
    if not archivo or not getattr(archivo, "filename", ""):
        return False, ["Debes subir un archivo CSV válido."], 0, []

    if not archivo.filename.lower().endswith(".csv"):
        return False, ["Debes subir un archivo CSV válido."], 0, []

    try:
        df = pd.read_csv(archivo, sep=None, engine="python", encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
    except Exception as e:
        return False, [f"Error leyendo el CSV: {e}"], 0, []

    errores = []
    errores_codigos = []
    insertados = 0

    try:
        proveedores = {
            str(u.codigo).strip(): u.id
            for u in Usuario.query.filter_by(tipo_vc="C").all()
            if u.codigo is not None
        }

        for i, fila in df.iterrows():
            fila_num = i + 2

            codigo = str(fila.get("id", "")).strip()
            nombre = str(fila.get("nombre", "")).strip()
            descripcion = str(fila.get("descripcion", "")).strip() or None
            imagen_url = str(fila.get("imagen_url", "")).strip() or None
            codigo_proveedor = str(fila.get("codigo_proveedor", "")).strip()

            if not codigo:
                errores.append(f"Fila {fila_num}: id vacío.")
                continue

            if not nombre:
                errores.append(f"Fila {fila_num}: nombre vacío.")
                errores_codigos.append(codigo)
                continue

            precio_raw = fila.get("precio")
            try:
                precio = float(precio_raw)
            except (TypeError, ValueError):
                errores.append(f"Fila {fila_num}: precio inválido ({precio_raw!r}).")
                errores_codigos.append(codigo)
                continue

            if not codigo_proveedor:
                errores.append(f"Fila {fila_num}: codigo_proveedor vacío.")
                errores_codigos.append(codigo)
                continue

            proveedor_id = proveedores.get(codigo_proveedor)
            if not proveedor_id:
                errores.append(f"Fila {fila_num}: proveedor no encontrado para codigo_proveedor={codigo_proveedor!r}.")
                errores_codigos.append(codigo)
                continue

            producto_existente = Producto.query.get(codigo)

            if producto_existente:
                producto_existente.nombre = nombre
                producto_existente.descripcion = descripcion
                producto_existente.precio = precio
                producto_existente.imagen_url = imagen_url
                producto_existente.proveedor_id = proveedor_id
            else:
                producto = Producto(
                    id=codigo,
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    imagen_url=imagen_url,
                    qr_token=generar_qr_token(),
                    proveedor_id=proveedor_id,
                )
                db.session.add(producto)

            insertados += 1

        db.session.commit()
        return True, errores, insertados, errores_codigos

    except SQLAlchemyError as e:
        db.session.rollback()
        return False, [f"Error de base de datos: {e}"], insertados, errores_codigos

    except Exception as e:
        db.session.rollback()
        return False, [f"Error inesperado: {e}"], insertados, errores_codigos
    
    
#/===========================================================\
# Funciones para el panel de administración USUARIO PROVEEDOR #
#\===========================================================/ 

# Función que maneja la creación de un nuevo usuario proveedor, validando el formulario, verificando duplicados, creando el usuario y sus acompañantes,
#  asignando datos específicos de proveedor y enviando correo de confirmación.
def f_crearUsuarioProveedor():

    form = UsuarioProveedorForm()

    if form.validate_on_submit():

        nombreUsuario = createUsername(
            form.nombre.data, form.apellido1.data, form.apellido2.data
        )

        if Usuario.query.filter_by(email=form.email.data).first():
            flash("El email ya está registrado", "danger")
            return render_template("admin/formularios/formProveedor.html", form=form)

        if Usuario.query.filter_by(nombre_usuario=nombreUsuario).first():
            flash("El nombre de usuario ya existe", "danger")
            return render_template("admin/formularios/formProveedor.html", form=form)

        if not comprobarContraseña(form.password.data, form.confirmar_password.data):
            return render_template("admin/formularios/formProveedor.html", form=form)

        qr_token = uuid.uuid4().hex
        while Usuario.query.filter_by(qr_token=qr_token).first():
            qr_token = uuid.uuid4().hex

        cena_usuario = form.asiste_cena.data

        nombres_ac   = request.form.getlist("acompanante_nombre")
        apellidos_ac = request.form.getlist("acompanante_apellido")

        usuario = Usuario(
            nombre         = form.nombre.data,
            apellido1      = form.apellido1.data,
            apellido2      = form.apellido2.data,
            nombre_usuario = nombreUsuario,
            email          = form.email.data,
            rol            = RolEnum.proveedor,
            nombre_empresa = (form.nombre_empresa.data or "").strip() or None,
            cif_empresa    = (form.cif_empresa.data    or "").strip() or None,
            codigo         = (form.codigo.data         or "").strip() or None,
            tipo_vc        = TipoVCEnum.C,
            qr_token       = qr_token,
            estado         = True,
            asiste_cena    = cena_usuario
        )
        usuario.set_password(form.password.data)

        try:
            db.session.add(usuario)
            db.session.flush()

            for i, (nombre_ac, apellido_ac) in enumerate(zip(nombres_ac, apellidos_ac)):
                nombre_ac   = nombre_ac.strip()
                apellido_ac = apellido_ac.strip()

                if not nombre_ac or not apellido_ac:
                    continue

                qr_token_ac = uuid.uuid4().hex
                while Acompanante.query.filter_by(qr_token=qr_token_ac).first():
                    qr_token_ac = uuid.uuid4().hex

                asiste_cena_ac = request.form.get(f"acompanante_cena_{i}") == "1"

                db.session.add(Acompanante(
                    usuario_id  = usuario.id,
                    nombre      = nombre_ac,
                    apellido    = apellido_ac,
                    qr_token    = qr_token_ac,
                    asiste_cena = asiste_cena_ac
                ))

            db.session.commit()

            # ── Correo de confirmación con PDF y QR adjunto ───────────
            acompanantes_creados = Acompanante.query.filter_by(usuario_id=usuario.id).all()
            enviado = correo_confirmacion_registro(usuario, acompanantes_creados)

            if enviado:
                flash("Proveedor creado correctamente. Se ha enviado el correo de confirmación.", "success")
            else:
                flash("Proveedor creado, pero hubo un error al enviar el correo de confirmación.", "warning")

            return redirect(url_for("router_admin.listarUsuariosProveedor"))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al crear el proveedor", "danger")

    return render_template("admin/formularios/formProveedor.html", form=form)


# Función que devuelve los datos de un usuario proveedor específico en formato JSON para rellenar el formulario de edición, 
# incluyendo su nombre completo generado a partir de sus campos de nombre y apellidos.
def f_obtenerUsuarioProveedor(id):
    """JSON para modal edición/eliminación."""
    usuario = db.session.get(Usuario, id)

    if not usuario:
        return jsonify({"error": "Proveedor no encontrado"}), 404

    return jsonify({
        "id":             usuario.id,
        "nombre":         usuario.nombre         or "",
        "apellido1":      usuario.apellido1      or "",
        "apellido2":      usuario.apellido2      or "",
        "nombre_usuario": usuario.nombre_usuario or "",
        "email":          usuario.email          or "",
        "codigo":         usuario.codigo         or "",
        "nombre_completo": " ".join(filter(None, [
            usuario.nombre, usuario.apellido1, usuario.apellido2
        ])).strip()
    })



# Función que maneja la edición de un usuario proveedor, validando los datos, verificando duplicados, actualizando la base de datos 
# y reasignando acompañantes según lo seleccionado en el formulario.
def f_editarUsuarioProveedor(id):
    usuario = db.session.get(Usuario, id)

    if not usuario:
        flash("Proveedor no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosProveedor"))

    nombre         = (request.form.get("nombre")   or "").strip()
    apellido1      = (request.form.get("apellido1") or "").strip()
    apellido2      = (request.form.get("apellido2") or "").strip()
    username_form  = (request.form.get("usuario")   or "").strip()
    email          = (request.form.get("email")     or "").strip()
    nombre_empresa = (request.form.get("empresa")   or "").strip()
    cif_empresa    = (request.form.get("cif")       or "").strip()
    codigo         = (request.form.get("codigo")    or "").strip()
    asiste_cena    = "asiste_cena" in request.form

    if not nombre or not apellido1 or not email:
        flash("Faltan campos obligatorios", "danger")
        return redirect(url_for("router_admin.listarUsuariosProveedor"))

    if Usuario.query.filter(
        Usuario.email == email,
        Usuario.id != id
    ).first():
        flash("El email ya está en uso", "danger")
        return redirect(url_for("router_admin.listarUsuariosProveedor"))

    nombre_cambio = (
        nombre    != usuario.nombre    or
        apellido1 != usuario.apellido1 or
        apellido2 != usuario.apellido2
    )

    if nombre_cambio:
        new_username = createUsername(nombre, apellido1, apellido2)
        if Usuario.query.filter(
            Usuario.nombre_usuario == new_username,
            Usuario.id != id
        ).first():
            flash("El username generado ya existe", "danger")
            return redirect(url_for("router_admin.listarUsuariosProveedor"))
        usuario.nombre_usuario = new_username
    elif username_form and username_form != usuario.nombre_usuario:
        if Usuario.query.filter(
            Usuario.nombre_usuario == username_form,
            Usuario.id != id
        ).first():
            flash("El nombre de usuario ya existe", "danger")
            return redirect(url_for("router_admin.listarUsuariosProveedor"))
        usuario.nombre_usuario = username_form

    usuario.nombre         = nombre
    usuario.apellido1      = apellido1
    usuario.apellido2      = apellido2
    usuario.email          = email
    usuario.codigo         = codigo or None
    usuario.asiste_cena    = asiste_cena
    usuario.nombre_empresa = nombre_empresa or None
    usuario.cif_empresa    = cif_empresa    or None

    try:
        # ── Reemplazar acompañantes ──────────────────────────────────
        Acompanante.query.filter_by(usuario_id=id).delete(synchronize_session=False)

        nombres_ac   = request.form.getlist("acompanante_nombre")
        apellidos_ac = request.form.getlist("acompanante_apellido")

        for i, (nombre_ac, apellido_ac) in enumerate(zip(nombres_ac, apellidos_ac)):
            nombre_ac   = nombre_ac.strip()
            apellido_ac = apellido_ac.strip()

            if not nombre_ac or not apellido_ac:
                continue

            qr_token_ac = uuid.uuid4().hex
            while Acompanante.query.filter_by(qr_token=qr_token_ac).first():
                qr_token_ac = uuid.uuid4().hex

            # ── Leer checkbox por índice: acompanante_cena_0, acompanante_cena_1... ──
            asiste_cena_ac = request.form.get(f"acompanante_cena_{i}") == "1"

            db.session.add(Acompanante(
                usuario_id  = id,
                nombre      = nombre_ac,
                apellido    = apellido_ac,
                qr_token    = qr_token_ac,
                asiste_cena = asiste_cena_ac
            ))

        db.session.commit()
        flash("Proveedor actualizado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al actualizar el proveedor", "danger")

    return redirect(url_for("router_admin.listarUsuariosProveedor"))



# Función que maneja la eliminación de un usuario proveedor, verificando su existencia, eliminando en cascada sus productos, solicitudes, pedidos, 
# acompañantes y controles relacionados, y finalmente eliminando el usuario.
def f_eliminarUsuarioProveedor(id):
    proveedor = db.session.get(Usuario, id)

    if not proveedor:
        flash("Proveedor no encontrado", "danger")
        return redirect(url_for("router_admin.listarUsuariosProveedor"))

    if proveedor.rol != RolEnum.proveedor:
        flash("El usuario no es un proveedor", "danger")
        return redirect(url_for("router_admin.listarUsuariosProveedor"))

    try:
        # 1. Detalles de pedido de los productos del proveedor
        productos_ids = [p.id for p in Producto.query.filter_by(proveedor_id=id).all()]
        if productos_ids:
            DetallePedido.query.filter(
                DetallePedido.producto_id.in_(productos_ids)
            ).delete(synchronize_session=False)

        # 2. Productos
        Producto.query.filter_by(proveedor_id=id).delete(synchronize_session=False)

        # 3. Obtener ids de solicitudes ANTES de borrarlas
        solicitudes_ids = [s.id for s in Solicitud.query.filter_by(usuario_id=id).all()]
        if solicitudes_ids:
            DetalleSolicitudMobiliario.query.filter(
                DetalleSolicitudMobiliario.solicitud_id.in_(solicitudes_ids)
            ).delete(synchronize_session=False)
            DetalleSolicitudStand.query.filter(
                DetalleSolicitudStand.solicitud_id.in_(solicitudes_ids)
            ).delete(synchronize_session=False)
            Extra.query.filter(
                Extra.solicitud_id.in_(solicitudes_ids)
            ).delete(synchronize_session=False)
            Mobiliario.query.filter(
                Mobiliario.solicitud_id.in_(solicitudes_ids)
            ).delete(synchronize_session=False)
            Stand.query.filter(
                Stand.solicitud_id.in_(solicitudes_ids)
            ).delete(synchronize_session=False)

        # 4. Solicitudes
        Solicitud.query.filter_by(usuario_id=id).delete(synchronize_session=False)

        # 5. Pedidos
        Pedido.query.filter_by(cliente_id=id).delete(synchronize_session=False)

        # 6. Acompañantes
        Acompanante.query.filter_by(usuario_id=id).delete(synchronize_session=False)

        # 7. Controles de entrada/salida
        ControlES.query.filter_by(usuario_id=id).delete(synchronize_session=False)

        # 8. Presentaciones donde participa
        PresentacionUsuario.query.filter_by(usuario_id=id).delete(synchronize_session=False)

        # 9. Finalmente el usuario
        db.session.delete(proveedor)
        db.session.commit()
        flash("Proveedor eliminado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al eliminar el proveedor", "danger")

    return redirect(url_for("router_admin.listarUsuariosProveedor"))



# Función que maneja la visualización del listado de usuarios proveedores, aplicando filtros de búsqueda, ordenación, paginación y renderizando la plantilla correspondiente.
def f_listarUsuariosProveedor():
    # --- Filtros desde query string ---
    busqueda  = request.args.get('busqueda', '').strip()
    orden_dir = request.args.get('orden_dir', 'desc')
    page      = request.args.get('page', 1, type=int)

    query = Usuario.query.filter(Usuario.rol == RolEnum.proveedor)

    # Filtro: nombre_usuario / cif_empresa / codigo
    # Heurística: >5 chars → busca en CIF además de código
    if busqueda:
        if len(busqueda) > 5:
            query = query.filter(
                db.or_(
                    Usuario.nombre_usuario.ilike(f"%{busqueda}%"),
                    Usuario.cif_empresa.ilike(f"%{busqueda}%"),
                )
            )
        else:
            query = query.filter(
                db.or_(
                    Usuario.nombre_usuario.ilike(f"%{busqueda}%"),
                    Usuario.codigo.ilike(f"%{busqueda}%"),
                )
            )

    orden = Usuario.id.asc() if orden_dir == 'asc' else Usuario.id.desc()

    paginacion = paginar(query, page=page, per_page=10, orden=orden)

    usuarios = []
    for u in paginacion.items:
        nombre_completo = " ".join(filter(None, [
            u.nombre, u.apellido1, u.apellido2
        ])).strip()

        usuarios.append({
            "id":             u.id,
            "nombre_completo": nombre_completo,
            "nombre":         u.nombre     or "",
            "apellido1":      u.apellido1  or "",
            "apellido2":      u.apellido2  or "",
            "nombre_usuario": u.nombre_usuario,
            "email":          u.email,
            "nombre_empresa": u.nombre_empresa or "",
            "cif_empresa":    u.cif_empresa    or "",
            "codigo":         u.codigo or "-",
            "asiste_cena":    u.asiste_cena or False,
            "fecha_alta":     u.fecha_alta.strftime("%d/%m/%Y, %H:%M") if u.fecha_alta else "-"
        })

    return render_template(
        "admin/listados/listadoProveedores.html",
        paginacion=paginacion,
        usuarios=usuarios,
        busqueda=busqueda,
        orden_dir=orden_dir,
    )



# Función que devuelve los acompañantes de un proveedor específico en formato JSON para mostrar en el modal del listado, incluyendo su nombre, apellido y si asisten a la cena.
def f_api_acompanantes_proveedor(proveedor_id):
    """JSON con los acompañantes de un proveedor para el modal del listado."""
 
    acompanantes = Acompanante.query.filter_by(usuario_id=proveedor_id).all()
 
    return jsonify({
        "acompanantes": [
            {
                "nombre":      ac.nombre,
                "apellido":    ac.apellido,
                "asiste_cena": ac.asiste_cena or False,
            }
            for ac in acompanantes
        ]
    })
 


# Función que devuelve los acompañantes de un cliente específico en formato JSON para mostrar en el modal del listado, incluyendo su nombre, apellido y si pernoctan. 
def f_api_acompanantes_cliente(cliente_id):
    """JSON con los acompañantes de un cliente para el modal del listado."""
 
    acompanantes = Acompanante.query.filter_by(usuario_id=cliente_id).all()
 
    return jsonify({
        "acompanantes": [
            {
                "id": ac.id,
                "nombre":   ac.nombre,
                "apellido": ac.apellido,
                "pernocta": ac.pernocta,
            }
            for ac in acompanantes
        ]
    })



# Función que genera un PDF con etiquetas para los proveedores, incluyendo su nombre, empresa, código y un código QR 
# que enlaza a su catálogo de productos, aplicando filtros de búsqueda y ordenación.
def f_generar_etiquetas_proveedores():
    busqueda = request.args.get('busqueda', '').strip()

    query = Usuario.query.filter_by(rol='proveedor')

    if busqueda:
        query = query.filter(
            db.or_(
                Usuario.nombre.ilike(f'%{busqueda}%'),
                Usuario.apellido1.ilike(f'%{busqueda}%'),
                Usuario.apellido2.ilike(f'%{busqueda}%'),
                Usuario.nombre_empresa.ilike(f'%{busqueda}%'),
                Usuario.cif_empresa.ilike(f'%{busqueda}%'),
                Usuario.codigo.ilike(f'%{busqueda}%'),
            )
        )

    proveedores = query.order_by(Usuario.nombre).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    W, H = A4
    PAGE_W = W - 40 * mm  

    # ── Estilos ──
    naranja = colors.HexColor('#F97316')
    gris    = colors.HexColor('#555555')

    estilo_empresa = ParagraphStyle('empresa',
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=gris,
        alignment=1,  # centrado
    )
    estilo_nombre = ParagraphStyle('nombre',
        fontName='Helvetica-Bold',
        fontSize=36,
        leading=42,
        textColor=colors.black,
        alignment=1,
    )
    estilo_escanea = ParagraphStyle('escanea',
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=gris,
        alignment=1,
    )
    estilo_escanea_bold = ParagraphStyle('escanea_bold',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=naranja,
        alignment=1,
    )

    story = []

    for i, proveedor in enumerate(proveedores):
        # Separador de página (excepto la primera)
        if i > 0:
            story.append(PageBreak())

        # ── Espacio superior ──
        story.append(Spacer(1, 25 * mm))

        # ── Nombre empresa (grande) ──
        if proveedor.nombre_empresa:
            story.append(Paragraph(proveedor.nombre_empresa.upper(), estilo_nombre))
            story.append(Spacer(1, 4 * mm))

        # ── Nombre completo (pequeño) ──
        nombre_completo = ' '.join(filter(None, [proveedor.nombre, proveedor.apellido1, proveedor.apellido2]))
        story.append(Paragraph(nombre_completo, estilo_empresa))
        story.append(Spacer(1, 10 * mm))

        # ── Línea separadora naranja ──
        story.append(HRFlowable(
            width='60%',
            thickness=2,
            color=naranja,
            spaceAfter=10 * mm,
            spaceBefore=0,
            hAlign='CENTER',
        ))

        # ── QR ──
        url = url_for('router_index.producto_por_qr',
                      qr_token=proveedor.qr_token, _external=True)
        qr_img = qrcode.make(url)
        qr_buf = io.BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_buf.seek(0)

        QR_SIZE = 80 * mm
        img = Image(qr_buf, width=QR_SIZE, height=QR_SIZE)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 8 * mm))

        # ── Texto CTA ──
        story.append(Paragraph('Escanea para ver mi catálogo de productos', estilo_escanea_bold))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(
            'Apunta la cámara de tu teléfono al código QR y accede directamente a todos mis productos.',
            estilo_escanea,
        ))

        # ── Código del proveedor abajo ──
        if proveedor.codigo:
            story.append(Spacer(1, 6 * mm))
            story.append(Paragraph(
                f'<font color="#F97316"><b>Código:</b></font> {proveedor.codigo}',
                ParagraphStyle('cod', fontName='Helvetica', fontSize=11, alignment=1, textColor=gris)
            ))

    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, mimetype='application/pdf',
                     download_name='etiquetas_proveedores.pdf')



#/===========================================================\
# Funciones para el panel de administración PRODUCTOS #
#\===========================================================/


# Función que maneja la visualización del catálogo de productos en el panel de administración, 
# aplicando filtros de búsqueda, proveedor, paginación y formato de respuesta (HTML o JSON para carga dinámica).
def f_catalogo_productos():
    busqueda     = request.args.get('busqueda', '').strip()
    proveedor_id = request.args.get('proveedor_id', type=int)
    page         = request.args.get('page', 1, type=int)
    per_page     = request.args.get('per_page', 20, type=int)
    formato      = request.args.get('formato', '')

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

    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    has_more   = paginacion.has_next

    if formato == 'json':
        html = render_template('partials/_cards_productos_admin.html', productos=paginacion.items)
        return jsonify({
            'html':     html,
            'has_more': has_more,
            'total':    paginacion.total,
            'loaded':   page * per_page
        })

    return render_template('admin/listados/listadoProductos.html',
        productos    = paginacion.items,
        proveedores  = Usuario.query.filter(Usuario.rol == "proveedor").all(),
        busqueda     = busqueda,
        proveedor_id = proveedor_id,
        has_more     = has_more
    )



# Función que maneja la visualización del detalle de un producto específico en el panel de administración, verificando su existencia y renderizando la plantilla correspondiente.
def f_detalle_producto(producto_id):
    producto = Producto.query.get(producto_id)

    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("router_comercial.catalogo"))

    return render_template("admin/listados/listadoProductos.html", producto=producto)



# Función que maneja la creación de un nuevo producto, validando el formulario, verificando el proveedor, generando un token QR único y guardando el producto en la base de datos.
def f_crear_producto(request):
    if request.method == "GET":
        proveedores = Usuario.query.filter_by(rol=RolEnum.proveedor, estado=True).all()
        return render_template("admin/formularios/formProducto.html", proveedores=proveedores)

    producto_nuevo = Producto(
        nombre       = request.form.get("nombre"),
        id           = request.form.get("codigo"),
        descripcion  = request.form.get("descripcion"),
        precio       = request.form.get("precio", type=float),
        imagen_url   = request.form.get("imagen") or None,
        proveedor_id = request.form.get("proveedor_id", type=int),
        qr_token     = generar_qr_token(),   # ← nuevo
    )
    db.session.add(producto_nuevo)
    db.session.commit()
    flash("Producto creado correctamente.", "success")
    return redirect(url_for("router_admin.catalogo_productos"))



# Función que maneja la edición de un producto existente, verificando su existencia, actualizando sus campos con los datos del formulario, 
# generando un token QR si no tiene y guardando los cambios en la base de datos.
def f_editar_producto(producto_id, request):
    producto = Producto.query.filter_by(id=producto_id).first()

    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("router_admin.catalogo_productos"))

    producto.nombre      = request.form.get("nombre")
    producto.descripcion = request.form.get("descripcion")
    producto.precio      = request.form.get("precio", type=float)
    producto.stock       = request.form.get("stock", type=int)
    producto.imagen_url  = request.form.get("imagen") or None

    if not producto.qr_token:                
        producto.qr_token = generar_qr_token()

    db.session.commit()
    flash("Producto actualizado correctamente.", "success")
    return redirect(url_for("router_admin.catalogo_productos"))



# Función que maneja la eliminación de un producto, verificando su existencia, eliminándolo de la base de datos y redirigiendo al catálogo.
def f_eliminar_producto(producto_id):
    producto = Producto.query.filter_by(id=producto_id).first()

    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("router_admin.catalogo_productos"))  # ← return aquí

    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado correctamente.", "success")
    return redirect(url_for("router_admin.catalogo_productos"))



# Función que genera un PDF con códigos QR para los productos, aplicando filtros de búsqueda y proveedor, y formateando las etiquetas con el nombre, descripción y precio del producto.
def f_generar_pdf_qrs():

    busqueda     = request.args.get('busqueda', '').strip()
    proveedor_id = request.args.get('proveedor_id', type=int)
    ids_param    = request.args.getlist('ids')          # ← NUEVO

    query = Producto.query

    # Si vienen IDs específicos, filtra solo por ellos
    if ids_param:                                        # ← NUEVO bloque
        query = query.filter(Producto.id.in_(ids_param))
    else:
        # Filtros normales solo si no hay selección manual
        if busqueda:
            query = query.filter(
                db.or_(
                    Producto.nombre.ilike(f'%{busqueda}%'),
                    db.cast(Producto.id, db.String).ilike(f'%{busqueda}%')
                )
            )
        if proveedor_id:
            query = query.filter_by(proveedor_id=proveedor_id)

    productos = query.all()

    buffer = io.BytesIO()

    ETIQUETA_W = 97  * mm
    ETIQUETA_H = 42.4 * mm
    COLS       = 2
    PAGE_W     = ETIQUETA_W * COLS
    PAGE_H     = A4[1]  # altura A4 para que quepan varias filas por página

    doc = SimpleDocTemplate(
        buffer,
        pagesize  = (PAGE_W, PAGE_H),
        rightMargin  = 0,
        leftMargin   = 0,
        topMargin    = 0,
        bottomMargin = 0,
    )

    # ── Estilos ──────────────────────────────────────────
    styles = getSampleStyleSheet()

    estilo_codigo = ParagraphStyle('codigo',
        fontName  = 'Helvetica-Bold',
        fontSize  = 7,
        leading   = 9,
        textColor = colors.HexColor('#333333'),
    )
    estilo_nombre = ParagraphStyle('nombre',
        fontName  = 'Helvetica-Bold',
        fontSize  = 9,
        leading   = 11,
        textColor = colors.black,
    )
    estilo_desc = ParagraphStyle('desc',
        fontName  = 'Helvetica',
        fontSize  = 7,
        leading   = 9,
        textColor = colors.HexColor('#555555'),
    )
    estilo_precio = ParagraphStyle('precio',
        fontName  = 'Helvetica-Bold',
        fontSize  = 11,
        leading   = 13,
        textColor = colors.HexColor('#E87722'),  # naranja dsg
    )

    # ── Construir etiquetas ───────────────────────────────
    QR_SIZE    = 34 * mm
    TEXT_W     = ETIQUETA_W - QR_SIZE - 6 * mm  # espacio para texto
    PADDING    = 2 * mm

    def hacer_etiqueta(producto):
        # QR
        url       = url_for('router_index.producto_por_qr', qr_token=producto.qr_token, _external=True)
        qr_img    = qrcode.make(url)
        qr_buf    = io.BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_buf.seek(0)
        img = Image(qr_buf, width=QR_SIZE, height=QR_SIZE)

        # Texto
        descripcion_corta = (producto.descripcion or "")[:80]
        precio_fmt        = f"€ {producto.precio:,.2f}"

        texto = Table([
            [Paragraph(f"#{producto.id}", estilo_codigo)],
            [Paragraph(producto.nombre,   estilo_nombre)],
            [Paragraph(descripcion_corta, estilo_desc)],
            [Spacer(1, 2*mm)],
            [Paragraph(precio_fmt,        estilo_precio)],
        ], colWidths=[TEXT_W])

        texto.setStyle(TableStyle([
            ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',(0, 0), (-1, -1), 0),
            ('TOPPADDING',  (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING',(0,0), (-1, -1), 1),
        ]))

        # Etiqueta: [texto | qr]
        etiqueta = Table(
            [[texto, img]],
            colWidths = [TEXT_W + 4*mm, QR_SIZE + PADDING],
            rowHeights= [ETIQUETA_H - 2*mm],
        )
        etiqueta.setStyle(TableStyle([
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 3*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2*mm),
            ('TOPPADDING',   (0, 0), (-1, -1), 2*mm),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 2*mm),
            ('BOX',          (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        return etiqueta

    # ── Agrupar en filas de 2 columnas ───────────────────
    etiquetas = [hacer_etiqueta(p) for p in productos]

    # Rellenar si es impar
    if len(etiquetas) % COLS != 0:
        etiquetas.append("")

    table_data = []
    for i in range(0, len(etiquetas), COLS):
        table_data.append(etiquetas[i:i+COLS])

    tabla_final = Table(
        table_data,
        colWidths = [ETIQUETA_W] * COLS,
        rowHeights= [ETIQUETA_H] * len(table_data),
    )
    tabla_final.setStyle(TableStyle([
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',(0, 0), (-1, -1), 0),
        ('TOPPADDING',  (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0,0), (-1, -1), 0),
    ]))

    doc.build([tabla_final])
    buffer.seek(0)

    return send_file(buffer, mimetype="application/pdf", download_name="etiquetas_productos.pdf")



#/===========================================================\
# Funciones para el panel de administración PEDIDOS #
#\===========================================================/


# Función que maneja la visualización del listado de pedidos en el panel de administración, aplicando filtros de estado, cliente, fecha y paginación,
def f_listar_pedidos():
    """Lista pedidos con filtros — ahora también pasa productos para el modal de edición."""
 
    estado     = request.args.get("estado")
    cliente_id = request.args.get("cliente_id", type=int)
    fecha_ini  = request.args.get("fecha_ini")
    fecha_fin  = request.args.get("fecha_fin")
    page       = request.args.get("page", 1, type=int)
 
    query = Pedido.query.join(Usuario, Pedido.cliente_id == Usuario.id)
 
    if estado:
        query = query.filter(Pedido.estado == estado)
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if fecha_ini:
        query = query.filter(Pedido.fecha_pedido >= datetime.fromisoformat(fecha_ini))
    if fecha_fin:
        query = query.filter(Pedido.fecha_pedido <= datetime.fromisoformat(fecha_fin))
 
    paginacion = paginar(query, page=page, per_page=15, orden=Pedido.fecha_pedido.desc())
    clientes   = Usuario.query.filter_by(rol=RolEnum.cliente, estado=True).order_by(Usuario.nombre).all()
 
    # Productos serializados para el modal de edición inline
    productos_raw = Producto.query.order_by(Producto.nombre).all()
    productos_json = [
        {
            "id":        p.id,
            "nombre":    p.nombre,
            "precio":    float(p.precio),
            "proveedor": (p.proveedor.nombre_empresa or p.proveedor.nombre) if p.proveedor else "",
        }
        for p in productos_raw
    ]
 
    return render_template(
        "admin/listados/listadoPedidos.html",
        paginacion    = paginacion,
        pedidos       = paginacion.items,
        clientes      = clientes,
        filtros       = request.args,
        productos     = productos_json,
    )


# Función que maneja la edición de un pedido existente por parte del administrador, verificando su existencia, validando los datos del formulario, 
# reemplazando las líneas del pedido y actualizando el total, observaciones y estado según los datos recibidos.
def f_editar_pedido_admin(pedido_id):
    """Procesa el formulario de edición del pedido (POST) — versión admin."""
 
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))
 
    if pedido.estado == "cancelado":
        flash("No se puede editar un pedido cancelado.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))
 
    # ── Parsear líneas ───────────────────────────────────────────
    try:
        lineas_data = json.loads(request.form.get("lineas_json", "[]"))
    except (ValueError, TypeError):
        flash("Datos de líneas inválidos.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))
 
    if not lineas_data:
        flash("El pedido debe tener al menos una línea.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))
 
    # ── Validar productos ────────────────────────────────────────
    ids_producto  = [int(l["producto_id"]) for l in lineas_data]
    productos_map = {
        p.id: p
        for p in Producto.query.filter(Producto.id.in_(ids_producto)).all()
    }
 
    if len(productos_map) != len(set(ids_producto)):
        flash("Uno o más productos no existen.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))
 
    for l in lineas_data:
        if int(l.get("cantidad", 0)) < 1:
            flash("Todas las cantidades deben ser mayor que 0.", "danger")
            return redirect(url_for("router_admin.listar_pedidos"))
 
    # ── Reemplazar líneas ────────────────────────────────────────
    DetallePedido.query.filter_by(pedido_id=pedido_id).delete()
 
    total = 0.0
    for l in lineas_data:
        producto = productos_map[int(l["producto_id"])]
        cantidad = int(l["cantidad"])
        precio   = float(producto.precio)
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
 
    # El admin también puede cambiar el estado desde el modal de edición
    nuevo_estado = request.form.get("estado")
    if nuevo_estado in ("pendiente", "confirmado", "cancelado"):
        pedido.estado = nuevo_estado
 
    db.session.commit()
 
    flash(f"Pedido #{pedido_id} actualizado correctamente.", "success")
    return redirect(url_for("router_admin.listar_pedidos"))
 


# Función que maneja la visualización del detalle de un pedido específico en el panel de administración, 
# verificando su existencia y renderizando la plantilla correspondiente con los datos del pedido.
def f_detalle_pedido_admin(pedido_id):
    pedido = Pedido.query.get(pedido_id)

    if not pedido:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))

    return render_template(
        "admin/listados/listadoPedidos.html",
        pedido=pedido,
        filtros={}  
    )



# Función que maneja el cambio de estado de un pedido por parte del administrador, verificando su existencia, validando el nuevo estado y actualizando el pedido en la base de datos.
def f_cambiar_estado_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))

    nuevo_estado = request.form.get("estado")
    estados_validos = ["pendiente", "confirmado", "cancelado"]

    if nuevo_estado not in estados_validos:
        flash("Estado no válido.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))

    pedido.estado = nuevo_estado

    try:
        db.session.commit()
        flash(f"Pedido #{pedido_id} marcado como {nuevo_estado}.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al cambiar el estado.", "danger")
        print(e)

    return redirect(url_for("router_admin.listar_pedidos"))



# Función que maneja la eliminación de un pedido por parte del administrador, verificando su existencia, eliminándolo de la base de datos y redirigiendo al listado de pedidos.
def f_eliminar_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("router_admin.listar_pedidos"))

    try:
        db.session.delete(pedido)
        db.session.commit()
        flash(f"Pedido #{pedido_id} eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar el pedido.", "danger")
        print(e)

    return redirect(url_for("router_admin.listar_pedidos"))



# Función que maneja la exportación de pedidos a un archivo CSV, aplicando filtros de estado, cliente y fecha, 
# y formateando los datos con encabezados y codificación UTF-8.
def f_exportar_pedidos_csv():
    estado     = request.args.get("estado")
    cliente_id = request.args.get("cliente_id", type=int)
    fecha_ini  = request.args.get("fecha_ini")
    fecha_fin  = request.args.get("fecha_fin")

    query = Pedido.query.join(Usuario, Pedido.cliente_id == Usuario.id)

    if estado:
        query = query.filter(Pedido.estado == estado)

    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)

    try:
        if fecha_ini:
            fecha_ini_dt = datetime.fromisoformat(fecha_ini)
            query = query.filter(Pedido.fecha_pedido >= fecha_ini_dt)

        if fecha_fin:
            fecha_fin_dt = datetime.fromisoformat(fecha_fin)
            query = query.filter(Pedido.fecha_pedido <= fecha_fin_dt)
    except ValueError:
        pass

    pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # encabezado
    writer.writerow([
        "ID Pedido", "Cliente", "Email", "Empresa",
        "Fecha", "Estado", "Total", "Observaciones"
    ])

    # datos
    for p in pedidos:
        cliente = p.cliente

        writer.writerow([
            p.id,
            f"{cliente.nombre or ''} {cliente.apellido1 or ''}".strip(),
            cliente.email or "",
            cliente.nombre_empresa or "",
            p.fecha_pedido.strftime("%d/%m/%Y %H:%M") if p.fecha_pedido else "",
            p.estado or "",
            f"{float(p.total):.2f}" if p.total is not None else "0.00",
            p.observaciones or ""
        ])

    csv_data = "\ufeff" + output.getvalue()

    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=pedidos.csv"
        }
    )



# Función que maneja la visualización de los detalles de un pedido específico en formato JSON, 
# incluyendo información del cliente, fecha, total, estado, observaciones y las líneas del pedido con sus respectivos productos.
def f_pedido_json(pedido_id):
    p = Pedido.query.get_or_404(pedido_id)

    return jsonify({
        'id': p.id,

        'cliente_nombre': f"{p.cliente.nombre or ''} {p.cliente.apellido1 or ''}".strip(),
        'cliente_email': p.cliente.email or "",
        'empresa': p.cliente.nombre_empresa or "",

        'fecha': p.fecha_pedido.strftime('%d/%m/%Y %H:%M') if p.fecha_pedido else "",

        'total': f"{float(p.total):.2f}" if p.total is not None else "0.00",
        'estado': p.estado or "",
        'observaciones': p.observaciones or "",

        'lineas': [
            {
                'producto_id': l.producto.id if l.producto else None,
                'producto': l.producto.nombre if l.producto else "",
                'cantidad': l.cantidad or 0,
                'precio_unitario': f"{float(l.precio_unitario):.2f}" if l.precio_unitario else "0.00",
                'subtotal': f"{float(l.subtotal):.2f}" if l.subtotal else "0.00"
            }
            for l in p.detalles
        ]
    })



#/===========================================================\
# Funciones para el panel de administración SOLICITUDES #
#\===========================================================/


# Función que maneja la visualización del listado de solicitudes en el panel de administración, mostrando todas las solicitudes 
# con sus detalles asociados y los extras disponibles.
def f_listado_solicitudes():
    """Muestra una página con TODAS las solicitudes y extras"""

    extras = Extra.query.order_by(Extra.id.desc()).all()

    solicitudes = (
        Solicitud.query
        .options(
            joinedload(Solicitud.usuario),
            subqueryload(Solicitud.detalles_stand)
                .joinedload(DetalleSolicitudStand.stand),
            subqueryload(Solicitud.detalles_mobiliario)
                .joinedload(DetalleSolicitudMobiliario.mobiliario),
            subqueryload(Solicitud.extras),
        )
        .order_by(Solicitud.fecha_solicitud.desc())
        .all()
    )

    return render_template(
        "admin/listados/listadoSolicitudes.html",
        solicitudes=solicitudes,
        extras=extras
    )
 


# Función que maneja el cambio de estado de una solicitud por parte del administrador, verificando su existencia, validando el nuevo estado,
#  actualizando la solicitud y opcionalmente los stands asociados, y registrando el historial de cambios. 
def f_cambiar_estado_solicitud(solicitud_id):
    """Cambia el estado de una solicitud y opcionalmente el estado de los stands asociados"""

    solicitud = Solicitud.query.get_or_404(solicitud_id)

    nuevo_estado = request.form.get("estado")
    accion_stand = request.form.get("accion_stand")

    estados_validos = {"pendiente", "confirmada", "rechazada", "pre_reservado"}

    if nuevo_estado not in estados_validos:
        flash("Estado no válido.", "danger")
        return redirect(url_for("router_admin.listado_solicitudes"))

    estado_anterior = solicitud.estado

    # =====================================
    # ACCIÓN ADMIN (ACEPTAR / RECHAZAR)
    # =====================================
    if nuevo_estado == "confirmada":
        accion_admin = "aceptar_solicitud_admin"
        texto_accion = "ACEPTACIÓN"
    elif nuevo_estado == "rechazada":
        accion_admin = "rechazar_solicitud_admin"
        texto_accion = "RECHAZO"
    else:
        accion_admin = "cambio_estado_solicitud_admin"
        texto_accion = "CAMBIO DE ESTADO"

    # =====================================
    # HISTORIAL: SOLICITUD
    # =====================================
    historial_solicitud = registrar_historial(
        stand_id=None,
        accion=accion_admin,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        solicitud_origen=solicitud.id,
        usuario_origen=None,
        usuario_destino=solicitud.usuario_id,
        observacion=f"{texto_accion} de solicitud desde panel de administración"
    )
    db.session.add(historial_solicitud)

    solicitud.estado = nuevo_estado


    # =====================================
    # CAMBIO DE STANDS (SI APLICA)
    # =====================================
    if accion_stand in {"ocupado", "disponible"}:

        nuevo_estado_stand = EstadoStandEnum[accion_stand]

        numeros_stands = [
            detalle.stand_id for detalle in solicitud.detalles_stand
        ]

        stands = Stand.query.filter(
            Stand.numero_stand.in_(numeros_stands)
        ).all()

        for stand in stands:

            estado_stand_anterior = stand.estado.value

            # =====================================
            # HISTORIAL: STAND
            # =====================================
            historial_stand = registrar_historial(
                stand_id=stand.numero_stand,
                accion=f"{accion_admin}_stand",
                estado_anterior=estado_stand_anterior,
                estado_nuevo=nuevo_estado_stand.value,
                solicitud_origen=solicitud.id,
                usuario_origen=None,
                usuario_destino=solicitud.usuario_id,
                observacion=f"{texto_accion} de solicitud desde admin (afecta a stand)"
            )
            db.session.add(historial_stand)

            stand.estado = nuevo_estado_stand
            if accion_stand == "disponible":
                stand.solicitud_id = None

    db.session.commit()

    flash(f"Solicitud actualizada a '{nuevo_estado}'.", "success")
    return redirect(url_for("router_admin.listado_solicitudes"))



# Función que maneja la actualización del precio de un extra asociado a una solicitud, verificando su existencia, validando el nuevo precio y guardando los cambios en la base de datos.
def f_guardar_precio_extra(extra_id):
    """Guarda o actualiza el precio de un extra"""

    extra  = Extra.query.get_or_404(extra_id)
    precio = request.form.get("precio")
    
    try:
        extra.precio = float(precio)
        db.session.commit()
        flash("Precio del extra guardado.", "success")
    except (ValueError, TypeError):
        flash("Precio no válido.", "danger")
 
    return redirect(url_for("router_admin.listado_solicitudes"))



# Función que maneja la aplicación de un descuento global a todas las solicitudes de un mismo usuario, calculando el precio final con el descuento aplicado
#  y guardando los cambios en la base de datos.
def f_aplica_descuento(solicitud_id):
    """Aplica un descuento global y lo persiste en BD"""

    solicitud = Solicitud.query.get_or_404(solicitud_id)

    try:
        descuento = float(request.form.get("descuento", 0))
        if descuento < 0:
            descuento = 0.0
    except (ValueError, TypeError):
        descuento = 0.0

    # Todas las solicitudes del usuario
    todas = Solicitud.query.filter_by(
        usuario_id=solicitud.usuario_id
    ).all()

    total_bruto = 0

    for s in todas:

        total_bruto += sum(
            float(d.precio_total or 0)
            for d in s.detalles_stand
        )

        total_bruto += sum(
            float(d.precio_total or 0)
            for d in s.detalles_mobiliario
        )

        total_bruto += sum(
            float(e.precio or 0) * e.cantidad
            for e in s.extras
        )

    precio_final = round(
        max(total_bruto - descuento, 0),
        2
    )

    # =====================================
    # GUARDAR EN TODAS LAS SOLICITUDES
    # =====================================

    for s in todas:

        s.descuento = round(descuento, 2)
        s.precio_final = precio_final

    db.session.commit()

    flash("Descuento aplicado correctamente.", "success")

    return redirect(
        url_for("router_admin.listado_solicitudes")
    )



# Función que maneja la visualización de un listado de solicitudes agrupadas por usuario, mostrando el precio bruto, 
# descuento aplicado y precio final para cada usuario, y permitiendo filtrar por nombre del proveedor.
def f_listado_descuento():
    proveedor_filtro = request.args.get("proveedor", "").strip().lower()

    usuarios_con_confirmada = (
        db.session.query(Solicitud.usuario_id)
        .filter(
            Solicitud.estado.in_(["confirmada", "asignado_por_admin"])
        )
        .filter(
            Solicitud.usuario_id.in_(
                db.session.query(Solicitud.usuario_id).filter(
                    Solicitud.estado.in_(["confirmada", "asignado_por_admin"]),
                    Solicitud.detalles_stand.any()
                )
            )
        )
        .distinct()
        .all()
    )

    usuarios_ids = [u.usuario_id for u in usuarios_con_confirmada]
    solicitudes_agrupadas = []

    for usuario_id in usuarios_ids:
        todas = Solicitud.query.filter_by(usuario_id=usuario_id).all()

        confirmadas = [
            s for s in todas
            if s.estado in ["confirmada", "asignado_por_admin"]
        ]

        stands = []
        mob = []
        extras = []

        for s in todas:
            mob += s.detalles_mobiliario
            extras += s.extras

        for s in confirmadas:
            stands += s.detalles_stand

        total_stands = sum(float(d.precio_total or 0) for d in stands)
        total_mob = sum(float(d.precio_total or 0) for d in mob)
        total_extras = sum(float(e.precio or 0) * e.cantidad for e in extras)

        total_bruto = total_stands + total_mob + total_extras
        s_principal = todas[0]

        descuento = float(s_principal.descuento or 0)
        precio_final = max(total_bruto - descuento, 0)

        s_principal._stands = stands
        s_principal._mob = mob
        s_principal._extras = extras
        s_principal._total_bruto = total_bruto
        s_principal._descuento = descuento
        s_principal.precio_final = round(precio_final, 2)

        solicitudes_agrupadas.append(s_principal)

    if proveedor_filtro:
        solicitudes_agrupadas = [
            s for s in solicitudes_agrupadas
            if proveedor_filtro in (s.usuario.nombre_empresa or "").lower()
            or proveedor_filtro in (s.usuario.nombre or "").lower()
            or proveedor_filtro in (s.usuario.apellido1 or "").lower()
            or proveedor_filtro in (s.usuario.nombre_usuario or "").lower()
        ]

    return render_template(
        "admin/listados/listadoSolicitudFinal.html",
        solicitudes=solicitudes_agrupadas
    )

#CARDS USUARIO ALEATORIO

ROLES_COLORES = {
    "Comercial":  "#F18A1F",   # Amarillo
    "Control":    "#C0392B",    # Rojo
    "Cliente":    "#63B66B",    # Verde
    "Proveedor":  "#74CBF3",    # Azul oscuro
    "Invitado":   "#B894C4",    # Morado
    "Medios/Prensa":"#99929A",  # Gris
}



# Función que maneja la creación de una tarjeta de rol para un usuario aleatorio, validando los datos del formulario, 
# generando un token QR y renderizando la plantilla correspondiente con el resultado.
ROL_CFG = {
    "proveedor": {
        "badge_rol": "EXPOSITOR",
        "color": "#74CBF3",
        "fields": ["nombre", "empresa"],
    },
    "invitado": {
        "badge_rol": "INVITADO",
        "color": "#B894C4",
        "fields": ["nombre"],
    },
    "medios/prensa": {
        "badge_rol": "MEDIOS / PRENSA",
        "color": "#99929A",
        "fields": ["nombre", "empresa"],
    },
    "comercial": {
        "badge_rol": "COMERCIAL",
        "color": "#F18A1F",
        "fields": ["nombre", "cargo", "empresa"],
    },
    "cliente": {
        "badge_rol": "VISITANTE",
        "color": "#63B66B",
        "fields": ["nombre", "codigo_cliente", "empresa"],
    },
}

ROL_CFG = {
    "proveedor": {
        "badge_rol": "EXPOSITOR",
        "color": "#4DC8ED",
        "fields": ["nombre", "empresa"],
    },
    "invitado": {
        "badge_rol": "INVITADO",
        "color": "#B894C4",
        "fields": ["nombre"],
    },
    "medios/prensa": {
        "badge_rol": "MEDIOS / PRENSA",
        "color": "#99929A",
        "fields": ["nombre", "empresa"],
    },
    "comercial": {
        "badge_rol": "COMERCIAL",
        "color": "#F18A1F",
        "fields": ["nombre", "cargo", "empresa"],
    },
    "cliente": {
        "badge_rol": "VISITANTE",
        "color": "#63B66B",
        "fields": ["nombre", "codigo_cliente", "empresa"],
    },
    "control": {
        "badge_rol": "CONTROL",
        "color": "#E53935",
        "fields": ["nombre", "cargo", "empresa"],
    },
}


def f_crear_tarjeta_rol():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        cargo = (request.form.get("cargo") or "").strip()
        empresa = (request.form.get("empresa") or "").strip()
        codigo_cliente = (request.form.get("codigo_cliente") or "").strip()
        rol = (request.form.get("rol") or "").strip()

        cfg = ROL_CFG.get(rol)
        errores = []

        if not cfg:
            errores.append("Selecciona un rol válido.")
        if cfg and "nombre" in cfg["fields"] and not nombre:
            errores.append("El nombre es obligatorio.")
        if cfg and "empresa" in cfg["fields"] and not empresa:
            errores.append("La empresa es obligatoria.")
        if cfg and "cargo" in cfg["fields"] and not cargo:
            errores.append("El cargo es obligatorio.")
        if cfg and "codigo_cliente" in cfg["fields"] and not codigo_cliente:
            errores.append("El código de cliente es obligatorio.")

        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template(
                "admin/formularios/formUsuarioAleatorio.html",
                qr_base64=None,
                form=dict(
                    nombre=nombre,
                    cargo=cargo,
                    empresa=empresa,
                    codigo_cliente=codigo_cliente,
                    rol=rol,
                    color=cfg["color"] if cfg else "#E05C2A",
                    badge_rol=cfg["badge_rol"] if cfg else rol,
                ),
                roles=ROL_CFG,
            )

        token_qr = uuid.uuid4().hex
        try:
            qr_base64 = generar_qr_imagen_64(token_qr)
        except Exception as exc:
            flash(f"Error al generar el QR: {exc}", "warning")
            qr_base64 = None

        flash("Acreditación generada correctamente.", "success")
        return redirect(url_for("router_admin.crear_tarjeta_rol"))

    return render_template(
        "admin/formularios/formUsuarioAleatorio.html",
        qr_base64=None,
        form={},
        roles=ROL_CFG,
    )

#/===========================================================\
# Funciones para PRESENTACIONES                              #
#\===========================================================/
 

# Función que maneja la visualización del listado de presentaciones en el panel de administración, aplicando paginación 
# y mostrando detalles como tema, descripción, fecha, aforo, inscritos, plazas libres y organizador.
def f_listar_presentaciones():
    page = request.args.get("page", 1, type=int)
 
    query = Presentacion.query.order_by(Presentacion.fecha_hora.asc())
 
    paginacion = paginar(query, page=page, per_page=10, orden=Presentacion.fecha_hora.asc())
 
    presentaciones = []
    for p in paginacion.items:
        inscritos = p.presentacion_usuarios.count()
        presentaciones.append({
            "id":          p.id,
            "tema":        p.tema,
            "descripcion": p.descripcion or "",
            "fecha_hora":  p.fecha_hora.strftime("%d/%m/%Y %H:%M"),
            "aforo":       p.aforo,
            "inscritos":   inscritos,
            "plazas_libres": max(p.aforo - inscritos, 0),
            "organizador": p.organizador if p.organizador else "-",
        })  
 
    return render_template(
        "admin/listados/listadoPresentaciones.html",
        paginacion=paginacion,
        presentaciones=presentaciones,
    )
 


# Función que maneja la creación de una nueva presentación por parte del administrador, validando los datos del formulario, 
def f_crear_presentacion():
    if request.method == "POST":
        tema        = (request.form.get("tema")        or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        fecha_hora_raw = (request.form.get("fecha_hora") or "").strip()
        aforo_raw   = request.form.get("aforo", "0").strip()
        organizador = request.form.get("org").strip()
 
        errores = []
        if not tema:
            errores.append("El tema es obligatorio.")
        if not fecha_hora_raw:
            errores.append("La fecha y hora son obligatorias.")
        if not organizador:
            errores.append("Debes asignar un organizador.")
 
        try:
            aforo = int(aforo_raw)
            if aforo < 1:
                raise ValueError
        except ValueError:
            errores.append("El aforo debe ser un número mayor que 0.")
            aforo = 0
 
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora_raw)
        except (ValueError, TypeError):
            errores.append("Formato de fecha/hora no válido.")
            fecha_hora = None
 
        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template(
                "admin/formularios/formPresentacion.html",
                form=request.form,
                accion="crear",
            )
 
        nueva = Presentacion(
            tema=tema,
            descripcion=descripcion or None,
            fecha_hora=fecha_hora,
            aforo=aforo,
            organizador=organizador,
            usuario_id=current_user.id,
        )
 
        try:
            db.session.add(nueva)
            db.session.commit()
            flash("Presentación creada correctamente.", "success")
            return redirect(url_for("router_admin.listar_presentaciones"))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al crear la presentación.", "danger")
 
   
    return render_template(
        "admin/formularios/formPresentacion.html",
        form={},
        accion="crear",
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR']
    )
 
 
# Función que maneja la edición de una presentación existente por parte del administrador, verificando su existencia, validando los datos del formulario. 
def f_editar_presentacion(presentacion_id):
    presentacion = Presentacion.query.get_or_404(presentacion_id)
 
    if request.method == "POST":
        tema           = (request.form.get("tema")        or "").strip()
        descripcion    = (request.form.get("descripcion") or "").strip()
        fecha_hora_raw = (request.form.get("fecha_hora")  or "").strip()
        aforo_raw      = request.form.get("aforo", "0").strip()
        organizador = request.form.get("org").strip()
 
        errores = []
        if not tema:
            errores.append("El tema es obligatorio.")
        if not fecha_hora_raw:
            errores.append("La fecha y hora son obligatorias.")
        if not organizador:
            errores.append("Debes asignar un organizador.")
 
        try:
            aforo = int(aforo_raw)
            if aforo < 1:
                raise ValueError
        except ValueError:
            errores.append("El aforo debe ser un número mayor que 0.")
            aforo = presentacion.aforo
 
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora_raw)
        except (ValueError, TypeError):
            errores.append("Formato de fecha/hora no válido.")
            fecha_hora = presentacion.fecha_hora
 
        # No permitir aforo menor que inscritos actuales
        inscritos = presentacion.presentacion_usuarios.count()
        if aforo < inscritos:
            errores.append(f"El aforo no puede ser menor que los inscritos actuales ({inscritos}).")
 
        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template(
                "admin/formularios/formPresentacion.html",
                form=request.form,
                presentacion=presentacion,
                accion="editar",
            )
 
        presentacion.tema        = tema
        presentacion.descripcion = descripcion or None
        presentacion.fecha_hora  = fecha_hora
        presentacion.aforo       = aforo
        presentacion.organizador = organizador
        presentacion.usuario_id  = current_user.id
 
        try:
            db.session.commit()
            flash("Presentación actualizada correctamente.", "success")
            return redirect(url_for("router_admin.listar_presentaciones"))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al actualizar la presentación.", "danger")
 
    return render_template(
        "admin/formularios/formPresentacion.html",
        form={},
        presentacion=presentacion,
        accion="editar",
    )
 
# Función que maneja la eliminación de una presentación por parte del administrador, verificando su existencia, eliminándola de la base de datos y redirigiendo al listado de presentaciones.
def f_eliminar_presentacion(presentacion_id):
    presentacion = Presentacion.query.get_or_404(presentacion_id)
 
    try:
        db.session.delete(presentacion)
        db.session.commit()
        flash("Presentación eliminada correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al eliminar la presentación.", "danger")
 
    return redirect(url_for("router_admin.listar_presentaciones"))
 

# Función que maneja la visualización del listado de inscritos a una presentación específica en formato JSON, 
# incluyendo detalles como nombre completo, empresa y email de cada inscrito. 
def f_api_inscritos_presentacion(presentacion_id):
    """JSON con el listado de clientes inscritos — para el modal del listado."""
    presentacion = Presentacion.query.get_or_404(presentacion_id)
 
    inscritos = []
    for pu in presentacion.presentacion_usuarios:
        u = pu.usuario
        inscritos.append({
            "id":             u.id,
            "nombre_completo": " ".join(filter(None, [u.nombre, u.apellido1, u.apellido2])),
            "empresa":        u.nombre_empresa or "-",
            "email":          u.email or "-",
        })
 
    return jsonify({
        "tema":      presentacion.tema,
        "inscritos": inscritos,
        "total":     len(inscritos),
        "aforo":     presentacion.aforo,
    })
 
# Función que maneja la visualización de los datos de una presentación específica en formato JSON, incluyendo detalles 
# como tema, descripción, fecha, aforo y organizador, para rellenar el modal de edición. 
def f_api_presentacion_json(presentacion_id):
    """JSON con datos de una presentación — para rellenar el modal de edición."""
    p = Presentacion.query.get_or_404(presentacion_id)
    return jsonify({
        "id":          p.id,
        "tema":        p.tema,
        "descripcion": p.descripcion or "",
        "fecha_hora":  p.fecha_hora.strftime("%Y-%m-%dT%H:%M"),
        "aforo":       p.aforo,
        "usuario_id":  p.usuario_id,
        "rolUsuario":  p.usuario.rol if p.usuario else None
    })

 

#/===========================================================\
# Funciones para MOBILIARIO                              #
#\===========================================================/

# Función que maneja la visualización del listado de mobiliario en el panel de administración, mostrando todos los muebles disponibles 
# con sus detalles como referencia, descripción, stock y precio.
def f_listar_mobiliario():
    mobiliario = Mobiliario.query.order_by(Mobiliario.referencia.asc()).all()
    return render_template(
        "admin/listados/listadoMobiliario.html",
        mobiliario=mobiliario,
    )
 
 
# Función que maneja la creación de un nuevo mobiliario por parte del administrador, validando los datos del formulario, 
def f_crear_mobiliario():
    if request.method == "POST":
        referencia  = (request.form.get("referencia")  or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        stock_raw   = request.form.get("stock",  "0").strip()
        precio_raw  = request.form.get("precio", "0").strip()
 
        errores = []
        if not referencia:
            errores.append("La referencia es obligatoria.")
 
        try:
            stock = int(stock_raw)
            if stock < 0:
                raise ValueError
        except ValueError:
            errores.append("El stock debe ser un número igual o mayor que 0.")
            stock = 0
 
        try:
            precio = Decimal(precio_raw)
            if precio < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            errores.append("El precio debe ser un número válido mayor o igual a 0.")
            precio = Decimal("0.00")
 
        # Referencia duplicada
        if referencia and Mobiliario.query.filter_by(referencia=referencia).first():
            errores.append(f"Ya existe un mobiliario con la referencia «{referencia}».")
 
        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template(
                "admin/formularios/formMobiliario.html",
                form=request.form,
                accion="crear",
            )
 
        nuevo = Mobiliario(
            referencia=referencia,
            descripcion=descripcion or None,
            stock=stock,
            precio=precio,
            
        )
 
        try:
            db.session.add(nuevo)
            db.session.commit()
            flash("Mobiliario creado correctamente.", "success")
            return redirect(url_for("router_admin.listar_mobiliario"))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al crear el mobiliario.", "danger")
 
    return render_template(
        "admin/formularios/formMobiliario.html",
        form={},
        accion="crear",
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR']
    )
 


# Función que maneja la edición de un mobiliario existente por parte del administrador, verificando su existencia, 
# validando los datos del formulario y actualizando el registro en la base de datos. 
def f_editar_mobiliario(mobiliario_id):
    mobiliario = Mobiliario.query.get_or_404(mobiliario_id)
 
    if request.method == "POST":
        referencia  = (request.form.get("referencia")  or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        stock_raw   = request.form.get("stock",  "0").strip()
        precio_raw  = request.form.get("precio", "0").strip()
 
        errores = []
        if not referencia:
            errores.append("La referencia es obligatoria.")
 
        try:
            stock = int(stock_raw)
            if stock < 0:
                raise ValueError
        except ValueError:
            errores.append("El stock debe ser un número igual o mayor que 0.")
            stock = mobiliario.stock
 
        try:
            precio = Decimal(precio_raw)
            if precio < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            errores.append("El precio debe ser un número válido mayor o igual a 0.")
            precio = mobiliario.precio
 
        # Referencia duplicada (excluyendo el propio registro)
        duplicado = Mobiliario.query.filter(
            Mobiliario.referencia == referencia,
            Mobiliario.id != mobiliario_id,
        ).first()
        if duplicado:
            errores.append(f"Ya existe otro mobiliario con la referencia «{referencia}».")
 
        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template(
                "admin/formularios/formMobiliario.html",
                form=request.form,
                mobiliario=mobiliario,
                accion="editar",
            )
 
        mobiliario.referencia  = referencia
        mobiliario.descripcion = descripcion or None
        mobiliario.stock       = stock
        mobiliario.precio      = precio
 
        try:
            db.session.commit()
            flash("Mobiliario actualizado correctamente.", "success")
            return redirect(url_for("router_admin.listar_mobiliario"))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al actualizar el mobiliario.", "danger")
 
    return render_template(
        "admin/formularios/formMobiliario.html",
        form={},
        mobiliario=mobiliario,
        accion="editar",
    )
 
 
# Función que maneja la eliminación de un mobiliario por parte del administrador, verificando su existencia, eliminándolo de la base de datos y redirigiendo al listado de mobiliario.
def f_eliminar_mobiliario(mobiliario_id):
    mobiliario = Mobiliario.query.get_or_404(mobiliario_id)
 
    try:
        db.session.delete(mobiliario)
        db.session.commit()
        flash(f"Mobiliario «{mobiliario.referencia}» eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Error al eliminar el mobiliario. Puede tener solicitudes asociadas.", "danger")
 
    return redirect(url_for("router_admin.listar_mobiliario"))    


# Función que maneja la visualización del mapa de stands en el panel de administración, mostrando el estado, proveedor, solicitud asociada, precio y dimensiones de cada stand.
def f_ver_mapa():
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
            "solicitud_id": stand.solicitud_id,
            "precio": float(stand.precio),
            "dimensiones": float(stand.dimensiones) if stand.dimensiones else 9
        }

    return render_template("admin/admin_mapa.html", resultado=resultado)


# Función que maneja la actualización del estado de múltiples stands a través de una solicitud JSON, verificando su existencia, 
# registrando el historial de cambios y limpiando las relaciones si se liberan los stands.
def f_actualizar_stands():

    data = request.get_json()
    stands = data.get("stands", {})

    try:

        for numero, nuevo_estado in stands.items():

            stand = Stand.query.filter_by(numero_stand=numero).first()
            if not stand:
                continue

            estado_anterior = stand.estado.value

            solicitud = stand.solicitud  # cache seguro

            # =====================================
            # HISTORIAL: CAMBIO DE ESTADO
            # =====================================
            historial_cambio = HistorialStand(
                stand_id=stand.numero_stand,
                accion="cambio_estado",
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                solicitud_origen_id=stand.solicitud_id,
                usuario_origen_id=None,
                usuario_destino_id=solicitud.usuario_id if solicitud else None,
                observacion="Cambio manual desde panel admin",
                fecha=datetime.now()
            )

            db.session.add(historial_cambio)

            # =====================================
            # ACTUALIZAR ESTADO
            # =====================================
            stand.estado = nuevo_estado

            # =====================================
            # LIMPIAR RELACIONES SI SE LIBERA
            # =====================================
            if nuevo_estado in ["disponible", "no_disponible"]:

                detalles = DetalleSolicitudStand.query.filter_by(
                    stand_id=stand.numero_stand
                ).all()

                for detalle in detalles:

                    sol = detalle.solicitud

                    # =====================================
                    # HISTORIAL: DESASIGNACIÓN
                    # =====================================
                    historial_desasig = HistorialStand(
                        stand_id=stand.numero_stand,
                        accion="desasignacion",
                        estado_anterior=estado_anterior,
                        estado_nuevo=nuevo_estado,
                        solicitud_origen_id=sol.id if sol else None,
                        usuario_origen_id= None,
                        observacion="Desasignado por liberación de stand",
                        fecha=datetime.now()
                    )

                    db.session.add(historial_desasig)

                    db.session.delete(detalle)

                    if sol:
                        sol.estado = "cancelada_admin"

                stand.solicitud_id = None

        db.session.commit()

        return jsonify({"ok": True})

    except Exception as e:

        db.session.rollback()
        print(e)

        return jsonify({
            "ok": False,
            "error": "ERROR_INTERNO"
        }), 500
        


# Función que maneja la visualización del historial de cambios de los stands en el panel de administración, aplicando filtros y paginación 
# para mostrar detalles como fecha, acción, estado anterior y nuevo, usuarios involucrados y observaciones.
def f_historial_stands():

    query = HistorialStand.query

    # =========================
    # FILTROS
    # =========================
    stand_id = request.args.get("stand_id")
    usuario_id = request.args.get("usuario_id")
    accion = request.args.get("accion")
    fecha_desde = request.args.get("desde")
    fecha_hasta = request.args.get("hasta")
    search = request.args.get("search")

    if stand_id:
        query = query.filter(HistorialStand.stand_id == stand_id)

    if usuario_id:
        query = query.filter(
            (HistorialStand.usuario_origen_id == usuario_id) |
            (HistorialStand.usuario_destino_id == usuario_id)
        )

    if accion:
        query = query.filter(HistorialStand.accion == accion)

    if fecha_desde:
        query = query.filter(HistorialStand.fecha >= fecha_desde)

    if fecha_hasta:
        query = query.filter(HistorialStand.fecha <= fecha_hasta)

    if search:
        query = query.filter(
            HistorialStand.observacion.ilike(f"%{search}%")
        )

    # =========================
    # PAGINACIÓN
    # =========================
    page = request.args.get("page", 1, type=int)
    per_page = 10
    paginacion = query.order_by(HistorialStand.fecha.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    historial_db = paginacion.items

    historial = []

    for h in historial_db:

        usuario_origen = Usuario.query.get(h.usuario_origen_id) if h.usuario_origen_id else None
        usuario_destino = Usuario.query.get(h.usuario_destino_id) if h.usuario_destino_id else None

        accion_legible = {
            "cambio_estado": "Cambio de estado",
            "pre_reserva": "Pre reserva de stand",
            "desasignacion": "Liberación de stand",
            "cambio_estado_solicitud": "Gestión de solicitud (Administrador)",
            "aceptar_solicitud_admin": "Solicitud aceptada por administración",
            "rechazar_solicitud_admin": "Solicitud rechazada por administración"
        }.get(h.accion, h.accion.replace("_", " ").title())

        def nombre_usuario(u):
            if not u:
                return "Administrador"
            return f"{u.nombre_empresa}".strip()

        historial.append({
            "fecha": h.fecha.strftime("%d/%m/%Y %H:%M") if h.fecha else "-",
            "stand": f"Stand #{h.stand_id}" if h.stand_id else "Solicitud",
            "accion": accion_legible,
            "estado_anterior": h.estado_anterior or "-",
            "estado_nuevo": h.estado_nuevo or "-",
            "usuario_origen": nombre_usuario(usuario_origen),
            "usuario_destino": nombre_usuario(usuario_destino),
            "observacion": h.observacion or "-"
        })

    return render_template(
        "admin/listados/listadoHistorialSolicitudes.html",
        historial=historial,
        paginacion=paginacion        
    )
 


# Función que maneja la asignación manual de stands a un proveedor específico a través de una solicitud JSON, verificando la existencia del usuario,
def f_asignar_stand_proveedor():

    data = request.get_json()

    stands_ids = data.get("stands", [])
    usuario_id = data.get("usuario_id")

    if not stands_ids or not usuario_id:

        return jsonify({
            "ok": False,
            "error": "DATOS_INSUFICIENTES"
        }), 400

    usuario = Usuario.query.get(usuario_id)

    if not usuario:

        return jsonify({
            "ok": False,
            "error": "NO_ENCONTRADO"
        }), 404

    # =========================
    # CREAR / BUSCAR SOLICITUD
    # =========================
    solicitud = usuario.solicitudes.filter_by(
        estado="asignado_por_admin"
    ).first()

    if not solicitud:

        solicitud = Solicitud(
            usuario_id=usuario.id,
            estado="asignado_por_admin",
            fecha_solicitud=datetime.now()
        )

        db.session.add(solicitud)
        db.session.flush()

    # =========================
    # RECORRER TODOS LOS STANDS
    # =========================
    for numero_stand in stands_ids:

        stand = Stand.query.filter_by(
            numero_stand=numero_stand
        ).first()

        if not stand:
            continue

        # 🚫 evitar sobrescribir
        if stand.estado in [
            EstadoStandEnum.ocupado,
            EstadoStandEnum.pre_reservado
        ]:
            continue

        estado_anterior = stand.estado.value

        # =========================
        # ASIGNAR STAND
        # =========================
        stand.estado = EstadoStandEnum.ocupado
        stand.solicitud_id = solicitud.id

        # =========================
        # 🔥 DETALLE SOLICITUD STAND (NUEVO)
        # =========================
        detalle = DetalleSolicitudStand(
            solicitud_id=solicitud.id,
            stand_id=stand.numero_stand,
            cantidad=1,
            precio_total=stand.precio or 0
        )

        db.session.add(detalle)

        # =========================
        # HISTORIAL
        # =========================
        historial = HistorialStand(
            stand_id=stand.numero_stand,
            accion="asignacion_admin",
            estado_anterior=estado_anterior,
            estado_nuevo="ocupado",
            solicitud_origen_id=None,
            solicitud_destino_id=solicitud.id,
            usuario_origen_id=None,
            usuario_destino_id=usuario.id,
            observacion="Asignación manual desde admin",
            fecha=datetime.now()
        )

        db.session.add(historial)

    db.session.commit()

    return jsonify({
        "ok": True
    })


# Función que maneja la visualización de los proveedores disponibles para asignar stands en formato JSON, incluyendo su ID y nombre de empresa.
def f_proveedores_disponibles():

    usuarios = Usuario.query.filter(
        Usuario.rol == "proveedor",
    ).all()

    return jsonify([
        {
            "id": u.id,
            "nombre": u.nombre_empresa
        }
        for u in usuarios
    ])
    

# Función que maneja la exportación del historial de cambios de los stands a un archivo Excel, aplicando formato legible y descargándolo para el usuario.    
def f_exportar_excel_historial():

    historial = HistorialStand.query.order_by(HistorialStand.fecha.desc()).all()

    data = []

    for h in historial:

        usuario_origen = Usuario.query.get(h.usuario_origen_id) if h.usuario_origen_id else None
        usuario_destino = Usuario.query.get(h.usuario_destino_id) if h.usuario_destino_id else None

        # =========================
        # EMPRESA (CON REGLA REAL)
        # =========================
        def empresa(u):
            if not u:
                return "Administrador"

            # si no tiene empresa, también puede ser admin o sistema
            return u.nombre_empresa if u.nombre_empresa else "Administrador"

        # =========================
        # ACCIÓN HUMANIZADA
        # =========================
        accion_legible = {
            "cambio_estado": "Cambio de estado de stand",
            "pre_reserva": "Reserva de stand",
            "desasignacion": "Liberación de stand",
            "cambio_estado_solicitud": "Gestión de solicitud (Administrador)",
            "aceptar_solicitud_admin": "Solicitud aceptada por administración",
            "rechazar_solicitud_admin": "Solicitud rechazada por administración"
        }.get(h.accion, h.accion.replace("_", " ").title())

        # =========================
        # REFERENCIA INTELIGENTE
        # =========================
        if h.stand_id:
            referencia = f"Stand #{h.stand_id}"
        else:
            referencia = "Solicitud (sin asignación de stand)"

        data.append({
            "fecha": h.fecha.strftime("%d/%m/%Y %H:%M") if h.fecha else "-",

            "referencia": referencia,

            "accion": accion_legible,

            "estado_anterior": h.estado_anterior or "-",
            "estado_nuevo": h.estado_nuevo or "-",

            # EMPRESAS (no usuarios)
            "empresa_origen": empresa(usuario_origen),
            "empresa_destino": empresa(usuario_destino),

            "observacion": h.observacion or "-"
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Historial")

    output.seek(0)

    return send_file(
        output,
        download_name="historial_stands.xlsx",
        as_attachment=True
    )



# Función que maneja la exportación del historial de cambios de los stands a un archivo PDF, aplicando formato legible y descargándolo para el usuario.
def f_exportar_pdf_historial():

    historial = HistorialStand.query.all()

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer)

    data = [["Fecha", "Stand", "Acción", "Estado"]]

    for h in historial:
        data.append([
            str(h.fecha),
            str(h.stand_id),
            h.accion,
            f"{h.estado_anterior} → {h.estado_nuevo}"
        ])

    table = Table(data)
    pdf.build([table])

    buffer.seek(0)

    return send_file(buffer, download_name="historial.pdf", as_attachment=True)


#/===========================================================\
# Funciones para INCIDENCIAS                                 #
#\===========================================================/


# Función que maneja la visualización del listado de incidencias en el panel de administración, aplicando filtros por estado y paginación 
# para mostrar detalles como título, descripción, estado y fecha de creación de cada incidencia.
def f_listar_incidencias():
    filtro_estado = request.args.get('estado')
    page = request.args.get('page', 1, type=int)

    query = Incidencia.query.order_by(Incidencia.fecha_creacion.desc())

    if filtro_estado in ['pendiente', 'revisada']:
        query = query.filter(Incidencia.estado == filtro_estado)    

    paginacion = query.paginate(page=page, per_page=10, error_out=False)
    

    return render_template('admin/listados/listadoIncidencias.html',
        incidencias=paginacion.items,
        paginacion=paginacion,
        filtro_estado=filtro_estado
    )


# Función que maneja la actualización del estado de una incidencia específica por parte del administrador, verificando su existencia, 
# validando el nuevo estado y actualizando el registro en la base de datos.
def f_cambiar_estado_incidencia(incidencia_id):
    incidencia = Incidencia.query.get_or_404(incidencia_id)
    nuevo_estado = request.form.get('estado')

    if nuevo_estado in ['pendiente', 'revisada']:
        incidencia.estado = nuevo_estado  # string directo, no EstadoIncidencia[nuevo_estado]
        db.session.commit()
        flash('Estado actualizado correctamente.', 'success')
    else:
        flash('Estado no válido.', 'danger')

    return redirect(url_for('router_admin.listar_incidencias'))

def f_eliminar_incidencia(incidencia_id):
    incidencia = Incidencia.query.get_or_404(incidencia_id)
    db.session.delete(incidencia)
    db.session.commit()
    flash('Incidencia eliminada.', 'success')
    return redirect(url_for('router_admin.listar_incidencias'))        


#/===========================================================\
# CAMBIAR FECHA DEL FORUM                                    #
#\===========================================================/


# Función que maneja la actualización de la fecha del forum a través de un formulario en el panel de administración, 
# validando el formato de la fecha y actualizando el registro en la base de datos.
def f_cambiar_fecha_forum():
    if request.method == "POST":
        nueva_fecha_str = request.form.get("fecha_forum")
        try:
            nueva_fecha = datetime.strptime(nueva_fecha_str, "%Y-%m-%dT%H:%M")
            config = Config.query.first()

            if config:
                config.fecha_forum = nueva_fecha
            else:
                config = Config(fecha_forum=nueva_fecha)
                db.session.add(config)

            db.session.commit()
            flash("Fecha del forum actualizada correctamente.", "success")

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al actualizar la fecha.", "danger")

    return redirect(url_for("router_admin.adminDashboard"))

def f_cambiar_fecha_fin_reservas():
    if request.method == "POST":
        nueva_fecha_str = request.form.get("fecha_fin_reservas")
        try:
            nueva_fecha = datetime.strptime(nueva_fecha_str, "%Y-%m-%dT%H:%M")
            config = Config.query.first()

            if config:
                config.fecha_fin_reservas = nueva_fecha
            else:
                config = Config(fecha_fin_reservas=nueva_fecha)
                db.session.add(config)

            db.session.commit()
            flash("Fecha de fin de reservas actualizada correctamente.", "success")

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Error al actualizar la fecha.", "danger")

    return redirect(url_for("router_admin.adminDashboard"))


#FUNCION ENVIAR Y GENERAR PDF DE SOLICITUDES



# ══════════════════════════════════════════════════════════════════════════════
#  PALETA — fondo blanco
# ══════════════════════════════════════════════════════════════════════════════
 
ORANGE     = colors.HexColor("#E8780A")   # naranja ligeramente más oscuro para contraste sobre blanco
DARK       = colors.HexColor("#1e293b")   # texto principal
MID        = colors.HexColor("#475569")   # texto secundario
MUTED_COL  = colors.HexColor("#94a3b8")   # texto apagado
GREEN      = colors.HexColor("#16a34a")   # descuento
WHITE      = colors.white
LIGHT_LINE = colors.HexColor("#e2e8f0")   # líneas divisoras suaves
ROW_ALT    = colors.HexColor("#f8fafc")   # fondo alternado filas
CARD_HEAD  = colors.HexColor("#f1f5f9")   # cabecera de tarjeta
 


# Función que maneja la generación de un PDF con todas las solicitudes del proveedor actual y su envío por correo electrónico, 
# obteniendo las solicitudes asociadas al proveedor, construyendo el PDF con la información de las solicitudes, y utilizando Flask-Mail para enviar el PDF 
# como adjunto al correo del proveedor
def f_generar_pdf_solicitudes(solicitud_id):
    solicitud = Solicitud.query.get_or_404(solicitud_id)

    estados = ["borrador", "asignado_por_admin", "confirmada"]

    solicitudes = (
        Solicitud.query
        .filter(
            Solicitud.usuario_id == solicitud.usuario_id,
            Solicitud.estado.in_(estados)
        )
        .order_by(Solicitud.fecha_solicitud)
        .all()
    )

    if not solicitudes:
        return jsonify({"ok": False, "error": "Sin solicitudes"}), 400

    pdf_bytes = _build_pdf(solicitudes, solicitud.usuario)

    try:
        msg = Message(
            subject="Resumen de tus solicitudes — DSG Forum",
            recipients=[solicitud.usuario.email],
        )
        msg.body = (
            f"Hola {getattr(solicitud.usuario, 'nombre', None) or solicitud.usuario.email},\n\n"
            "Adjuntamos el resumen completo de tus solicitudes en DSG Forum.\n\n"
            "Si tienes alguna duda contacta con nosotros.\n\n"
            "Un saludo,\nEl equipo de DSG"
        )
        msg.attach(
            filename=f"solicitudes_{solicitud.usuario.id}_{datetime.now().strftime('%Y%m%d')}.pdf",
            content_type="application/pdf",
            data=pdf_bytes,
        )
        mail.send(msg)

    except Exception as e:
        current_app.logger.error(f"Error enviando PDF por correo: {e}")
        return jsonify({"ok": False, "error": "No se pudo enviar el correo"}), 500

    return jsonify({"ok": True, "message": f"PDF enviado a {solicitud.usuario.email}"})


# ══════════════════════════════════════════════════════════════════════════════
#  ESTILOS
# ══════════════════════════════════════════════════════════════════════════════
 

# Función que dibuja el encabezado del PDF, incluyendo los logos de la organización y el diseño visual del encabezado
def _draw_header(canvas, doc):

    canvas.saveState()

    width, height = A4

    # =========================
    # PATHS LOGOS
    # =========================
    logo_left = os.path.join(
        current_app.root_path,
        "static/img/logo_forum2026.png",
    )

    logo_right = os.path.join(
        current_app.root_path,
        "static/img/logo.png"
    )

    # =========================
    # TAMAÑOS
    # =========================
    logo_width = 90
    logo_height = 42

    top_y = height - 55

    # =========================
    # LOGO IZQUIERDA
    # =========================
    canvas.drawImage(
        logo_left,
        40,
        top_y,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask='auto'
    )

    # =========================
    # LOGO DERECHA
    # =========================
    canvas.drawImage(
        logo_right,
        width - logo_width - 40,
        top_y,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask='auto'
    )

    canvas.restoreState()



# Función que dibuja el pie de página del PDF, incluyendo una nota sobre recargos en caso de devolución de productos en mal estado, 
# y el diseño visual del pie de página
def _draw_footer(canvas, doc):
    canvas.saveState()
    width, height = A4

    footer_style = ParagraphStyle(
        "FooterNote",
        parent=getSampleStyleSheet()["Normal"],
        fontSize=8,
        textColor=colors.orange,
        fontName="Helvetica-Oblique",
        alignment=TA_CENTER,
    )

    p = Paragraph(
        "*Se aplicarán recargos en caso de que alguno de los productos se devuelva en mal estado.",
        footer_style
    )

    w, h = p.wrap(doc.width, doc.bottomMargin)
    p.drawOn(canvas, doc.leftMargin, 10)  # 10 puntos desde el borde inferior

    canvas.restoreState()



# Función que define los estilos de texto para el PDF, incluyendo estilos para títulos, subtítulos, secciones, texto normal, cantidades, totales, 
# y otros elementos visuales del PDF
def _styles():
    base = getSampleStyleSheet()
 
    return dict(
        title=ParagraphStyle(
            "DSGTitle",
            parent=base["Normal"],
            fontSize=24,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
            spaceAfter=0,
            leading=30,
        ),
        subtitle=ParagraphStyle(
            "DSGSubtitle",
            parent=base["Normal"],
            fontSize=11,
            textColor=MID,
            fontName="Helvetica",
            spaceBefore=6,
            spaceAfter=6,
            leading=16,
        ),
        meta=ParagraphStyle(
            "DSGMeta",
            parent=base["Normal"],
            fontSize=9,
            textColor=MUTED_COL,
            fontName="Helvetica",
            spaceAfter=14,
        ),
        section=ParagraphStyle(
            "DSGSection",
            parent=base["Normal"],
            fontSize=12,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
            spaceBefore=20,
            spaceAfter=4,
        ),
        normal=ParagraphStyle(
            "DSGNormal",
            parent=base["Normal"],
            fontSize=9,
            textColor=DARK,
            fontName="Helvetica",
            spaceAfter=2,
        ),
        card_title=ParagraphStyle(
            "DSGCardTitle",
            parent=base["Normal"],
            fontSize=9,
            textColor=DARK,
            fontName="Helvetica-Bold",
            spaceAfter=0,
        ),
        subsection=ParagraphStyle(
            "DSGSubsection",
            parent=base["Normal"],
            fontSize=8,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
        ),
        amount=ParagraphStyle(
            "DSGAmount",
            parent=base["Normal"],
            fontSize=9,
            textColor=DARK,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        ),
        amount_muted=ParagraphStyle(
            "DSGAmountMuted",
            parent=base["Normal"],
            fontSize=8,
            textColor=MID,
            fontName="Helvetica",
            alignment=TA_RIGHT,
        ),
        total_lbl=ParagraphStyle(
            "DSGTotalLbl",
            parent=base["Normal"],
            fontSize=10,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
        ),
        total_val=ParagraphStyle(
            "DSGTotalVal",
            parent=base["Normal"],
            fontSize=10,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        ),
        ticket_lbl=ParagraphStyle(
            "DSGTicketLbl",
            parent=base["Normal"],
            fontSize=10,
            textColor=DARK,
            fontName="Helvetica",
        ),
        ticket_val=ParagraphStyle(
            "DSGTicketVal",
            parent=base["Normal"],
            fontSize=10,
            textColor=DARK,
            fontName="Helvetica",
            alignment=TA_RIGHT,
        ),
        subtotal_lbl=ParagraphStyle(
            "DSGSubtotalLbl",
            parent=base["Normal"],
            fontSize=10,
            textColor=DARK,
            fontName="Helvetica-Bold",
        ),
        subtotal_val=ParagraphStyle(
            "DSGSubtotalVal",
            parent=base["Normal"],
            fontSize=10,
            textColor=DARK,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        ),
        discount_lbl=ParagraphStyle(
            "DSGDiscountLbl",
            parent=base["Normal"],
            fontSize=10,
            textColor=GREEN,
            fontName="Helvetica",
        ),
        discount_val=ParagraphStyle(
            "DSGDiscountVal",
            parent=base["Normal"],
            fontSize=10,
            textColor=GREEN,
            fontName="Helvetica",
            alignment=TA_RIGHT,
        ),
        grand_lbl=ParagraphStyle(
            "DSGGrandLbl",
            parent=base["Normal"],
            fontSize=13,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
        ),
        grand_val=ParagraphStyle(
            "DSGGrandVal",
            parent=base["Normal"],
            fontSize=13,
            textColor=ORANGE,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        ),
    )
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
 

 # Función que construye el PDF con la información de las solicitudes del proveedor, utilizando ReportLab para generar un documento PDF con el diseño y formato adecuado,
 # incluyendo secciones para solicitudes de stands, mobiliario, extras, y un ticket resumen al final, y devolviendo el PDF generado como un objeto de bytes 
 # para su posterior envío por correo electrónico
def _build_pdf(solicitudes, user) -> bytes:
    buffer = io.BytesIO()
    W, H = A4
    margin = 18 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Mis Solicitudes — DSG Forum",
    )

    st = _styles()
    story = []
    content_w = W - 2 * margin

    # ── CABECERA ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Resumen de solicitudes", st["subtitle"]))
    story.append(Paragraph(
        f"Proveedor: <b>{getattr(user, 'nombre', None) or user.email}</b>"
        f"&nbsp;&nbsp;·&nbsp;&nbsp;"
        f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        st["meta"]
    ))
    story.append(HRFlowable(
        width=content_w, color=ORANGE, thickness=2, spaceAfter=16
    ))

    # ── SEPARAR ───────────────────────────────────────────────────────────────
    stands_list     = []
    mobiliario_list = []

    for s in solicitudes:
        if len(s.detalles_stand) > 0 and len(s.detalles_mobiliario) == 0:
            stands_list.append(s)
        else:
            mobiliario_list.append(s)

    # ── SECCIONES ─────────────────────────────────────────────────────────────
    if stands_list:
        story.append(Paragraph("Solicitudes de Stands", st["section"]))
        story.append(HRFlowable(
            width=content_w, color=LIGHT_LINE, thickness=1, spaceAfter=8
        ))
        for sol in stands_list:
            story += _render_card(sol, st, content_w)

    if mobiliario_list:
        story.append(Paragraph("Solicitudes de Mobiliario", st["section"]))
        story.append(HRFlowable(
            width=content_w, color=LIGHT_LINE, thickness=1, spaceAfter=8
        ))
        for sol in mobiliario_list:
            story += _render_card(sol, st, content_w)

    # ── TICKET GLOBAL ─────────────────────────────────────────────────────────
    story += _render_ticket(solicitudes, st, content_w)

    doc.build(
        story,
        onFirstPage=lambda c, d: (_draw_header(c, d), _draw_footer(c, d)),
        onLaterPages=lambda c, d: (_draw_footer(c, d))
    )
    return buffer.getvalue()



# Función que renderiza una tarjeta individual para cada solicitud, mostrando la información detallada de la solicitud, incluyendo los 
# stands, mobiliario, extras, y el total de la solicitud, y devolviendo esta información como una lista de elementos de ReportLab para ser añadidos al PDF
def _render_card(sol, st, content_w):
    elements = []
    COL_L = content_w * 0.65
    COL_R = content_w * 0.35

    h_tbl = Table(
        [[Paragraph(
            f"Solicitud — {sol.fecha_solicitud.strftime('%d/%m/%Y  %H:%M')}",
            st["card_title"]
        )]],
        colWidths=[content_w]
    )
    h_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CARD_HEAD),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, -1), 1, LIGHT_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(h_tbl)

    body_rows = []

    # Stands
    if len(sol.detalles_stand) > 0:
        body_rows.append([Paragraph("Stands", st["subsection"]), ""])
        for d in sol.detalles_stand:
            body_rows.append([
                Paragraph(
                    f"Stand #{d.stand.numero_stand}"
                    f" <font color='#94a3b8'>· {d.stand.dimensiones} m²</font>",
                    st["normal"]
                ),
                Paragraph(f"{float(d.precio_total):.2f} €", st["amount"]),
            ])

    # Mobiliario
    if len(sol.detalles_mobiliario) > 0:
        if body_rows:
            body_rows.append(["", ""])
        body_rows.append([Paragraph("Mobiliario", st["subsection"]), ""])
        for d in sol.detalles_mobiliario:
            ppu = float(d.precio_total) / d.cantidad
            body_rows.append([
                Paragraph(
                    f"{d.mobiliario.referencia}"
                    f" <font color='#94a3b8'>× {d.cantidad} · {ppu:.2f} €/ud</font>",
                    st["normal"]
                ),
                Paragraph(f"{float(d.precio_total):.2f} €", st["amount"]),
            ])

    # Extras
    if sol.extras:
        if body_rows:
            body_rows.append(["", ""])
        body_rows.append([Paragraph("Extras", st["subsection"]), ""])
        for e in sol.extras:
            if e.precio:
                val = f"{float(e.precio):.2f} €/ud · {float(e.precio) * e.cantidad:.2f} € total"
            else:
                val = "Precio pendiente"
            body_rows.append([
                Paragraph(
                    f"{e.descripcion} <font color='#94a3b8'>× {e.cantidad}</font>",
                    st["normal"]
                ),
                Paragraph(val, st["amount_muted"]),
            ])

    if body_rows:
        row_styles = [
            ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]
        for i, row in enumerate(body_rows):
            if row[1] != "" and i % 2 == 0:
                row_styles.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))

        b_tbl = Table(body_rows, colWidths=[COL_L, COL_R])
        b_tbl.setStyle(TableStyle(row_styles))
        elements.append(b_tbl)

    # — Fila total solicitud —
    total_stands = sum(float(d.precio_total) for d in sol.detalles_stand)
    total_mob    = sum(float(d.precio_total) for d in sol.detalles_mobiliario)
    total_extras = sum(float(e.precio) * e.cantidad for e in sol.extras if e.precio)
    total        = total_stands + total_mob + total_extras

    tot_tbl = Table(
        [[Paragraph("Total solicitud", st["total_lbl"]),
          Paragraph(f"{total:.2f} €", st["total_val"])]],
        colWidths=[COL_L, COL_R]
    )
    tot_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("LINEABOVE",     (0, 0), (-1, 0), 1.5, ORANGE),
        ("LINEBELOW",     (0, 0), (-1, 0), 1,   LIGHT_LINE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    elements.append(tot_tbl)
    elements.append(Spacer(1, 14))

    return elements




# Función que renderiza el ticket resumen al final del PDF, calculando los totales de stands, mobiliario, extras, aplicando descuentos si es necesario,
# y mostrando un resumen global de la situación económica de las solicitudes del proveedor, devolviendo esta información como una lista de elementos 
# de ReportLab para ser añadidos al PDF
def _render_ticket(solicitudes, st, content_w):
    elements = []
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Ticket Global", ParagraphStyle(
        "tg", fontSize=13, fontName="Helvetica-Bold",
        textColor=ORANGE, spaceBefore=10, spaceAfter=4,
    )))
    elements.append(HRFlowable(
        width=content_w, color=ORANGE, thickness=2, spaceAfter=10
    ))

    total_stands = total_mob = total_extras = precio_final = 0

    for s in solicitudes:
        for d in s.detalles_stand:
            total_stands += float(d.precio_total or 0)
        for d in s.detalles_mobiliario:
            total_mob += float(d.precio_total or 0)
        for e in s.extras:
            if e.precio:
                total_extras += float(e.precio) * e.cantidad
        if s.precio_final is not None:
            precio_final = float(s.precio_final)

    subtotal    = total_stands + total_mob + total_extras
    descuento   = subtotal - precio_final if precio_final > 0 and precio_final < subtotal else 0
    total_final = precio_final if descuento > 0 else subtotal

    COL_L = content_w * 0.6
    COL_R = content_w * 0.4

    rows = [
        [Paragraph("Stands",     st["ticket_lbl"]), Paragraph(f"{total_stands:.2f} €", st["ticket_val"])],
        [Paragraph("Mobiliario", st["ticket_lbl"]), Paragraph(f"{total_mob:.2f} €",   st["ticket_val"])],
        [Paragraph("Extras",     st["ticket_lbl"]), Paragraph(f"{total_extras:.2f} €", st["ticket_val"])],
        [Paragraph("Subtotal",   st["subtotal_lbl"]), Paragraph(f"{subtotal:.2f} €",   st["subtotal_val"])],
    ]

    if descuento > 0:
        rows.append([
            Paragraph("Descuento", st["discount_lbl"]),
            Paragraph(f"− {descuento:.2f} €", st["discount_val"]),
        ])

    rows.append([
        Paragraph("TOTAL", st["grand_lbl"]),
        Paragraph(f"{total_final:.2f} €", st["grand_val"]),
    ])

    t = Table(rows, colWidths=[COL_L, COL_R])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("LINEBELOW",     (0, 0), (-1, -3), 0.5, LIGHT_LINE),
        ("LINEABOVE",     (0, -1), (-1, -1), 1.5, ORANGE),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#fff7ed")),
        ("BOX",           (0, 0), (-1, -1), 1, LIGHT_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t)

    return elements
   