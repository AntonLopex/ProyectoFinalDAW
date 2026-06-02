from extensions import db

class Extra(db.Model):
    __tablename__ = "extras"

    id           = db.Column(db.Integer,        primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"),nullable=False)
    descripcion  = db.Column(db.String(255),    nullable=False)
    cantidad     = db.Column(db.Integer,        nullable=False, default=1)
    precio       = db.Column(db.Numeric(10, 2), nullable=False, default= 0)  

    solicitud = db.relationship("Solicitud", back_populates="extras")


    def __repr__(self):
        return f"<Extra {self.id} - {self.descripcion} x{self.cantidad}>"   