from datetime import datetime, timezone
from extensions import db
from .enums import RolEnum, TipoVCEnum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    apellido1 = db.Column(db.String(150), nullable=False)
    apellido2 = db.Column(db.String(150), nullable=False)
    nombre_usuario = db.Column(db.String(5), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum(RolEnum), nullable=False)
    nombre_empresa = db.Column(db.String(255))
    cif_empresa = db.Column(db.String(50))
    codigo = db.Column(db.String(5))
    tipo_vc = db.Column(db.Enum(TipoVCEnum))
    comercial_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_llegada = db.Column(db.DateTime)
    qr_token = db.Column(db.String(255), unique=True)
    estado = db.Column(db.Boolean, default=True)
    fecha_alta = db.Column(db.DateTime, default=datetime.now())
    asiste_cena = db.Column(db.Boolean, nullable=True)
    pernocta = db.Column(db.Boolean, nullable=True)  
 
    # Relaciones
    comercial = db.relationship(
        "Usuario",
        remote_side="Usuario.id",
        backref=db.backref("clientes_asignados", lazy="dynamic"),
        foreign_keys=[comercial_id],
    )
    controles = db.relationship("ControlES", back_populates="usuario", lazy="dynamic")
    pedidos = db.relationship("Pedido", back_populates="cliente", lazy="dynamic")
    productos = db.relationship("Producto", back_populates="proveedor", lazy="dynamic")
    acompanantes = db.relationship("Acompanante", back_populates="usuario", lazy="dynamic")
    solicitudes = db.relationship("Solicitud", back_populates="usuario", lazy="dynamic")
    presentacion_usuarios = db.relationship("PresentacionUsuario", back_populates="usuario", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def tiene_rol(self, *roles) -> bool:
        return self.rol in roles
    
    def __repr__(self):
        return f"<Usuario {self.id} – {self.email} [{self.rol.value}]>"
