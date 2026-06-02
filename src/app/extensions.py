from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Instancia única compartida por toda la aplicación.
# Se inicializa con la app en el factory (create_app).
db = SQLAlchemy()


login_manager = LoginManager()
mail = Mail()

login_manager.login_view = "auth.login"        # ruta a la que redirige si no autenticado
login_manager.login_message = "Debes iniciar sesión para acceder."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id: str):
    from models.usuario import Usuario
    return Usuario.query.get(int(user_id))