from flask import Blueprint, request
from flask_login import current_user, login_required
from routes.index.f_index import f_crear_incidencia, f_dashboard_avisoLegal, f_dashboard_politicaCookies, f_dashboard_politicaPrivacidad, f_editar_usuario, f_login, f_logout, f_dashboard, f_producto_por_qr, f_recuperar_contraseña
from utils.utils import rol_requerido


routerIndex = Blueprint('router_index', __name__)


@routerIndex.route("/", methods=["GET", "POST"])
def home():
    return f_login()


@routerIndex.route("/dashboard")
def dashboard():
    return f_dashboard()


@routerIndex.route("/logout")
def logout():
    return f_logout()


@routerIndex.route("/recuperar", methods=["GET", "POST"])   
def recuperar_contraseña():
    return f_recuperar_contraseña(request) 


@routerIndex.route('/incidencia', methods=['POST'])
@login_required
@rol_requerido("cliente", "proveedor", "comercial")
def crear_incidencia():
    return f_crear_incidencia()


@routerIndex.route('/editar-usuario', methods=['GET', 'POST'])
@login_required
@rol_requerido('cliente', 'proveedor', 'comercial')
def editar_usuario():
    return f_editar_usuario(current_user.id)


@routerIndex.route("/producto/qr/<qr_token>")
def producto_por_qr(qr_token):
    return f_producto_por_qr(qr_token)


@routerIndex.route("/aviso-legal")
def aviso_legal():
    return f_dashboard_avisoLegal()


@routerIndex.route("/politica-privacidad")
def politica_privacidad():
    return f_dashboard_politicaPrivacidad()

@routerIndex.route("/politica-cookies")
def politica_cookies():
    return f_dashboard_politicaCookies()