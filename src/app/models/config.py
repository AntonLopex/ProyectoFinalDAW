from extensions import db


class Config(db.Model):
    __tablename__ = "config"

    id        = db.Column(db.Integer,     primary_key=True)
    tipo      = db.Column(db.String(100), nullable=False, unique=True)
    valor     = db.Column(db.Integer,     nullable=True)
    valor_str = db.Column(db.String(500), nullable=True)
    fecha_forum = db.Column(db.DateTime, nullable=False)
    fecha_fin_reservas = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Config {self.tipo} = {self.valor or self.valor_str}>"
