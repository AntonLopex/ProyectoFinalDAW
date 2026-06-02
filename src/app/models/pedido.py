from datetime import datetime, timezone
from extensions import db


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id                  = db.Column(db.Integer,        primary_key=True)
    cliente_id          = db.Column(db.Integer,        db.ForeignKey("usuarios.id"), nullable=False)
    fecha_pedido        = db.Column(db.DateTime,       default=lambda: datetime.now(), nullable=False)
    estado              = db.Column(db.String(20),     default="pendiente", nullable=False)
                         # Valores: pendiente | confirmado | cancelado
    total               = db.Column(db.Numeric(10, 2), default=0, nullable=False)
                         # Calculado: suma de subtotales de DetallePedido
    observaciones       = db.Column(db.Text,           nullable=True)
    fecha_actualizacion = db.Column(db.DateTime,       onupdate=lambda: datetime.now(), nullable=True)

    cliente  = db.relationship("Usuario",       back_populates="pedidos")
    detalles = db.relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")

    def recalcular_total(self):
        """Recalcula el total sumando los subtotales de cada línea."""
        self.total = sum(d.subtotal for d in self.detalles if d.subtotal is not None)

    def __repr__(self):
        return f"<Pedido {self.id} – cliente_id={self.cliente_id} estado={self.estado}>"
