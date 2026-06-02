from models.enums import RolEnum, TipoAccesoEnum
from models.usuario import Usuario
from models.control_es import ControlES
from models.acompanante import Acompanante
from datetime import date, datetime, time
from extensions import db
from models.config import Config
from flask import flash, render_template, jsonify, redirect, request, url_for
from utils.utils import exportar_csv


# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DE NEGOCIO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja el proceso de registro de un acceso mediante código QR, validando el código, 
# registrando la entrada o salida correspondiente, y devolviendo información sobre la acción realizada
def registrar_acceso_qr(codigo_qr):


    # 1. Comprobar si es QR de acompañante
    acompanante = Acompanante.query.filter_by(qr_token=codigo_qr).first()
    if acompanante:
        return {
            "valido": True,
            "accion": "entrada",
            "usuario_id": None,
            "es_acompanante": True,
            "nombre": f"{acompanante.nombre} {acompanante.apellido}",
            "hora": datetime.now()
        }

    # 2. Buscar usuario normal por qr_token
    usuario = Usuario.query.filter_by(qr_token=codigo_qr, estado=True).first()

    if not usuario:
        return {"valido": False, "error": "QR no válido, no encontrado o usuario inactivo."}

    if not usuario.tiene_rol(RolEnum.cliente, RolEnum.control):
        return {"valido": False, "error": "Acceso denegado para este rol."}

    ultimo_registro = (
        ControlES.query
        .filter_by(usuario_id=usuario.id)
        .order_by(ControlES.hora_entrada.desc())
        .first()
    )

    ahora = datetime.now()

    if not ultimo_registro or ultimo_registro.hora_salida is not None:
        nuevo_registro = ControlES(
            usuario_id   = usuario.id,
            hora_entrada = ahora,
            tipo_acceso  = TipoAccesoEnum.qr
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        return {"valido": True, "accion": "entrada", "usuario_id": usuario.id, "hora": ahora}

    ultimo_registro.hora_salida = ahora
    db.session.commit()
    return {"valido": True, "accion": "salida", "usuario_id": usuario.id, "hora": ahora}



# Función que maneja la búsqueda de un usuario por código, permitiendo buscar tanto por código de cliente como por CIF de empresa, 
# y devolviendo el usuario encontrado o None si no se encuentra
def buscar_usuario_por_codigo(texto):
    """
    Si el texto tiene 5 caracteres busca por codigo_cliente,
    si no busca por cif_empresa.
    """
    texto = texto.strip().upper()

    if len(texto) == 5:
        usuario = Usuario.query.filter_by(codigo=texto, estado=True).first()
    else:
        usuario = Usuario.query.filter(
            Usuario.cif_empresa.ilike(texto),
            Usuario.estado == True
        ).first()

    return usuario    



# Función que maneja la validación de un código QR, verificando si el código corresponde a un usuario activo con rol permitido, 
# y devolviendo información sobre la validez del código y el usuario asociado
def validar_qr(codigo_qr):
    usuario = Usuario.query.with_entities(
        Usuario.id, Usuario.estado, Usuario.rol
    ).filter_by(qr_token=codigo_qr).first()

    if not usuario:
        return {"valido": False, "error": "QR no válido o no encontrado."}
    if not usuario.estado:
        return {"valido": False, "error": "Usuario inactivo."}

    ROLES_PERMITIDOS = {'cliente', 'control'}
    if usuario.rol not in ROLES_PERMITIDOS:
        return {"valido": False, "error": "Acceso denegado."}

    return {"valido": True, "usuario_id": usuario.id}



# Función que maneja la obtención del último acceso registrado para un usuario específico, devolviendo el registro más reciente
#  o None si no hay registros para ese usuario
def obtener_ultimo_acceso(usuario_id):
    return (
        ControlES.query
        .filter_by(usuario_id=usuario_id)
        .order_by(ControlES.hora_entrada.desc())
        .first()
    )



# Función que maneja el proceso de registro manual de una entrada para un usuario específico, validando el usuario,
#  registrando la entrada con la hora proporcionada o la hora actual, y devolviendo
def alta_entrada_manual(usuario_id, hora=None):
    if not db.session.get(Usuario, usuario_id):
        return {"error": "Usuario no válido"}
    
    nuevo_registro = ControlES(
        usuario_id   = usuario_id,
        hora_entrada = hora or datetime.now(),
        tipo_acceso  = TipoAccesoEnum.manual
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return {"accion": "entrada", "usuario_id": usuario_id, "hora": nuevo_registro.hora_entrada}



# Función que maneja el proceso de registro manual de una salida para un usuario específico, validando el usuario,
#  verificando que haya una entrada abierta para ese usuario, registrando la salida con la
def alta_salida_manual(usuario_id, hora=None):
    if not db.session.get(Usuario, usuario_id):
        return {"error": "Usuario no válido"}

    ultimo = obtener_ultimo_acceso(usuario_id)

    if not ultimo or ultimo.hora_salida is not None:
        return {"error": "No hay ninguna entrada abierta para este usuario."}

    ultimo.hora_salida = hora or datetime.now()
    db.session.commit()
    return {"accion": "salida", "usuario_id": usuario_id, "hora": ultimo.hora_salida}



# Función que maneja el proceso de corrección de un registro de acceso específico, permitiendo actualizar la hora de entrada y/o salida,
#  validando que las horas sean coherentes, y devolviendo información sobre la acción realizada
def corregir_acceso(acceso_id, nueva_hora_entrada=None, nueva_hora_salida=None):
    registro = ControlES.query.get(acceso_id)

    if not registro:
        return {"error": "Registro no encontrado."}

    if nueva_hora_entrada and nueva_hora_salida:
        if nueva_hora_entrada > nueva_hora_salida:
            return {"error": "La hora de entrada no puede ser posterior a la de salida."}

    if nueva_hora_entrada:
        registro.hora_entrada = nueva_hora_entrada

    if nueva_hora_salida:
        if nueva_hora_salida < registro.hora_entrada:
            return {"error": "La hora de salida no puede ser anterior a la de entrada."}
        registro.hora_salida = nueva_hora_salida

    db.session.commit()
    return {"accion": "corregido", "acceso_id": acceso_id}



# Función que maneja el proceso de anulación de un registro de acceso específico, eliminando el registro de la base de datos 
# y devolviendo información sobre la acción realizada
def anular_acceso(acceso_id):
    registro = ControlES.query.get(acceso_id)

    if not registro:
        return {"error": "Registro no encontrado."}

    db.session.delete(registro)
    db.session.commit()
    return {"accion": "anulado", "acceso_id": acceso_id}



# Función que maneja la obtención de un listado de accesos registrados, con filtros opcionales por fecha, usuario, empresa, y rol,
#  y devolviendo la lista de accesos que cumplen con los criterios de filtrado orden
def listar_accesos(estado=None, usuario_id=None, empresa=None, rol=None, fecha=None, as_query=False):
    query = ControlES.query.join(Usuario, ControlES.usuario_id == Usuario.id)

    if estado == "dentro":
        query = query.filter(ControlES.hora_salida.is_(None))
    elif estado == "fuera":
        query = query.filter(ControlES.hora_salida.isnot(None))

    if usuario_id:
        query = query.filter(ControlES.usuario_id == usuario_id)

    if empresa:
        query = query.filter(Usuario.nombre_empresa.ilike(f"%{empresa}%"))

    if rol:
        query = query.filter(Usuario.rol == rol)

    if fecha:
        query = query.filter(db.func.date(ControlES.hora_entrada) == fecha)

    query = query.order_by(ControlES.hora_entrada.desc())
    return query if as_query else query.all()



# Función que maneja la obtención del historial completo de accesos para un usuario específico, devolviendo el usuario y su lista de accesos ordenada por fecha
def historial_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return {"error": "Usuario no encontrado."}

    accesos = (
        ControlES.query
        .filter_by(usuario_id=usuario_id)
        .order_by(ControlES.hora_entrada.desc())
        .all()
    )
    return {"usuario": usuario, "accesos": accesos}



# Función que maneja el proceso de registro de una entrada para un invitado, incrementando el contador de invitados del día en la configuración,
#  y devolviendo el total actualizado de invitados registrados para ese día
def entrada_invitado():
    config = Config.query.filter_by(tipo="invitados_total_dia").first()

    if not config:
        config = Config(tipo="invitados_total_dia", valor=0)
        db.session.add(config)
    elif config.valor is None:
        config.valor = 0

    config.valor += 1
    db.session.commit()
    return config.valor



# Función que maneja el proceso de reseteo del contador de invitados del día, estableciendo el valor a 0 en la configuración,
#  y devolviendo información sobre la acción realizada
def resetear_invitados():
    config = Config.query.filter_by(tipo="invitados_total_dia").first()

    if config:
        config.valor = 0
        db.session.commit()

    return {"accion": "reset_invitados"}


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXTO DE TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════


# Función que construye el contexto base que necesita control.html, obteniendo la lista de accesos para una fecha específica (o sin filtrar por fecha),
#  calculando estadísticas básicas sobre los accesos, y formateando los filtros para su
ACCESOS_POR_PAGINA = 10

def _contexto_control(fecha=None, empresa=None, rol=None, page=1):
    # Query paginada (respeta todos los filtros)
    paginacion = listar_accesos(
        fecha=fecha, empresa=empresa, rol=rol, as_query=True
    ).paginate(page=page, per_page=ACCESOS_POR_PAGINA, error_out=False)

    # Stats sobre el día completo (sin filtro de empresa/rol)
    base_dia = listar_accesos(fecha=fecha, as_query=True)
    total_dia   = base_dia.count()
    con_salida  = base_dia.filter(ControlES.hora_salida.isnot(None)).count()

    config = Config.query.filter_by(tipo="invitados_total_dia").first()

    return {
        "accesos":    paginacion.items,
        "paginacion": paginacion,
        "stats": {
            "entradas": total_dia,
            "salidas":  con_salida,
            "dentro":   total_dia - con_salida,
            "invitados": config.valor if config else 0,
        },
        "filtros": {
            "fecha":   fecha.isoformat() if fecha else "",
            "empresa": empresa or "",
            "rol":     rol or "",
        },
        "now": datetime.now()
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CAPA HTTP
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del dashboard principal de control, mostrando información relevante y actualizada sobre los accesos registrados,
#  estadísticas, y filtros para la búsqueda de accesos
def f_dashboard():
    return render_template(
        "control/control.html",
        **_contexto_control()
    )



# Función que maneja el proceso de registro de una entrada para un invitado, incrementando el contador de invitados del día en la configuración,
#  y devolviendo el total actualizado de invitados registrados para ese día, mostrando la información en
def f_invitado_entrada():
    total = entrada_invitado()
    ctx   = _contexto_control()
    ctx["total_invitados"] = total
    return render_template("control/control.html", **ctx)



# Función que maneja el proceso de reseteo del contador de invitados del día, estableciendo el valor a 0 en la configuración,
#  y devolviendo información sobre la acción realizada, mostrando la información en el dashboard de control
def f_invitado_reset():
    resultado = resetear_invitados()
    return jsonify(resultado), 200



# Función que maneja el proceso de registro de un acceso mediante código QR, validando el código,
#  registrando la entrada o salida correspondiente, y devolviendo información sobre la acción realizada,
def f_qr_scan(request):
    codigo_qr = request.form.get("codigo_qr")

    if not codigo_qr:
        flash("El campo codigo_qr es obligatorio.", "danger")
        return redirect(url_for("router_control.dashboard"))

    resultado = registrar_acceso_qr(codigo_qr)
    return render_template("control/control.html", **_contexto_control(), resultado=resultado)



# Función que maneja la obtención del último acceso registrado para un usuario específico, devolviendo el registro más reciente en formato JSON,
#  o un mensaje de error si no hay registros para ese usuario
def f_ultimo_acceso(usuario_id):
    registro = obtener_ultimo_acceso(usuario_id)

    if not registro:
        return jsonify({"mensaje": "Sin registros."}), 404

    return jsonify({
        "id":           registro.id,
        "usuario_id":   registro.usuario_id,
        "hora_entrada": registro.hora_entrada.isoformat(),
        "hora_salida":  registro.hora_salida.isoformat() if registro.hora_salida else None,
        "tipo_acceso":  registro.tipo_acceso.value
    }), 200



# Función que maneja la búsqueda de un usuario por código, permitiendo buscar tanto por código de cliente como por CIF de empresa,
#  y devolviendo el usuario encontrado o un mensaje de error si no se encuentra
def f_entrada_manual(request):
    codigo = request.form.get("codigo", "").strip()
    hora   = request.form.get("hora")

    if not codigo:
        flash("Introduce un código de cliente o CIF.", "danger")
        return redirect(url_for("router_control.dashboard"))

    usuario = buscar_usuario_por_codigo(codigo)

    if not usuario:
        flash(f"No se encontró ningún usuario con el código o CIF '{codigo}'.", "danger")
        return redirect(url_for("router_control.dashboard"))

    try:
        hora = datetime.fromisoformat(hora) if hora else None
    except ValueError:
        flash("Formato de hora inválido.", "danger")
        return redirect(url_for("router_control.dashboard"))

    resultado = alta_entrada_manual(usuario.id, hora)

    if "error" in resultado:
        flash(resultado["error"], "danger")
    else:
        flash(f"Entrada registrada para {usuario.nombre} {usuario.apellido1}.", "success")

    return redirect(url_for("router_control.dashboard"))



# Función que maneja el proceso de registro de una salida para un usuario específico, validando el usuario, verificando que haya una entrada abierta para ese usuario,
#  registrando la salida con la hora proporcionada o la hora actual, y devolviendo
def f_salida_manual(request):
    usuario_id = request.form.get("usuario_id")

    if not usuario_id:
        flash("El campo usuario_id es obligatorio.", "danger")
        return redirect(url_for("router_control.dashboard"))

    try:
        usuario_id = int(usuario_id)
    except ValueError:
        flash("Formato inválido en usuario_id.", "danger")
        return redirect(url_for("router_control.dashboard"))

    resultado = alta_salida_manual(usuario_id)

    if "error" in resultado:
        flash(resultado["error"], "danger")
    else:
        flash("Salida registrada correctamente.", "success")

    return redirect(url_for("router_control.dashboard"))



# Función que maneja el proceso de corrección de un registro de acceso específico, permitiendo actualizar la hora de entrada y/o salida,
#  validando que las horas sean coherentes, y devolviendo información sobre la acción realizada
def f_corregir(acceso_id, request):
    nueva_entrada = request.form.get("nueva_hora_entrada")
    nueva_salida  = request.form.get("nueva_hora_salida")

    try:
        nueva_entrada = datetime.fromisoformat(nueva_entrada) if nueva_entrada else None
        nueva_salida  = datetime.fromisoformat(nueva_salida)  if nueva_salida  else None
    except ValueError:
        flash("Formato de hora inválido.", "danger")
        return redirect(url_for("router_control.dashboard"))

    resultado = corregir_acceso(acceso_id, nueva_entrada, nueva_salida)

    if "error" in resultado:
        flash(resultado["error"], "danger")
    else:
        flash("Registro corregido correctamente.", "success")

    return redirect(url_for("router_control.dashboard"))



# Función que maneja el proceso de anulación de un registro de acceso específico, eliminando el registro de la base de datos 
# y devolviendo información sobre la acción realizada
def f_anular(acceso_id):
    resultado = anular_acceso(acceso_id)

    if "error" in resultado:
        flash(resultado["error"], "danger")
    else:
        flash("Registro anulado correctamente.", "success")

    return redirect(url_for("router_control.dashboard"))


# Función que maneja la obtención de un listado de accesos registrados, con filtros opcionales por fecha, usuario, empresa, y rol,
#  y devolviendo la lista de accesos que cumplen con los criterios de filtrado ordenada por fecha, mostrando la información en el dashboard de control
def f_listar(request):
    page       = request.args.get("page", 1, type=int)
    estado     = request.args.get("estado", "").strip() or None
    usuario_id = request.args.get("usuario_id")
    empresa    = request.args.get("empresa", "").strip() or None
    rol        = request.args.get("rol", "").strip() or None
 
    try:
        usuario_id = int(usuario_id) if usuario_id else None
    except ValueError:
        flash("Formato inválido en usuario_id.", "danger")
        return redirect(url_for("router_control.dashboard"))
 
    # Validar estado
    if estado not in (None, "dentro", "fuera"):
        estado = None
 
    rol_enum = None
    if rol:
        try:
            rol_enum = RolEnum(rol)
        except ValueError:
            rol_enum = None
 
    # Query paginada
    paginacion = listar_accesos(
        estado=estado,
        usuario_id=usuario_id,
        empresa=empresa,
        rol=rol_enum,
        as_query=True
    ).paginate(page=page, per_page=10, error_out=False)
 
    # Stats sobre el total del día (sin filtros)
    base_dia   = listar_accesos(as_query=True)
    total_dia  = base_dia.count()
    con_salida = base_dia.filter(ControlES.hora_salida.isnot(None)).count()
 
    config = Config.query.filter_by(tipo="invitados_total_dia").first()
 
    return render_template(
        "control/control.html",
        accesos=paginacion.items,
        paginacion=paginacion,
        stats={
            "entradas": total_dia,
            "salidas":  con_salida,
            "dentro":   total_dia - con_salida,
            "invitados": config.valor if config else 0
        },
        filtros={
            "estado":  estado or "",
            "empresa": empresa or "",
            "rol":     rol or ""
        },
        now=datetime.now()
    )




# Función que maneja la obtención del historial completo de accesos para un usuario específico, devolviendo el usuario y su lista de accesos ordenada por fecha,
#  mostrando la información en formato JSON
def f_historial(usuario_id):
    resultado = historial_usuario(usuario_id)

    if "error" in resultado:
        return jsonify(resultado), 404

    usuario = resultado["usuario"]
    accesos = resultado["accesos"]

    return jsonify({
        "usuario": {
            "id":     usuario.id,
            "nombre": usuario.nombre,
            "email":  usuario.email
        },
        "accesos": [
            {
                "id":           a.id,
                "hora_entrada": a.hora_entrada.isoformat(),
                "hora_salida":  a.hora_salida.isoformat() if a.hora_salida else None,
                "tipo_acceso":  a.tipo_acceso.value
            }
            for a in accesos
        ]
    }), 200



# Función que maneja la obtención de un listado de accesos registrados, con filtros opcionales por fecha, usuario, empresa, y rol,
#  y devolviendo la lista de accesos que cumplen con los criterios de filtrado orden
def f_exportar_accesos_csv():
    accesos = listar_accesos()

    headers = [
        "ID", "Nombre", "Apellido1", "Apellido2", "Email",
        "Empresa", "Hora Entrada", "Hora Salida", "Tipo Acceso"
    ]

    def mapper(a):
        return [
            a.id,
            a.usuario.nombre,
            a.usuario.apellido1,
            a.usuario.apellido2 or '',
            a.usuario.email,
            a.usuario.nombre_empresa or '',
            a.hora_entrada.strftime('="%d/%m/%Y %H:%M"'),
            a.hora_salida.strftime('="%d/%m/%Y %H:%M"') if a.hora_salida else '',
            a.tipo_acceso.value
        ]

    return exportar_csv(accesos, headers, mapper, "historial_accesos.csv")