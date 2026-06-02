from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_welcome_email(user):

    subject = "Bienvenido a OLEA 🍽️"

    from_email = settings.EMAIL_HOST_USER

    to_email = [user.email]

    text_content = f"""
Bienvenido a OLEA

Tu nombre de usuario es:
{user.nombre_usuario}

Ya puedes compartir recetas y descubrir platos increíbles.
    """

    html_content = f"""
    <div style="
        background-color: #fefae0;
        padding: 40px 20px;
        font-family: Arial, sans-serif;
    ">

        <div style="
            max-width: 600px;
            margin: auto;
            background-color: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        ">

            <!-- HEADER -->
            <div style="
                background-color: #606c38;
                padding: 35px;
                text-align: center;
            ">

                <h1 style="
                    color: white;
                    margin: 0;
                    font-size: 38px;
                    font-family: Georgia, serif;
                ">
                    OLEA 🌿
                </h1>

            </div>

            <!-- BODY -->
            <div style="
                padding: 40px;
                color: #283618;
            ">

                <h2 style="
                    margin-top: 0;
                    color: #606c38;
                ">
                    Bienvenido a la comunidad 🍽️
                </h2>

                <p style="
                    font-size: 16px;
                    line-height: 1.7;
                ">
                    Hola <strong>{user.nombre}</strong>,
                </p>

                <p style="
                    font-size: 16px;
                    line-height: 1.7;
                ">
                    Tu cuenta ha sido creada correctamente y ya puedes comenzar
                    a compartir recetas, descubrir nuevos platos y conectar
                    con amantes de la cocina.
                </p>

                <!-- USERNAME BOX -->
                <div style="
                    background-color: #f8f9fa;
                    border-left: 5px solid #dda15e;
                    padding: 20px;
                    border-radius: 12px;
                    margin: 30px 0;
                ">

                    <p style="
                        margin: 0;
                        font-size: 14px;
                        color: #666;
                    ">
                        Tu nombre de usuario
                    </p>

                    <h3 style="
                        margin: 8px 0 0 0;
                        color: #606c38;
                        font-size: 28px;
                    ">
                        {user.nombre_usuario}
                    </h3>

                </div>

                <!-- FEATURES -->
                <div style="
                    margin-top: 30px;
                ">

                    <p style="margin-bottom: 10px;">
                        ✅ Compartir recetas
                    </p>

                    <p style="margin-bottom: 10px;">
                        ✅ Guardar favoritos
                    </p>

                    <p style="margin-bottom: 10px;">
                        ✅ Comentar y valorar platos
                    </p>

                </div>

                <!-- FOOTER -->
                <div style="
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #888;
                    font-size: 14px;
                    text-align: center;
                ">

                    Gracias por formar parte de OLEA 🌿

                </div>

            </div>

        </div>

    </div>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to_email
    )

    email.attach_alternative(html_content, "text/html")

    email.send()