from flask import Blueprint, request
from flask_login import login_required, current_user
from routes.cliente.f_cliente import (
    f_cancelar_inscripcion,
    f_dashboard_cliente,
    f_inscribirse,
    f_mi_qr,
    f_catalogo_cliente,
    f_detalle_producto_cliente,
    f_presentaciones_cliente,
    f_registro,
    f_scan_producto_qr,
    f_scan_proveedor_qr,
    f_ver_carrito,
    f_añadir_al_carrito,
    f_actualizar_carrito,
    f_vaciar_carrito,
    f_confirmar_pedido,
    f_mis_pedidos,
    f_detalle_pedido_cliente,
    f_ver_mapa,
    f_ver_mapa_data
)
from utils.utils import rol_requerido

routerCliente = Blueprint('router_cliente', __name__)

@routerCliente.route("/registrar/cliente", methods=["GET", "POST"])
def registro():
    return f_registro()


@routerCliente.route("/cliente", methods=["GET"])
@login_required
@rol_requerido("cliente")
def dashboard():
    return f_dashboard_cliente(current_user.id)


@routerCliente.route("/cliente/qr", methods=["GET"])
@rol_requerido("cliente")
@login_required
def mi_qr(): 
    return f_mi_qr(current_user.id)


@routerCliente.route("/cliente/catalogo", methods=["GET"])
@rol_requerido("cliente")
@login_required
def catalogo():
    return f_catalogo_cliente()


@routerCliente.route("/cliente/catalogo/<int:producto_id>", methods=["GET"])
@rol_requerido("cliente")
@login_required
def detalle_producto(producto_id):
    return f_detalle_producto_cliente(producto_id)


@routerCliente.route("/cliente/carrito", methods=["GET"])
@rol_requerido("cliente")
@login_required
def carrito():
    return f_ver_carrito()


@routerCliente.route("/cliente/carrito/añadir", methods=["POST"])
@rol_requerido("cliente")
@login_required
def añadir_al_carrito():
    return f_añadir_al_carrito(request)


@routerCliente.route("/cliente/carrito/actualizar", methods=["POST"])
@rol_requerido("cliente")
@login_required
def actualizar_carrito():
    return f_actualizar_carrito(request)


@routerCliente.route("/cliente/carrito/vaciar", methods=["POST"])
@rol_requerido("cliente")
@login_required
def vaciar_carrito():
    return f_vaciar_carrito()


@routerCliente.route("/cliente/carrito/confirmar", methods=["POST"])
@rol_requerido("cliente")
@login_required
def confirmar_pedido():
    return f_confirmar_pedido(current_user.id)


@routerCliente.route("/cliente/pedidos", methods=["GET"])
@rol_requerido("cliente")
@login_required
def mis_pedidos():
    return f_mis_pedidos(current_user.id)


@routerCliente.route("/cliente/pedidos/<int:pedido_id>", methods=["GET"])
@rol_requerido("cliente")
@login_required
def detalle_pedido(pedido_id):
    return f_detalle_pedido_cliente(pedido_id, current_user.id)


@routerCliente.route("/presentaciones")
@login_required
@rol_requerido("cliente")
def presentaciones():
    return f_presentaciones_cliente()


@routerCliente.route("/presentaciones/<int:presentacion_id>/inscribirse", methods=["POST"])
@login_required
@rol_requerido("cliente")
def inscribirse(presentacion_id):
    return f_inscribirse(presentacion_id)


@routerCliente.route("/presentaciones/<int:presentacion_id>/cancelar", methods=["POST"])
@login_required
@rol_requerido("cliente")
def cancelar_inscripcion(presentacion_id):
    return f_cancelar_inscripcion(presentacion_id)

@routerCliente.route("/cliente/mapa", methods=["GET"])
@login_required
@rol_requerido("cliente","admin","proveedor")
def mapa():
    return f_ver_mapa()

@routerCliente.route("/cliente/mapa/data", methods=["GET"])
@login_required
@rol_requerido("cliente","admin","proveedor")
def mapa_data():
    return f_ver_mapa_data()

@routerCliente.route("/cliente/scan/producto/<string:token>")
@login_required
@rol_requerido("cliente")
def scan_producto_qr(token):
    return f_scan_producto_qr(token)

@routerCliente.route("/cliente/scan/proveedor/<string:token>")
@login_required
@rol_requerido("cliente")
def scan_proveedor_qr(token):
    return f_scan_proveedor_qr(token)