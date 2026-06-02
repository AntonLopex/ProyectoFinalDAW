from flask import Blueprint
from flask_login import current_user, login_required
from routes.proveedor.f_proveedor import (
    f_mi_qr_proveedor,
    f_mis_solicitudes,
    f_proveedor,
    f_listar_productos_propios, 
    f_detalle_producto,
    f_registro_proveedor,
    f_mapa_stands,
    f_obtener_estado_stands,
    f_confirmar_pedido,
    f_catalogo_mobiliario,
    f_confirmar_mobiliario,
    f_get_solicitud_actual,
    
)
from utils.utils import rol_requerido 


routerProveedor = Blueprint('router_proveedor', __name__)



@routerProveedor.route("/proveedor", methods=["GET", "POST"])
@rol_requerido("proveedor")
@login_required
def dashboard():
    return f_proveedor()

@routerProveedor.route("/proveedor/qr", methods=["GET"])
@login_required
@rol_requerido("proveedor")
def mi_qr():
    return f_mi_qr_proveedor(current_user.id)    


@routerProveedor.route("/proveedor/productos", methods=["GET"])
@login_required
@rol_requerido("proveedor")
def productos():
    return f_listar_productos_propios()


@routerProveedor.route("/proveedor/productos/<int:producto_id>", methods=["GET"])
@rol_requerido("proveedor")
@login_required
def detalle_producto(producto_id):
    return f_detalle_producto(producto_id)


@routerProveedor.route("/registrar/proveedor", methods=["GET", "POST"])
def registro_proveedor():
    return f_registro_proveedor()


@routerProveedor.route("/proveedor/stands", methods=["GET"])
@login_required
@rol_requerido("proveedor")
def mapa_stands():
    return f_mapa_stands()

@routerProveedor.route("/proveedor/solicitudes", methods=["GET"])
@login_required
@rol_requerido("proveedor")
def mis_solicitudes():
    return f_mis_solicitudes(current_user.id)

@routerProveedor.route("/proveedor/api/stands/estado")
@login_required
@rol_requerido("proveedor")
def obtener_estado_stands():
    return f_obtener_estado_stands()

@routerProveedor.route("/proveedor/api/stands/confirmar", methods=["POST"])
@login_required
@rol_requerido("proveedor")
def confirmar_pedido():
    return f_confirmar_pedido()

@routerProveedor.route("/proveedor/mobiliario/catalogo")
@login_required
@rol_requerido("proveedor")
def catalogo_mobiliario():
    return f_catalogo_mobiliario()

@routerProveedor.route("/proveedor/api/mobiliario/confirmar", methods=["POST"])
@login_required
@rol_requerido("proveedor")
def confirmar_mobiliario():
    return f_confirmar_mobiliario()

@routerProveedor.route("/api/solicitud/actual", methods=["GET"])
@login_required
@rol_requerido("proveedor")
def get_solicitud_actual():
    return f_get_solicitud_actual()


