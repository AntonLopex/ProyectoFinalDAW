from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class UsuarioClienteForm(FlaskForm):

    nombre = StringField("Nombre", validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(max=100, message="Máximo 100 caracteres")
    ])

    apellido1 = StringField("Primer apellido", validators=[
        DataRequired(message="El primer apellido es obligatorio"),
        Length(max=100, message="Máximo 100 caracteres")
    ])

    apellido2 = StringField("Segundo apellido", validators=[
        Length(max=100, message="Máximo 100 caracteres")
    ])

    email = StringField("Email", validators=[
        DataRequired(message="El email es obligatorio"),
        Email(message="Introduce un email válido")
    ])

    password = PasswordField("Contraseña", validators=[
        DataRequired(message="La contraseña es obligatoria"),
        Length(min=8, message="La contraseña debe tener al menos 8 caracteres")
    ])

    confirmar_password = PasswordField("Confirmar contraseña", validators=[
        DataRequired(message="Debes confirmar la contraseña"),
        EqualTo("password", message="Las contraseñas no coinciden")
    ])

    nombre_empresa = StringField("Nombre de la empresa", validators=[
        DataRequired(message="El nombre de la empresa es obligatorio"),
        Length(max=255, message="Máximo 255 caracteres")
    ])

    cif_empresa = StringField("CIF de la empresa", validators=[
        DataRequired(message="El CIF es obligatorio"),
        Length(max=50, message="Máximo 50 caracteres")
    ])

    codigo = StringField("Código de cliente", validators=[
        Length(max=5, message="Máximo 5 caracteres")
    ])

    fecha_llegada = StringField("Fecha y hora de llegada estimada", validators=[
        DataRequired(message="La fecha de llegada es obligatoria"),
        Length(max=16, message="Máximo 16 caracteres")
    ])

    comercial_id = StringField("Comercial asignado", validators=[
        Optional()
    ])

    pernocta = BooleanField("Se quedará a dormir")

    submit = SubmitField("Crear cliente")