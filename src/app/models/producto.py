from extensions import db


class Producto(db.Model):
    __tablename__ = "productos"

    id           = db.Column(db.Integer,        primary_key=True)
    nombre       = db.Column(db.String(150),    nullable=False)
    descripcion  = db.Column(db.Text,           nullable=True)
    precio       = db.Column(db.Numeric(10, 2), nullable=False)
    imagen_url   = db.Column(db.String(1000),    nullable=True)
    qr_token     = db.Column(db.String(255),    unique=True, nullable=True)
    proveedor_id = db.Column(db.Integer,        db.ForeignKey("usuarios.id"), nullable=False)

    proveedor       = db.relationship("Usuario",       back_populates="productos")
    detalles_pedido = db.relationship("DetallePedido", back_populates="producto")

    def __repr__(self):
        return f"<Producto {self.id} – {self.nombre} (€{self.precio})>"
