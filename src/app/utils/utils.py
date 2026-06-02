import base64
import csv
from datetime import datetime
import io
import tempfile
from flask_mail import Message
import qrcode
import os
from dotenv import load_dotenv
from extensions import mail

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, Table, TableStyle

from flask import Response, flash, redirect, url_for
from models.enums import RolEnum
from models.historial_stand import HistorialStand
from models.usuario import Usuario
from functools import wraps
from flask import abort
from flask_login import current_user


# CARGAR VARIABLES DE ENTORNO

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587)) 
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_SENDER_NAME = os.getenv("MAIL_SENDER_NAME")


# FUNCIONES GENERALES

def rol_requerido(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            user_role = current_user.rol
            user_role_value = user_role.value if hasattr(user_role, "value") else user_role

            if user_role_value not in roles:
                abort(403)

            return f(*args, **kwargs)

        return wrapper
    return decorator

def paginar(query, page=1, per_page=10, orden=None):

    if orden is not None:
        query = query.order_by(orden)

    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def redirigir_por_rol(usuario):

    if usuario.rol == RolEnum.admin:
        return redirect(url_for("router_admin.adminDashboard"))

    elif usuario.rol == RolEnum.control:
        return redirect(url_for("router_control.dashboard"))

    elif usuario.rol == RolEnum.comercial:
        return redirect(url_for("router_comercial.dashboard"))

    elif usuario.rol == RolEnum.proveedor:
        return redirect(url_for("router_proveedor.dashboard"))

    elif usuario.rol == RolEnum.cliente:
       return redirect(url_for("router_cliente.dashboard"))

    # fallback  
    return redirect(url_for("router_index.home"))

def comprobarContraseña(password, password_confirm):
    if password != password_confirm:
        flash("Las contraseñas no coinciden.", "danger")
        return False
    return True

def createUsername(name, surname1, surname2):

    # 🔒 seguridad contra NULL
    name = (name or "").strip()
    surname1 = (surname1 or "").strip()
    surname2 = (surname2 or "").strip()

    # 🧠 construir base de iniciales
    base = ""

    if name:
        base += name[0]

    if surname1:
        base += surname1[0]

    if surname2:
        base += surname2[0]

    base = base.upper()

    # 🔥 fallback si todo viene vacío
    if not base:
        base = "USR"

    # 🔍 buscar coincidencias EXACTAS o con sufijo
    resultados = Usuario.query.with_entities(
        Usuario.nombre_usuario
    ).filter(
        Usuario.nombre_usuario.like(f"{base}%")
    ).all()

    existentes = {r[0] for r in resultados}

    # ✔ CASO 1: no existe ninguno igual → devolver base SIN número
    if base not in existentes:
        return base
    else:
    # ✔ CASO 2: existe al menos uno → buscar sufijo SOLO entonces
        i = 1
        while f"{base}{i}" in existentes:
            i += 1

        return f"{base}{i}"



def exportar_csv(data, headers, row_mapper, filename="export.csv"):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    # Cabecera
    writer.writerow(headers)

    # Filas
    for item in data:
        writer.writerow(row_mapper(item))

    csv_bytes = output.getvalue().encode('utf-8-sig')

    return Response(
        csv_bytes,
        mimetype='text/csv; charset=utf-8',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )        


def generar_qr_imagen(token: str) -> str:
    """Genera un QR, lo guarda en archivo temporal y devuelve la ruta — para el PDF."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1F2937", back_color="#FFF")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name, format="PNG")
    tmp.close()
    return tmp.name


def _generar_qr_bytesio(token: str) -> io.BytesIO:
    """Genera un QR y devuelve un BytesIO — uso interno."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1F2937", back_color="#FFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generar_qr_imagen_64(token: str) -> str:
    """Genera un QR y devuelve base64 — para el HTML."""
    buf = _generar_qr_bytesio(token)
    return base64.b64encode(buf.getvalue()).decode("utf-8")  



# ── Paleta (del _build_pdf) ───────────────────────────────────────────────────
ORANGE     = colors.HexColor("#F97316")
ORANGE_BG  = colors.HexColor("#fff7ed")
DARK       = colors.HexColor("#111827")
MUTED      = colors.HexColor("#9CA3AF")
LIGHT_LINE = colors.HexColor("#E5E7EB")
CARD_HEAD  = colors.HexColor("#F3F4F6")
ROW_ALT    = colors.HexColor("#F9FAFB")
WHITE      = colors.white

LOGO_DSG   = "static/img/logo.png"
LOGO_FORUM = "static/img/logo_forum2026.png"
LOGO_H     = 2 * cm


# ── Estilos ───────────────────────────────────────────────────────────────────

def _styles():
    return {
        # Cabecera del documento
        "subtitle": ParagraphStyle(
            "subtitle",
            fontSize=18,
            fontName="Helvetica-Bold",
            textColor=DARK,
            spaceBefore=4,
            spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "meta",
            fontSize=9,
            fontName="Helvetica",
            textColor=MUTED,
            spaceAfter=10,
        ),
        # Sección principal (ej. "ASISTENTE")
        "section": ParagraphStyle(
            "section",
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=ORANGE,
            spaceBefore=14,
            spaceAfter=4,
            leading=14,
        ),
        # Título dentro de card (nombre del usuario)
        "card_title": ParagraphStyle(
            "card_title",
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=DARK,
            spaceAfter=2,
        ),
        # Rol (ASISTENTE / ACOMPAÑANTE)
        "card_role": ParagraphStyle(
            "card_role",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=ORANGE,
            spaceAfter=0,
            leading=11,
        ),
        # Etiquetas de metadatos (Usuario, Empresa…)
        "meta_key": ParagraphStyle(
            "meta_key",
            fontSize=8,
            fontName="Helvetica",
            textColor=MUTED,
        ),
        # Valores de metadatos
        "meta_val": ParagraphStyle(
            "meta_val",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=DARK,
            spaceAfter=2,
        ),
        # Código cliente (en naranja)
        "meta_val_orange": ParagraphStyle(
            "meta_val_orange",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=ORANGE,
            spaceAfter=2,
        ),
        # Texto de ayuda bajo el QR
        "hint": ParagraphStyle(
            "hint",
            fontSize=7.5,
            fontName="Helvetica",
            textColor=MUTED,
            spaceBefore=5,
            spaceAfter=0,
        ),
        # Subsección dentro de card (para acompañantes)
        "subsection": ParagraphStyle(
            "subsection",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=MUTED,
            spaceBefore=2,
            spaceAfter=2,
        ),
    }


# ── Header / Footer en canvas ─────────────────────────────────────────────────



def _draw_header(canv, doc):
    PAGE_W, PAGE_H = A4

    canv.saveState()

    LOGO_H_PX = LOGO_H          # 2 cm
    y_top = PAGE_H - LOGO_H_PX  # borde superior del logo

    # Ajustes manuales
    LEFT_LOGO_OFFSET = -2.5 * cm   # más hacia la izquierda
    RIGHT_LOGO_MARGIN = 0.6 * cm   # separación del borde derecho

    # ── Logo izquierda ────────────────────────────────────────────────────────
    if os.path.exists(LOGO_DSG):
        canv.drawImage(
            LOGO_DSG,
            LEFT_LOGO_OFFSET,
            y_top,
            height=LOGO_H_PX,
            preserveAspectRatio=True,
            mask="auto",
        )

    # ── Logo derecha ─────────────────────────────────────────────────────────
    if os.path.exists(LOGO_FORUM):
        try:
            from PIL import Image as PILImage
            with PILImage.open(LOGO_FORUM) as im:
                ratio = im.width / im.height
        except Exception:
            ratio = 3.0

        logo_w = LOGO_H_PX * ratio

        canv.drawImage(
            LOGO_FORUM,
            PAGE_W - logo_w - RIGHT_LOGO_MARGIN,
            y_top,
            width=logo_w,
            height=LOGO_H_PX,
            preserveAspectRatio=True,
            mask="auto",
        )

    # ── Línea separadora ─────────────────────────────────────────────────────
    line_y = y_top - 0.25 * cm
    canv.setStrokeColor(LIGHT_LINE)
    canv.setLineWidth(0.5)
    canv.line(0, line_y, PAGE_W, line_y)

    canv.restoreState()





def _draw_footer(canv, doc):
    PAGE_W, PAGE_H = A4
    MARGIN = doc.leftMargin
    anho = datetime.now().year
    anho_corto = str(anho)[-2:]

    canv.saveState()

    # Línea naranja decorativa
    canv.setStrokeColor(ORANGE)
    canv.setLineWidth(1.5)
    canv.line(MARGIN, 1.5 * cm, PAGE_W - MARGIN, 1.5 * cm)

    # Texto del pie
    canv.setFont("Helvetica", 7)
    canv.setFillColor(MUTED)
    canv.drawCentredString(
        PAGE_W / 2, 0.9 * cm,
        f"Forum {anho_corto} · Grupo DSG © {anho}  —  Credencial de acceso personal, no transferible",
    )

    canv.restoreState()


# ── Card de usuario (principal o acompañante) ─────────────────────────────────

def _render_user_card(nombre, rol, meta_rows, ruta_qr, hint_text, st, content_w, qr_size=5.5 * cm):
    """
    Devuelve una lista de elementos Platypus que forman la 'card' de un asistente
    con el mismo estilo de card que _build_pdf (cabecera gris, cuerpo en tabla,
    borde naranja, etc.).
    """
    elements = []

    # ── Cabecera de la card (nombre + rol sobre fondo gris) ───────────────────
    h_tbl = Table(
        [[
            Paragraph(nombre, st["card_title"]),
            Paragraph(rol, st["card_role"]),
        ]],
        colWidths=[content_w * 0.72, content_w * 0.28],
    )
    h_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CARD_HEAD),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, -1), 1, LIGHT_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
    ]))
    elements.append(h_tbl)

    # ── Cuerpo: metadatos a la izquierda, QR a la derecha ────────────────────
    COL_L = content_w * 0.55
    COL_R = content_w * 0.45

    # Columna izquierda: pares clave/valor
    meta_story = []
    for key, val, orange in meta_rows:
        meta_story.append(Paragraph(key, st["meta_key"]))
        style = st["meta_val_orange"] if orange else st["meta_val"]
        meta_story.append(Paragraph(val, style))

    meta_cell = meta_story  # lista de Paragraphs que Platypus apila

    # Columna derecha: imagen QR con marco fino
    qr_box_size = qr_size + 0.8 * cm
    qr_img = Image(ruta_qr, width=qr_size, height=qr_size)
    qr_inner = Table(
        [[qr_img]],
        colWidths=[qr_box_size],
        rowHeights=[qr_box_size],
    )
    qr_inner.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOX",           (0, 0), (-1, -1), 0.75, LIGHT_LINE),
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ]))

    hint_para = Paragraph(hint_text, st["hint"])

    right_cell = [qr_inner, hint_para]

    body_tbl = Table(
        [[meta_cell, right_cell]],
        colWidths=[COL_L, COL_R],
    )
    body_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (0, 0),   "MIDDLE"),
        ("VALIGN",        (1, 0), (1, 0),   "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "CENTER"),
        ("LINEBELOW",     (0, 0), (-1, -1), 1.5, ORANGE),
    ]))
    elements.append(body_tbl)
    elements.append(Spacer(1, 14))

    return elements


# ── Función principal ─────────────────────────────────────────────────────────

def _generar_pdf(usuario, acompanantes: list) -> bytes:
    buf = io.BytesIO()
    W, H = A4
    MARGIN = 20 * mm

    # topMargin debe superar: MARGIN(20mm) + LOGO_H(1.6cm) + línea(0.4cm) + holgura(0.4cm) ≈ 4.4cm
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=3.1 * cm,
        bottomMargin=20 * mm,
        title="Credencial de acceso — DSG Forum",
    )

    st = _styles()
    story = []
    content_w = W - 2 * MARGIN
    tmp_files = []

    # ── Cabecera del documento ────────────────────────────────────────────────
    anho = datetime.now().year
    nombre_proveedor = getattr(usuario, "nombre", None) or usuario.email

    story.append(Paragraph("Credencial de acceso", st["subtitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"Usuario: <b>{nombre_proveedor}</b>",
        st["meta"],
    ))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        st["meta"],
    ))
    story.append(HRFlowable(
        width=content_w, color=ORANGE, thickness=2, spaceAfter=16,
    ))

    # ── Sección: Asistente principal ──────────────────────────────────────────
    story.append(Paragraph("Asistente", st["section"]))
    story.append(HRFlowable(
        width=content_w, color=LIGHT_LINE, thickness=1, spaceAfter=8,
    ))

    nombre_completo = f"{usuario.nombre.capitalize()} {usuario.apellido1.capitalize()}"
    if usuario.apellido2:
        nombre_completo += f" {usuario.apellido2.capitalize()}"

    meta_rows = []
    if usuario.nombre_usuario:
        meta_rows.append(("Usuario", usuario.nombre_usuario, False))
    if getattr(usuario, "nombre_empresa", None):
        meta_rows.append(("Empresa", usuario.nombre_empresa, False))
    if getattr(usuario, "codigo", None):
        meta_rows.append(("Código cliente", usuario.codigo, True))  # naranja

    ruta_qr = generar_qr_imagen(usuario.qr_token)
    tmp_files.append(ruta_qr)

    story += _render_user_card(
        nombre=nombre_completo,
        rol="ASISTENTE",
        meta_rows=meta_rows,
        ruta_qr=ruta_qr,
        hint_text="Presenta este código en el control de accesos",
        st=st,
        content_w=content_w,
        qr_size=5.5 * cm,
    )

    # ── Sección: Acompañantes ─────────────────────────────────────────────────
    if acompanantes:
        story.append(Paragraph("Acompañantes", st["section"]))
        story.append(HRFlowable(
            width=content_w, color=LIGHT_LINE, thickness=1, spaceAfter=8,
        ))

        for ac in acompanantes:
            nombre_ac = f"{ac.nombre.capitalize()} {ac.apellido.capitalize()}"

            meta_rows_ac = []
            if getattr(ac, "empresa", None):
                meta_rows_ac.append(("Empresa", ac.empresa, False))

            ruta_qr_ac = generar_qr_imagen(ac.qr_token)
            tmp_files.append(ruta_qr_ac)

            story += _render_user_card(
                nombre=nombre_ac,
                rol="ACOMPAÑANTE",
                meta_rows=meta_rows_ac,
                ruta_qr=ruta_qr_ac,
                hint_text="Acompañante · Control de accesos",
                st=st,
                content_w=content_w,
                qr_size=4.0 * cm,
            )

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(
        story,
        onFirstPage=lambda c, d: (_draw_header(c, d), _draw_footer(c, d)),
        onLaterPages=lambda c, d: (_draw_header(c, d), _draw_footer(c, d)),
    )

    for ruta in tmp_files:
        try:
            os.remove(ruta)
        except OSError:
            pass

    buf.seek(0)
    return buf.read()

def correo_confirmacion_registro(usuario, acompanantes: list = None) -> bool:
    if acompanantes is None:
        acompanantes = []

    anho = datetime.now().year
    anho_corto = str(anho)[-2:]
    nombre_mostrar = f"{usuario.nombre.capitalize()} {usuario.apellido1.capitalize()}"

    n_acompanantes = len(acompanantes)
    info_acompanantes = (
        f"<p>Junto a tu credencial encontrarás también los QR de tus "
        f"<strong>{n_acompanantes} acompañante{'s' if n_acompanantes != 1 else ''}</strong>.</p>"
        if n_acompanantes > 0 else ""
    )

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
                    ¡Registro completado, {nombre_mostrar}!
                </h2>
                <p style="margin:0 0 20px; color:#9CA3AF; font-size:0.9rem; line-height:1.7;">
                    Tu cuenta en <strong style="color:#F9FAFB;">Forum {anho_corto}</strong> ha sido creada correctamente.
                    Adjunto a este correo encontrarás tu credencial de acceso en PDF con tu código QR personal.
                </p>

                {info_acompanantes}

                <!-- Datos del usuario -->
                <div style="background:#111827; border:1px solid #374151; border-radius:8px;
                            padding:16px 20px; margin-bottom:24px;">
                    <table width="100%" cellpadding="6" cellspacing="0" style="font-size:0.88rem;">
                    <tr>
                        <td style="color:#9CA3AF; width:40%;">Nombre</td>
                        <td style="color:#F9FAFB; font-weight:600;">{nombre_mostrar}</td>
                    </tr>
                    <tr>
                        <td style="color:#9CA3AF;">Usuario</td>
                        <td style="color:#F9FAFB; font-weight:600;">{usuario.nombre_usuario}</td>
                    </tr>
                    <tr>
                        <td style="color:#9CA3AF;">Email</td>
                        <td style="color:#F9FAFB; font-weight:600;">{usuario.email}</td>
                    </tr>
                    {"<tr><td style='color:#9CA3AF;'>Empresa</td><td style='color:#F9FAFB; font-weight:600;'>" + usuario.nombre_empresa + "</td></tr>" if usuario.nombre_empresa else ""}
                    {"<tr><td style='color:#9CA3AF;'>Código cliente</td><td style='color:#F97316; font-weight:700; letter-spacing:0.05em;'>" + (usuario.codigo or '') + "</td></tr>" if usuario.codigo else ""}
                    </table>
                </div>

                {f'''
                <!-- Acompañantes -->
                <div style="background:rgba(52,211,153,0.05); border:1px solid rgba(52,211,153,0.2);
                            border-radius:8px; padding:12px 16px; margin-bottom:24px;">
                    <p style="margin:0; font-size:0.85rem; color:#6EE7B7;">
                    <strong>👥 {n_acompanantes} acompañante{"s" if n_acompanantes != 1 else ""} registrado{"s" if n_acompanantes != 1 else ""}</strong>
                    — Sus QR también están incluidos en el PDF adjunto.
                    </p>
                </div>
                ''' if n_acompanantes > 0 else ""}

                <!-- Instrucciones -->
                <div style="border-left:3px solid #F97316; padding-left:16px; margin-bottom:24px;">
                    <p style="margin:0 0 8px; font-size:0.85rem; color:#9CA3AF; line-height:1.7;">
                    <strong style="color:#F9FAFB;">¿Cómo usar tu QR?</strong>
                    </p>
                    <p style="margin:0; font-size:0.83rem; color:#9CA3AF; line-height:1.8;">
                    1. Descarga e imprime el PDF adjunto o tenlo disponible en tu móvil.<br/>
                    2. Muestra el código QR al lector en el control de accesos.<br/>
                    3. El primer escaneo registra tu <strong style="color:#F9FAFB;">entrada</strong>
                        y el segundo tu <strong style="color:#F9FAFB;">salida</strong>.
                    </p>
                </div>

                <!-- Aviso -->
                <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2);
                            border-radius:8px; padding:12px 16px;">
                    <p style="margin:0; font-size:0.82rem; color:#FCA5A5;">
                    ⚠ Si no has solicitado este registro, contacta con el equipo organizador inmediatamente.
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

    # ── Generar PDF con los QR ────────────────────────────────────────────────
    try:
        pdf_bytes = _generar_pdf(usuario, acompanantes)
    except Exception as e:
        print(f"[correo_confirmacion_registro] Error generando PDF: {e}")
        return False

    # ── Construir y enviar con flask_mail ─────────────────────────────────────
    try:
        msg = Message(
            subject=f"Forum {anho_corto} — Confirmación de registro y credencial QR",
            recipients=[usuario.email],
            html=html,
        )

        msg.attach(
            filename=f"credencial_forum{anho_corto}_{usuario.nombre_usuario}.pdf",
            content_type="application/pdf",
            data=pdf_bytes,
        )

        mail.send(msg)
        return True

    except Exception as e:
        print(f"[correo_confirmacion_registro] Error enviando correo: {e}")
        return False


def inject_year():
    now = datetime.now()

    year = now.year + 1 if now.month >= 6 else now.year

    return {
        'CURRENT_YEAR': year,
        'SHORT_YEAR': str(year)[-2:]
    }
    
def registrar_historial(
    stand_id,
    accion,
    estado_anterior=None,
    estado_nuevo=None,
    solicitud_origen=None,
    solicitud_destino=None,
    usuario_origen=None,
    usuario_destino=None,
    observacion=None
):
    return HistorialStand(
        stand_id=stand_id,
        accion=accion,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        solicitud_origen_id=solicitud_origen,
        solicitud_destino_id=solicitud_destino,
        usuario_origen_id=usuario_origen,
        usuario_destino_id=usuario_destino,
        observacion=observacion,
        fecha=datetime.now()
    )
