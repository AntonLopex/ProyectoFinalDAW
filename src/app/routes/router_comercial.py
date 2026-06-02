from flask import Blueprint, request
from flask_login import current_user, login_required
from routes.comercial.f_comercial import (
    f_editar_pedido,
    f_mi_qr_comercial,
    f_obtener_mis_clientes,
    f_obtener_detalle_cliente,
    f_crear_cliente,
    f_actualizar_cliente,
    f_obtener_pedidos_por_comercial,
    f_obtener_detalle_pedido,
    f_comercial,
    f_catalogo_productos, 
    f_detalle_producto,
    f_registo_comercial
)
from utils.utils import rol_requerido

routerComercial = Blueprint('router_comercial', __name__)


@routerComercial.route("/comercial", methods=["GET"])
@rol_requerido("comercial")
@login_required
def dashboard():
    return f_comercial()


@routerComercial.route("/comercial/clientes", methods=["GET"])
@rol_requerido("comercial")
@login_required
def mis_clientes():
    return f_obtener_mis_clientes(current_user.id, request)


@routerComercial.route("/comercial/clientes/<int:cliente_id>", methods=["GET"])
@rol_requerido("comercial")
@login_required
def detalle_cliente(cliente_id):
    return f_obtener_detalle_cliente(cliente_id, current_user.id)


@routerComercial.route("/comercial/clientes/crear", methods=["POST"])
@rol_requerido("comercial")
@login_required
def crear_cliente():
    data = request.form
    return f_crear_cliente(data, current_user.id)


@routerComercial.route("/comercial/clientes/<int:cliente_id>/actualizar", methods=["POST"])
@rol_requerido("comercial")
@login_required
def actualizar_cliente(cliente_id):
    data = request.form
    return f_actualizar_cliente(cliente_id, data, current_user.id)


@routerComercial.route("/comercial/pedidos", methods=["GET"])
# @rol_requerido("comercial")
# @login_required
def mis_pedidos():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin    = request.args.get("fecha_fin")
    cliente_id   = request.args.get("cliente_id", type=int)
    return f_obtener_pedidos_por_comercial(current_user.id, fecha_inicio, fecha_fin, cliente_id)


@routerComercial.route("/comercial/pedidos/<int:pedido_id>", methods=["GET"])
@rol_requerido("comercial")
@login_required
def detalle_pedido(pedido_id):
    return f_obtener_detalle_pedido(pedido_id, current_user.id)



@routerComercial.route("/comercial/catalogo", methods=["GET"])
@login_required
@rol_requerido("comercial")
def catalogo():
    return f_catalogo_productos()


@routerComercial.route("/comercial/catalogo/<int:producto_id>", methods=["GET"])
@login_required
@rol_requerido("comercial")
def detalle_producto(producto_id):
    return f_detalle_producto(producto_id)


@routerComercial.route("/registrar/comercial", methods=["GET", "POST"])
def registro_comercial():
    return f_registo_comercial()


@routerComercial.route("/comercial/pedidos/<int:pedido_id>/editar", methods=["POST"])
@login_required
def editar_pedido(pedido_id):
    return f_editar_pedido(pedido_id, comercial_id=current_user.id)

@routerComercial.route("/comercial/qr", methods=["GET"])
@rol_requerido("comercial")
@login_required
def mi_qr():
    return f_mi_qr_comercial(current_user.id)