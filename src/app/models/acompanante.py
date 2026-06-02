from extensions import db


class Acompanante(db.Model):
    __tablename__ = "acompanantes"

    id         = db.Column(db.Integer,     primary_key=True)
    usuario_id = db.Column(db.Integer,     db.ForeignKey("usuarios.id"), nullable=False)
    nombre     = db.Column(db.String(100), nullable=False)
    apellido   = db.Column(db.String(100), nullable=False)
    qr_token  = db.Column(db.String(255), unique=True, nullable=True)
    asiste_cena = db.Column(db.Boolean, nullable=True)  
    pernocta = db.Column(db.Boolean, nullable=True)

    usuario = db.relationship("Usuario", back_populates="acompanantes")

    def __repr__(self):
        return f"<Acompanante {self.nombre} {self.apellido} – usuario_id={self.usuario_id}>"
