from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class Select2MultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass


class UsuarioComercialForm(FlaskForm):

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

    clientes = Select2MultipleField(
        "Clientes",
        coerce=int
    )

    submit = SubmitField("Crear comercial")