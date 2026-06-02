from datetime import datetime
from flask_mail import Message
import secrets
import string
from flask import  app, current_app, jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user

from models.acompanante import Acompanante
from models.enums import RolEnum
from models.incidencia import Incidencia
from models.producto import Producto
from models.usuario import Usuario
from utils.utils import createUsername, redirigir_por_rol
from extensions import db, mail
from utils.utils import inject_year
from werkzeug.security import check_password_hash, generate_password_hash


# Función que maneja el proceso de inicio de sesión, validando las credenciales del usuario, iniciando la sesión, y redirigiendo según el rol del usuario
def f_login():

    # Si ya está logueado, redirigir según rol
    if current_user.is_authenticated:
        return redirigir_por_rol(current_user)

    if request.method == "POST":
        nombre_usuario = request.form.get("nombre_usuario", "").strip().upper()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

        if not usuario or not usuario.check_password(password):
            flash("Nombre de usuario o contraseña incorrectos.", "danger")
            return render_template("auth/index.html", CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR'])

        login_user(usuario)

        # Si venía de una página protegida
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)

        # Redirección según rol
        return redirigir_por_rol(usuario)

    return render_template("auth/index.html", CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR'])




# Función que maneja la redirección al dashboard correspondiente según el rol del usuario, redirigiendo a la página de inicio si el rol no es reconocido
def f_dashboard():
    return redirect(url_for("router_index.home"))



# Función que maneja el proceso de cierre de sesión, cerrando la sesión del usuario, mostrando un mensaje de confirmación, y redirigiendo a la página de inicio
def f_logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("router_index.home"))
 


# Función que maneja el proceso de recuperación de contraseña, validando el email proporcionado, generando una nueva contraseña temporal, 
# actualizando la contraseña del usuario, enviando un correo con la nueva contraseña, y mostrando mensajes de éxito o error según corresponda
def generar_contraseña_temporal(longitud=10):
    """Genera una contraseña aleatoria segura."""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))



# Función que maneja el proceso de recuperación de contraseña, validando el email proporcionado, generando una nueva contraseña temporal,
# actualizando la contraseña del usuario, enviando un correo con la nueva contraseña, y mostrando
def f_recuperar_contraseña(request):
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            flash("No se encontró una cuenta con ese email.", "danger")
            return redirect(url_for("router_index.recuperar_contraseña"))

        nueva_contraseña = generar_contraseña_temporal()
        usuario.set_password(nueva_contraseña)
        db.session.commit()

        try:
            msg = Message(
                subject="Recuperación de contraseña — Forum "+datetime.now().strftime("%y"),
                recipients=[usuario.email],
                html=f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin:0; padding:0; background:#111827; font-family:'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#111827; padding: 40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#1F2937; border-radius:12px; border:1px solid #374151; overflow:hidden;">
          <tr>
            <td style="background:#1F2937; padding: 32px 40px 24px; border-bottom: 1px solid #374151; text-align:center;">
              <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#F97316; margin-right:8px; vertical-align:middle;"></span>
              <span style="font-size:1.4rem; font-weight:700; color:#F9FAFB; letter-spacing:0.02em; vertical-align:middle;">
                Forum <span style="color:#F97316;">{datetime.now().strftime('%y')}</span>
              </span>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 40px;">
              <p style="margin:0 0 8px; font-size:0.85rem; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.06em;">
                Recuperación de contraseña
              </p>
              <h1 style="margin:0 0 24px; font-size:1.3rem; font-weight:600; color:#F9FAFB;">
                Hola, {usuario.nombre}
              </h1>
              <p style="margin:0 0 24px; font-size:0.95rem; color:#9CA3AF; line-height:1.6;">
                Hemos recibido una solicitud para restablecer tu contraseña en <strong style="color:#F9FAFB;">Forum {datetime.now().strftime('%y')}</strong>.
                Tu nueva contraseña temporal es:
              </p>
              <div style="background:#111827; border:1px solid #374151; border-left: 3px solid #F97316; border-radius:8px; padding: 16px 24px; text-align:center; margin-bottom:24px;">
                <span style="font-size:1.4rem; font-weight:700; color:#F97316; letter-spacing:0.1em;">
                  {nueva_contraseña}</span>
              </div>
              <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2); border-radius:8px; padding:12px 16px;">
                <p style="margin:0; font-size:0.85rem; color:#FCA5A5;">
                  <strong>⚠ Si no has solicitado este cambio</strong>, contacta con el administrador inmediatamente.
                </p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 40px; border-top: 1px solid #374151; text-align:center;">
              <p style="margin:0; font-size:0.8rem; color:#6B7280;">
                Forum {datetime.now().strftime('%y')} — Grupo DSG &copy; {datetime.now().strftime('%Y')} 
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
                """
            )
            mail.send(msg)
            flash("Te hemos enviado una nueva contraseña a tu correo.", "success")

        except Exception as e:
            db.session.rollback()
            flash("Error al enviar el correo. Contacta con el administrador.", "danger")
            print(e)

        return redirect(url_for("router_index.home"))

    return render_template("auth/recuperar_contraseña.html" ,CURRENT_YEAR=inject_year()['CURRENT_YEAR'], SHORT_YEAR=inject_year()['SHORT_YEAR'])


# Función que maneja el proceso de creación de una nueva incidencia, validando los datos proporcionados, guardando la incidencia en la base de datos, 
# y devolviendo información sobre la acción realizada    

CORREO_DESTINO = 'dfernandezs@distrisantiago.es'

def f_crear_incidencia():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Petición inválida'}), 400

    titulo      = data.get('titulo', '').strip()
    descripcion = data.get('descripcion', '').strip()

    if not titulo or not descripcion:
        return jsonify({'error': 'Título y descripción son obligatorios'}), 400

    incidencia = Incidencia(
        titulo=titulo,
        descripcion=descripcion,
        usuario_id=current_user.id
    )

    db.session.add(incidencia)
    db.session.commit()

    try:
        anho      = datetime.now().year
        anho_corto = str(anho)[-2:]
        fecha_hora = datetime.now().strftime('%d/%m/%Y a las %H:%M')
        nombre_mostrar = ( current_user.nombre_empresa if current_user.rol.value == 'proveedor' else f"{current_user.nombre} {current_user.apellido1}" )
        rol = current_user.rol.value.capitalize()

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        </head>
        <body style="margin:0; padding:0; background:#111827; font-family:'Segoe UI', Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111827; padding:40px 0;">
            <tr>
            <td align="center">
                <table width="560" cellpadding="0" cellspacing="0"
                    style="background:#1F2937; border-radius:12px; border:1px solid #374151; overflow:hidden;">

                <!-- Header -->
                <tr>
                    <td style="padding:28px 32px; border-bottom:1px solid #374151; text-align:center;">
                    <span style="display:inline-block; width:10px; height:10px; border-radius:50%;
                                background:#F97316; margin-right:8px; vertical-align:middle;"></span>
                    <span style="font-size:1.4rem; font-weight:700; color:#F9FAFB;
                                letter-spacing:0.02em; vertical-align:middle;">
                        Forum <span style="color:#F97316;">{anho_corto}</span>
                    </span>
                    </td>
                </tr>

                <!-- Cuerpo -->
                <tr>
                    <td style="padding:32px 40px;">

                    <h2 style="margin:0 0 8px; font-size:1.2rem; font-weight:700; color:#F9FAFB;">
                        🛠 Nueva incidencia registrada
                    </h2>
                    <p style="margin:0 0 24px; color:#9CA3AF; font-size:0.9rem; line-height:1.7;">
                        Se ha abierto una nueva incidencia el <strong style="color:#F9FAFB;">{fecha_hora}</strong>.
                        A continuación encontrarás los detalles del reporte.
                    </p>

                    <!-- Datos de la incidencia -->
                    <div style="background:#111827; border:1px solid #374151; border-radius:8px;
                                padding:16px 20px; margin-bottom:24px;">
                        <table width="100%" cellpadding="6" cellspacing="0" style="font-size:0.88rem;">
                        <tr>
                            <td style="color:#9CA3AF; width:40%;">ID</td>
                            <td style="color:#F97316; font-weight:700; letter-spacing:0.05em;">#{incidencia.id}</td>
                        </tr>
                        <tr>
                            <td style="color:#9CA3AF;">Título</td>
                            <td style="color:#F9FAFB; font-weight:600;">{titulo}</td>
                        </tr>
                        <tr>
                            <td style="color:#9CA3AF;">Rol</td>
                            <td style="color:#F9FAFB; font-weight:600;">{rol}</td>
                        </tr>
                        <tr>
                            <td style="color:#9CA3AF;">Reportado por</td>
                            <td style="color:#F9FAFB; font-weight:600;">{nombre_mostrar}</td>
                        </tr>
                        <tr>
                            <td style="color:#9CA3AF;">Email</td>
                            <td style="color:#F9FAFB; font-weight:600;">{current_user.email}</td>
                        </tr>
                        <tr>
                            <td style="color:#9CA3AF;">Fecha</td>
                            <td style="color:#F9FAFB; font-weight:600;">{fecha_hora}</td>
                        </tr>
                        </table>
                    </div>

                    <!-- Descripción -->
                    <div style="border-left:3px solid #F97316; padding-left:16px; margin-bottom:24px;">
                        <p style="margin:0 0 6px; font-size:0.85rem; color:#F9FAFB; font-weight:600;">
                        Descripción
                        </p>
                        <p style="margin:0; font-size:0.88rem; color:#9CA3AF; line-height:1.8;">
                        {descripcion}
                        </p>
                    </div>

                    <!-- Aviso -->
                    <div style="background:rgba(249,115,22,0.08); border:1px solid rgba(249,115,22,0.2);
                                border-radius:8px; padding:12px 16px;">
                        <p style="margin:0; font-size:0.82rem; color:#FDBA74;">
                        ⚠ Accede al panel de administración para gestionar esta incidencia.
                        </p>
                    </div>

                    </td>
                </tr>

                <!-- Footer -->
                <tr>
                    <td style="padding:20px 40px; border-top:1px solid #374151; text-align:center;">
                    <p style="margin:0; font-size:0.78rem; color:#6B7280;">
                        Forum {anho_corto} — Grupo DSG &copy; {anho} &mdash;
                        Este es un correo automático, no respondas a este mensaje.
                    </p>
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </body>
        </html>
        """

        msg = Message(
            subject=f'🛠 Incidencia #{incidencia.id}: {titulo}',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[CORREO_DESTINO]
        )
        msg.html = html
        mail.send(msg)

    except Exception as e:
        current_app.logger.error(f'Error al enviar correo de incidencia #{incidencia.id}: {e}')

    return jsonify({'ok': True, 'id': incidencia.id}), 201

# Función que maneja la edición del perfil de un usuario, validando los datos proporcionados, actualizando la información del usuario en la base de datos,
# y devolviendo mensajes de éxito o error según corresponda
def f_editar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("router_index.home"))

    if request.method == 'POST':
        nombre    = request.form.get('nombre', '').strip().lower()
        apellido1 = request.form.get('apellido1', '').strip().lower()
        apellido2 = request.form.get('apellido2', '').strip().lower()
        email     = request.form.get('email', '').strip().lower()
        empresa   = request.form.get('nombre_empresa', '').strip()
        cif       = request.form.get('cif_empresa', '').strip()

        pwd_actual  = request.form.get('password_actual', '').strip()
        pwd_nueva   = request.form.get('password_nueva', '').strip()
        pwd_confirm = request.form.get('password_confirm', '').strip()

        if not nombre or not email:
            flash("El nombre y el email son obligatorios.", "error")
            return render_template("editar_usuario.html",
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        existente = Usuario.query.filter_by(email=email).first()
        if existente and existente.id != usuario_id:
            flash("Ese correo ya está en uso por otro usuario.", "error")
            return render_template("editar_usuario.html",
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        if pwd_nueva:
            if not pwd_actual:
                flash("Debes introducir tu contraseña actual para cambiarla.", "error")
                return render_template("editar_usuario.html",
                                       CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                       SHORT_YEAR=inject_year()['SHORT_YEAR'])
            if not check_password_hash(usuario.password_hash, pwd_actual):
                flash("La contraseña actual no es correcta.", "error")
                return render_template("editar_usuario.html",
                                       CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                       SHORT_YEAR=inject_year()['SHORT_YEAR'])
            if pwd_nueva != pwd_confirm:
                flash("Las contraseñas nuevas no coinciden.", "error")
                return render_template("editar_usuario.html",
                                       CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                       SHORT_YEAR=inject_year()['SHORT_YEAR'])
            if len(pwd_nueva) < 8:
                flash("La contraseña nueva debe tener al menos 8 caracteres.", "error")
                return render_template("editar_usuario.html",
                                       CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                       SHORT_YEAR=inject_year()['SHORT_YEAR'])
            usuario.password_hash = generate_password_hash(pwd_nueva)

        # Comprobar cambios de nombre ANTES de actualizar
        nombre_cambio = (
            nombre    != usuario.nombre    or
            apellido1 != usuario.apellido1 or
            apellido2 != usuario.apellido2
        )

        # Campos comunes
        usuario.nombre         = nombre
        usuario.apellido1      = apellido1
        usuario.apellido2      = apellido2
        usuario.email          = email
        usuario.nombre_empresa = empresa
        usuario.cif_empresa    = cif

        # Solo regenerar nombre_usuario si cambió nombre o apellidos
        if nombre_cambio:
            usuario.nombre_usuario = createUsername(nombre, apellido1, apellido2)

        # Campos específicos por rol
        if usuario.rol.value == 'cliente':
            usuario.codigo   = request.form.get('codigo', '').strip()
            usuario.pernocta = bool(request.form.get('pernocta'))

        elif usuario.rol.value == 'proveedor':
            usuario.codigo      = request.form.get('codigo', '').strip()
            usuario.asiste_cena = bool(request.form.get('asiste_cena'))

        # ── Acompañantes ──────────────────────────────────────────
        if usuario.rol.value in ['cliente', 'proveedor']:
            nombres    = request.form.getlist('acompanante_nombre')
            apellidos  = request.form.getlist('acompanante_apellido')
            ids        = request.form.getlist('acompanante_id')

            # IDs enviados (vacío = nuevo)
            ids_enviados = [int(i) for i in ids if i]

            # Eliminar acompañantes que ya no están en el form
            for ac in list(usuario.acompanantes):
                if ac.id not in ids_enviados:
                    db.session.delete(ac)

            for i, (ac_id, nombre_ac, apellido_ac) in enumerate(
                zip(ids, nombres, apellidos)
            ):
                nombre_ac   = nombre_ac.strip()
                apellido_ac = apellido_ac.strip()
                if not nombre_ac:
                    continue  # fila vacía, ignorar

                if ac_id:
                    # Actualizar existente
                    ac = Acompanante.query.get(int(ac_id))
                    if ac and ac.usuario_id == usuario.id:
                        ac.nombre   = nombre_ac
                        ac.apellido = apellido_ac
                        if usuario.rol.value == 'cliente':
                            pernoctas = request.form.getlist('acompanante_pernocta')
                            ac.pernocta = str(i) in pernoctas
                        elif usuario.rol.value == 'proveedor':
                            ac.asiste_cena = bool(
                                request.form.get(f'acompanante_cena_{i}')
                            )
                else:
                    # Nuevo acompañante
                    nuevo_ac = Acompanante(
                        usuario_id = usuario.id,
                        nombre     = nombre_ac,
                        apellido   = apellido_ac,
                    )
                    if usuario.rol.value == 'cliente':
                        pernoctas = request.form.getlist('acompanante_pernocta')
                        nuevo_ac.pernocta = f'new_{i}' in pernoctas
                    elif usuario.rol.value == 'proveedor':
                        nuevo_ac.asiste_cena = bool(
                            request.form.get(f'acompanante_cena_new_{i}')
                        )
                    db.session.add(nuevo_ac)

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("router_index.editar_usuario"))

    return render_template(
        "editar_usuario.html",
        CURRENT_YEAR = inject_year()['CURRENT_YEAR'],
        SHORT_YEAR   = inject_year()['SHORT_YEAR']
    )



# Función que maneja la obtención de un producto o proveedor a través de un token QR, redirigiendo a la página de detalle del producto o al 
# catálogo del proveedor según corresponda, y mostrando un mensaje de error si el token no es válido
def f_producto_por_qr(qr_token):
    # Intentar primero como producto
    producto = Producto.query.filter_by(qr_token=qr_token).first()
    if producto:
        return redirect(url_for("router_cliente.detalle_producto", producto_id=producto.id))

    # Si no es producto, comprobar si es proveedor
    proveedor = Usuario.query.filter_by(qr_token=qr_token, rol=RolEnum.proveedor).first()
    if proveedor:
        return redirect(url_for("router_cliente.catalogo", proveedor_id=proveedor.id))

    flash("QR inválido.", "danger")
    return redirect(url_for("router_cliente.catalogo"))


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════ 


# Funciones que manejan la visualización de las páginas de aviso legal, política de privacidad, y política de cookies, 
# mostrando la información correspondiente en cada caso
def f_dashboard_avisoLegal():
    return render_template("footer/aviso_legal.html") 

def f_dashboard_politicaPrivacidad():
    return render_template("footer/proteccion_datos.html")

def f_dashboard_politicaCookies():
    return render_template("footer/politica_cookies.html")