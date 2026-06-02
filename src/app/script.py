from run import create_app
from extensions import db
from models import Producto
import uuid

# Script para asignar un token QR único a cada producto que no tenga uno, utilizando la función uuid4 para generar tokens únicos 
# y actualizando la base de datos con los nuevos tokens asignados a los productos correspondientes
app = create_app()
with app.app_context():
    sin_token = Producto.query.filter_by(qr_token=None).all()
    for p in sin_token:
        p.qr_token = str(uuid.uuid4())
    db.session.commit()
    print(f"{len(sin_token)} productos actualizados.")