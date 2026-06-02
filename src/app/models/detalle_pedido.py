from extensions import db


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"

    id              = db.Column(db.Integer,        primary_key=True)
    pedido_id       = db.Column(db.Integer,        db.ForeignKey("pedidos.id"),   nullable=False)
    producto_id     = db.Column(db.Integer,        db.ForeignKey("productos.id"), nullable=False)
    cantidad        = db.Column(db.Integer,        nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
                     # Se snapshot en el momento del pedido para conservar el precio histórico
    subtotal        = db.Column(db.Numeric(10, 2), nullable=False)
                     # Calculado: cantidad × precio_unitario

    pedido   = db.relationship("Pedido",   back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_pedido")

    def calcular_subtotal(self):
        """Calcula y persiste el subtotal de esta línea."""
        if self.cantidad is not None and self.precio_unitario is not None:
            self.subtotal = self.cantidad * self.precio_unitario

    def __repr__(self):
        return (
            f"<DetallePedido pedido={self.pedido_id} "
            f"producto={self.producto_id} qty={self.cantidad}>"
        )
