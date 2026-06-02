from flask import Flask

from extensions import db,login_manager, mail
from dbConnection import Config
from routes.router_index import routerIndex
from routes.router_control import routerControl
from routes.router_admin import routerAdmin
from routes.router_comercial import routerComercial
from routes.router_proveedor import routerProveedor
from routes.router_cliente import routerCliente

def create_app():
    app = Flask(__name__)


    app.config.from_object(Config)
    app.register_blueprint(routerIndex)
    app.register_blueprint(routerControl)
    app.register_blueprint(routerAdmin)
    app.register_blueprint(routerComercial)
    app.register_blueprint(routerProveedor)
    app.register_blueprint(routerCliente)
    

    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        
    
    
    login_manager.init_app(app)
    login_manager.login_view = "router_index.login"

    mail.init_app(app)


    return app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8200, debug=True)