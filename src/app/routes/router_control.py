from flask import Blueprint, request
from flask_login import login_required
from routes.control.f_control import (
    f_invitado_entrada,
    f_qr_scan,
    f_ultimo_acceso,
    f_entrada_manual,
    f_salida_manual,
    f_corregir,
    f_anular,
    f_listar,
    f_historial,
    f_dashboard,
    f_invitado_reset,
    f_exportar_accesos_csv
)
from utils.utils import rol_requerido

routerControl = Blueprint('router_control', __name__)


@routerControl.route("/control", methods=["GET", "POST"])
@rol_requerido("control")
@login_required
def dashboard():
    return f_dashboard()


@routerControl.route("/control/qr", methods=["POST"])
@rol_requerido("control", "proveedor", "comercial", "cliente")
@login_required
def qr_scan():
    return f_qr_scan(request)


@routerControl.route("/control/ultimo/<int:usuario_id>", methods=["GET"])
@rol_requerido("control")
@login_required
def ultimo_acceso(usuario_id):
    return f_ultimo_acceso(usuario_id)


@routerControl.route("/control/entrada", methods=["POST"])
@rol_requerido("control")
@login_required
def entrada_manual():
    return f_entrada_manual(request)


@routerControl.route("/control/salida", methods=["POST"])
@rol_requerido("control")
@login_required
def salida_manual():
    return f_salida_manual(request)


@routerControl.route("/control/corregir/<int:acceso_id>", methods=["POST"])
@rol_requerido("control")
@login_required
def corregir(acceso_id):
    return f_corregir(acceso_id, request)


@routerControl.route("/control/anular/<int:acceso_id>", methods=["POST"])
@rol_requerido("control")
@login_required
def anular(acceso_id):
    return f_anular(acceso_id)


@routerControl.route("/control/listar", methods=["GET"])
@rol_requerido("control")
@login_required
def listar():
    return f_listar(request)


@routerControl.route("/control/historial/<int:usuario_id>", methods=["GET"])
@rol_requerido("control")
@login_required
def historial(usuario_id):
    return f_historial(usuario_id)


@routerControl.route("/control/invitado/entrada", methods=["GET", "POST"])
@rol_requerido("control")
@login_required
def invitado_entrada():
    return f_invitado_entrada()


@routerControl.route("/control/invitado/reset", methods=["POST"])
@rol_requerido("control")
@login_required
def invitado_reset():
    return f_invitado_reset()


@routerControl.route("/control/exportar", methods=["GET"])
@rol_requerido("control")
@login_required
def exportar_accesos():
    return f_exportar_accesos_csv()