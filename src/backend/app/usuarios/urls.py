from django.urls import path
from .views import MiPerfilView, MyProfileView, RegisterView, LoginView, LogoutView, MeView, UpdatePasswordView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path("edit-mi-perfil/", MyProfileView.as_view(), name="editar-mi-perfil"),
    path("cambiar-contrasena/", UpdatePasswordView.as_view(), name="cambiar-contrasena"),
    path("mi-perfil/", MiPerfilView.as_view(), name="mi-perfil"),
]