from flask import Blueprint, flash, jsonify, redirect, request, url_for
from flask_login import login_required
from utils.utils import rol_requerido
from routes.admin.f_admin import (
    f_api_acompanantes_cliente,
    f_api_acompanantes_proveedor,
    f_api_inscritos_presentacion,
    f_api_presentacion_json,
    f_aplica_descuento,
    f_cambiar_estado_incidencia,
    f_cambiar_estado_pedido,
    f_cambiar_estado_solicitud,
    f_cambiar_fecha_forum,
    f_crear_mobiliario,
    f_crear_presentacion,
    f_crear_tarjeta_rol,
    f_crearUsuarioProveedor,
    f_detalle_pedido_admin,
    f_detalle_producto,
    f_editar_mobiliario,
    f_editar_pedido_admin,
    f_editar_presentacion,
    f_editarUsuarioProveedor,
    f_eliminar_incidencia,
    f_eliminar_mobiliario,
    f_eliminar_pedido,
    f_eliminar_presentacion,
    f_eliminarUsuarioProveedor,
    f_exportar_pedidos_csv,
    f_generar_etiquetas_proveedores,
    f_generar_pdf_qrs,
    f_guardar_precio_extra,
    f_importar_productos,
    f_adminDashboard,
    f_eliminarUsuarioComercial,
    f_listado_descuento,
    f_listado_solicitudes,
    f_listar_incidencias,
    f_listar_mobiliario,
    f_listar_pedidos,
    f_listar_presentaciones,
    f_listarUsuariosControl,
    f_crearUsuarioControl,
    f_listarUsuariosProveedor,
    f_obtenerUsuarioControl,
    f_editarUsuarioControl,
    f_obtenerUsuarioEliminar,
    f_eliminarUsuarioControl,
    f_listarUsuariosComercial,
    f_api_clientes_comercial,
    f_editarUsuarioComercial,
    f_crearUsuarioComercial,
    f_buscar_clientes_libres,
    f_listarUsuariosCliente,
    f_eliminarUsuarioCliente,
    f_editarUsuarioCliente,
    f_crearUsuarioCliente,
    f_obtenerUsuarioCliente,
    f_obtenerUsuarioProveedor,
    f_catalogo_productos,
    f_detalle_producto, 
    f_crear_producto,
    f_editar_producto,
    f_eliminar_producto,
    f_pedido_json,
    f_ver_mapa,
    f_actualizar_stands,
    f_historial_stands,
    f_exportar_excel_historial,
    f_exportar_pdf_historial,
    f_asignar_stand_proveedor,
    f_proveedores_disponibles,
    f_contar_incidencias_pendientes,
    f_descargar_plantilla_productos,
    f_generar_pdf_solicitudes,
    f_cambiar_fecha_fin_reservas
)

routerAdmin = Blueprint('router_admin', __name__)



@routerAdmin.route("/admin/dashboard")
@rol_requerido('admin')
@login_required
def adminDashboard():
    return f_adminDashboard()

#/=========================================================\
# Rutas para el panel de administración USUARIO CONTROL     #
#\=========================================================/

@routerAdmin.route("/admin/dashboard/usuario-control/ver")
@rol_requerido('admin')
@login_required
def listarUsuariosControl():
    return f_listarUsuariosControl()

@routerAdmin.route("/admin/dashboard/usuario-control/crear", methods=["GET", "POST"])
@rol_requerido('admin')
@login_required
def crearUsuarioControl():
    return f_crearUsuarioControl()

@routerAdmin.route("/admin/dashboard/usuario-control/<int:id>", methods=["GET"])
@rol_requerido('admin')
@login_required
def obtenerUsuarioControl(id):
    return f_obtenerUsuarioControl(id)


@routerAdmin.route("/admin/dashboard/usuario-control/editar", methods=["POST", "GET"])
@rol_requerido('admin')
@login_required
def editarUsuarioControl():
    return f_editarUsuarioControl()

@routerAdmin.route("/admin/dashboard/usuario-control/eliminar/<int:id>", methods=["GET"])
@rol_requerido('admin')
@login_required
def obtenerUsuarioEliminar(id):
    return f_obtenerUsuarioEliminar(id)

@routerAdmin.route("/admin/dashboard/usuario-control/eliminar", methods=["POST"])
@rol_requerido('admin')
@login_required
def eliminarUsuarioControl():
    return f_eliminarUsuarioControl()

#/=========================================================\
# Rutas para el panel de administración USUARIO COMERCIAL   #
#\=========================================================/

@routerAdmin.route("/admin/dashboard/usuario-comercial/ver")
@login_required
@rol_requerido('admin')
def listarUsuariosComercial():
    return f_listarUsuariosComercial()

@routerAdmin.route("/admin/api/comercial/<int:comercial_id>/clientes")
@login_required
@rol_requerido('admin')
def api_clientes_comercial(comercial_id):
    return f_api_clientes_comercial(comercial_id)

@routerAdmin.route("/admin/dashboard/usuario-comercial/editar/<int:id>", methods=["GET", "POST"])
@rol_requerido('admin')
@login_required
def editarUsuarioComercial(id):
    return f_editarUsuarioComercial(id)

@routerAdmin.route("/admin/dashboard/usuario-comercial/eliminar/<int:id>", methods=["POST"])
@rol_requerido('admin')
@login_required
def eliminarUsuarioComercial(id):
    return f_eliminarUsuarioComercial(id)

@routerAdmin.route("/admin/dashboard/usuario-comercial/crear", methods=["GET", "POST"])
@rol_requerido('admin')
@login_required
def crearUsuarioComercial():
    return f_crearUsuarioComercial()

@routerAdmin.route("/admin/api/clientes/libres")
@login_required
def buscar_clientes_libres():
    return f_buscar_clientes_libres()

#/=========================================================\
# Rutas para el panel de administración USUARIO CLIENTE     #
#\=========================================================/

@routerAdmin.route("/admin/dashboard/usuario-cliente/ver")
@rol_requerido('admin')
@login_required 
def listarUsuariosCliente():
    return f_listarUsuariosCliente()

@routerAdmin.route("/admin/dashboard/usuario-cliente/eliminar/<int:id>", methods=["POST"])
@rol_requerido('admin')
@login_required
def eliminarUsuarioCliente(id):
    return f_eliminarUsuarioCliente(id)

@routerAdmin.route("/admin/dashboard/usuario-cliente/editar/<int:id>", methods=["GET", "POST"])
@rol_requerido('admin')
@login_required
def editarUsuarioCliente(id):
    return f_editarUsuarioCliente(id)

@routerAdmin.route("/admin/dashboard/usuario-cliente/crear", methods=["GET", "POST"])
@rol_requerido('admin')
@login_required
def crearUsuarioCliente():
    return f_crearUsuarioCliente()

@routerAdmin.route("/admin/dashboard/usuario-cliente/<int:id>", methods=["GET"])
@rol_requerido('admin')
@login_required
def obtenerUsuarioCliente(id):
    return f_obtenerUsuarioCliente(id)    


#/=========================================================\
# Ruta para la importación de productos con CSV    #
#\=========================================================/

@routerAdmin.route("/admin/dashboard/usuario-cliente/importar", methods=["POST"])
@rol_requerido("admin")
@login_required
def importar_productos_csv():
    archivo = request.files.get("csv_file")

    ok, errores, insertados, codigos_fallidos = f_importar_productos(archivo)

    if not ok:
        return jsonify({
            "ok": False,
            "message": errores[0] if errores else "No se pudo importar el CSV.",
            "insertados": insertados,
            "fallidos": len(codigos_fallidos),
            "codigos_fallidos": codigos_fallidos,
            "errores": errores
        }), 400

    fallidos = len(codigos_fallidos)

    if fallidos > 0:
        return jsonify({
            "ok": True,
            "message": "Importación parcial completada.",
            "insertados": insertados,
            "fallidos": fallidos,
            "codigos_fallidos": codigos_fallidos,
            "errores": errores
        }), 207

    return jsonify({
        "ok": True,
        "message": "Productos insertados correctamente.",
        "insertados": insertados,
        "fallidos": 0,
        "codigos_fallidos": [],
        "errores": []
    }), 200
    
    
@routerAdmin.route("/admin/dashboard/usuario-cliente/descargar-plantilla", methods=["GET"])
@rol_requerido("admin")
@login_required
def descargar_plantilla_productos():
    return f_descargar_plantilla_productos()

#/=========================================================\
# Rutas para el panel de administración USUARIO PROVEEDOR     #
#\=========================================================/

@routerAdmin.route("/admin/dashboard/usuario-proveedor/ver")
@rol_requerido('admin')
@login_required
def listarUsuariosProveedor():
    return f_listarUsuariosProveedor()

@routerAdmin.route("/admin/dashboard/usuario-proveedor/crear", methods=["GET", "POST"])
@rol_requerido('admin')
@login_required
def crearUsuarioProveedor():
    return f_crearUsuarioProveedor()

@routerAdmin.route("/admin/dashboard/usuario-proveedor/<int:id>", methods=["GET"])
@rol_requerido('admin')
@login_required
def obtenerUsuarioProveedor(id):
    return f_obtenerUsuarioProveedor(id)

@routerAdmin.route("/admin/dashboard/usuario-proveedor/editar/<int:id>", methods=["POST"])
@rol_requerido('admin')
@login_required
def editarUsuarioProveedor(id):
    return f_editarUsuarioProveedor(id)

@routerAdmin.route("/admin/dashboard/usuario-proveedor/eliminar/<int:id>", methods=["POST"])
@rol_requerido('admin')
@login_required
def eliminarUsuarioProveedor(id):
    return f_eliminarUsuarioProveedor(id)

@routerAdmin.route("/admin/dashboard/proveedores/etiquetas")
@login_required
def generar_etiquetas_proveedores():
    return f_generar_etiquetas_proveedores()

#/=========================================================\
# GESTIONAR ACOMPAÑANTES    #
#\=========================================================/

@routerAdmin.route("/admin/api/proveedor/<int:proveedor_id>/acompanantes")
@rol_requerido('admin')
@login_required
def api_acompanantes_proveedor(proveedor_id):
    return f_api_acompanantes_proveedor(proveedor_id)

@routerAdmin.route("/admin/api/cliente/<int:cliente_id>/acompanantes")
@rol_requerido('admin')
@login_required
def api_acompanantes_cliente(cliente_id):
    return f_api_acompanantes_cliente(cliente_id)


#/=========================================================\
# Rutas para el panel de administración PRODUCTOS  #
#\=========================================================/

@routerAdmin.route("/admin/dashboard/catalogo_productos" , methods=["GET"])
@rol_requerido('admin')
@login_required
def catalogo_productos():
    return f_catalogo_productos()


@routerAdmin.route("/admin/dashboard/catalogo_productos/<int:producto_id>", methods=["GET"])
@rol_requerido('admin')
@login_required
def detalle_producto_cliente(producto_id):
    return f_detalle_producto(producto_id)

@routerAdmin.route("/admin/dashboard/crear", methods=["POST", "GET"])
@login_required
def crear_producto():
    return f_crear_producto(request)

@routerAdmin.route("/admin/dashboard/editar/<int:producto_id>", methods=["POST"])
@login_required
def editar_producto(producto_id):
    return f_editar_producto(producto_id, request)

@routerAdmin.route("/admin/dashboard/eliminar/<int:producto_id>", methods=["POST"])
@login_required
def eliminar_producto(producto_id):
    return f_eliminar_producto(producto_id)

@routerAdmin.route("/admin/dashboard/productos/generar-qrs")
@login_required
def generar_qrs_pdf():
    return f_generar_pdf_qrs()

#/=========================================================\
# Rutas para el panel de administración PEDIDOS  #
#\=========================================================/


@routerAdmin.route("/admin/pedidos", methods=["GET"])
@login_required
@rol_requerido("admin")
def listar_pedidos():
    return f_listar_pedidos()


@routerAdmin.route("/admin/pedidos/<int:pedido_id>", methods=["GET"])
@login_required
@rol_requerido("admin")
def detalle_pedido(pedido_id):
    return f_detalle_pedido_admin(pedido_id)


@routerAdmin.route("/admin/pedidos/<int:pedido_id>/estado", methods=["POST"])
@login_required
@rol_requerido("admin")
def cambiar_estado_pedido(pedido_id):
    return f_cambiar_estado_pedido(pedido_id)


@routerAdmin.route("/admin/pedidos/<int:pedido_id>/eliminar", methods=["POST"])
@login_required
@rol_requerido("admin")
def eliminar_pedido(pedido_id):
    return f_eliminar_pedido(pedido_id)


@routerAdmin.route("/admin/pedidos/exportar", methods=["GET"])
@login_required
@rol_requerido("admin")
def exportar_pedidos_csv():
    return f_exportar_pedidos_csv()


@routerAdmin.route('/admin/pedidos/<int:pedido_id>/json')
@login_required
@rol_requerido("admin")
def pedido_json(pedido_id):
    return f_pedido_json(pedido_id)

#/=========================================================\
# Rutas para el panel de administración SOLICITUDES  #
#\=========================================================/

@routerAdmin.route("/admin/solicitudes")
@login_required
@rol_requerido("admin")
def listado_solicitudes():
    return f_listado_solicitudes()
 
 
@routerAdmin.route("/admin/solicitudes/<int:solicitud_id>/estado", methods=["POST"])
@login_required
@rol_requerido("admin")
def cambiar_estado_solicitud(solicitud_id):
    return f_cambiar_estado_solicitud(solicitud_id)
 
 
@routerAdmin.route("/admin/solicitudes/extra/<int:extra_id>/precio", methods=["POST"])
@login_required
@rol_requerido("admin")
def guardar_precio_extra(extra_id):
    return f_guardar_precio_extra(extra_id)

@routerAdmin.route("/admin/solicitudes/descuento", methods=["GET"])
@login_required
@rol_requerido("admin")
def listado_descuento():
    return f_listado_descuento()

@routerAdmin.route("/admin/solicitudes/<int:solicitud_id>/descuento", methods=["POST"])
@login_required
@rol_requerido("admin")
def aplica_descuento(solicitud_id):
    return f_aplica_descuento(solicitud_id)


@routerAdmin.route("/admin/solicitudes/generar-pdf/<int:solicitud_id>", methods=["POST"])
@login_required
@rol_requerido("admin")
def generar_pdf_solicitudes(solicitud_id):
    return f_generar_pdf_solicitudes(solicitud_id)


 #/=========================================================\
#    Rutas para Targetas de Rol                             #
#\=========================================================/


@routerAdmin.route("/admin/tarjetas/crear", methods=["GET", "POST"])
@login_required
@rol_requerido("admin")
def crear_tarjeta_rol():
    return f_crear_tarjeta_rol()
 


 #/=========================================================\
# Rutas para PRESENTACIONES                                #
#\=========================================================/
 
@routerAdmin.route("/admin/presentaciones", methods=["GET"])
@login_required
@rol_requerido("admin")
def listar_presentaciones():
    return f_listar_presentaciones()
 
 
@routerAdmin.route("/admin/presentaciones/crear", methods=["GET", "POST"])
@login_required
@rol_requerido("admin")
def crear_presentacion():
    return f_crear_presentacion()
 
 
@routerAdmin.route("/admin/presentaciones/<int:presentacion_id>/editar", methods=["GET", "POST"])
@login_required
@rol_requerido("admin")
def editar_presentacion(presentacion_id):
    return f_editar_presentacion(presentacion_id)
 
 
@routerAdmin.route("/admin/presentaciones/<int:presentacion_id>/eliminar", methods=["POST"])
@login_required
@rol_requerido("admin")
def eliminar_presentacion(presentacion_id):
    return f_eliminar_presentacion(presentacion_id)
 
 
@routerAdmin.route("/admin/api/presentaciones/<int:presentacion_id>/inscritos")
@login_required
@rol_requerido("admin")
def api_inscritos_presentacion(presentacion_id):
    return f_api_inscritos_presentacion(presentacion_id)
 
 
@routerAdmin.route("/admin/api/presentaciones/<int:presentacion_id>/json")
@login_required
@rol_requerido("admin")
def api_presentacion_json(presentacion_id):
    return f_api_presentacion_json(presentacion_id)


@routerAdmin.route("/admin/pedidos/<int:pedido_id>/editar", methods=["POST"])
@login_required
@rol_requerido("admin")
def editar_pedido_admin(pedido_id):
    return f_editar_pedido_admin(pedido_id)


 #/=========================================================\
# Rutas para MOBILIARIO                                #
#\=========================================================/


@routerAdmin.route("/admin/mobiliario")
@login_required
@rol_requerido("admin")
def listar_mobiliario():
    return f_listar_mobiliario()


@routerAdmin.route("/admin/mobiliario/crear", methods=["GET", "POST"])
@login_required
@rol_requerido("admin")
def crear_mobiliario():
    return f_crear_mobiliario()


@routerAdmin.route("/admin/mobiliario/<int:mobiliario_id>/editar", methods=["GET", "POST"])
@login_required
@rol_requerido("admin")
def editar_mobiliario(mobiliario_id):
    return f_editar_mobiliario(mobiliario_id)


@routerAdmin.route("/admin/mobiliario/<int:mobiliario_id>/eliminar", methods=["POST"])
@login_required
@rol_requerido("admin")
def eliminar_mobiliario(mobiliario_id):
    return f_eliminar_mobiliario(mobiliario_id)

@routerAdmin.route("/admin/stands/mapa", methods=['GET', "POST"])
@login_required
@rol_requerido("admin")
def ver_mapa():
    return f_ver_mapa()

@routerAdmin.route("/admin/stands/actualizar", methods=['GET', "POST"])
@login_required
@rol_requerido("admin")
def actualizar_stands():
    return f_actualizar_stands()

@routerAdmin.route("/admin/stands/asignar-proveedor", methods=["POST"])
@login_required
@rol_requerido("admin")
def asignar_stand_proveedor():
    return f_asignar_stand_proveedor()

@routerAdmin.route("/admin/proveedores/disponibles", methods=["GET"])
@login_required
@rol_requerido("admin")
def proveedores_disponibles():
    return f_proveedores_disponibles()

@routerAdmin.route("/admin/stands/historial", methods=['GET', "POST"])
@login_required
@rol_requerido("admin")
def historial_stands():
    return f_historial_stands()

@routerAdmin.route("/admin/stands/export/historial/excel")
@login_required
@rol_requerido("admin")
def exportar_historial_excel():
    return f_exportar_excel_historial()

@routerAdmin.route("/admin/stands/export/historial/pdf")
@login_required
@rol_requerido("admin")
def exportar_historial_pdf():
    return f_exportar_pdf_historial()

 #/=========================================================\
# Rutas para MOBILIARIO                                #
#\=========================================================/


@routerAdmin.route('/admin/incidencias')
@login_required
@rol_requerido('admin')
def listar_incidencias():
    return f_listar_incidencias()

@routerAdmin.route('/admin/incidencias/contar-pendientes')
@login_required
@rol_requerido('admin')
def contar_incidencias_pendientes():
    return f_contar_incidencias_pendientes()

@routerAdmin.route('/admin/incidencias/<int:incidencia_id>/estado', methods=['POST'])
@login_required
@rol_requerido('admin')
def cambiar_estado_incidencia(incidencia_id):
    return f_cambiar_estado_incidencia(incidencia_id)

@routerAdmin.route('/admin/incidencias/<int:incidencia_id>/eliminar', methods=['POST'])
@login_required
@rol_requerido('admin')
def eliminar_incidencia(incidencia_id):
    return f_eliminar_incidencia(incidencia_id)


#CAMBIAR FECHA DEL FORUM

@routerAdmin.route("/admin/config/fecha-forum", methods=["POST"])
@rol_requerido('admin')
@login_required
def cambiar_fecha_forum():
    return f_cambiar_fecha_forum()

@routerAdmin.route("/admin/config/fecha-fin-reservas", methods=["POST"])
@rol_requerido('admin')
@login_required
def cambiar_fecha_fin_reservas():
    return f_cambiar_fecha_fin_reservas()
