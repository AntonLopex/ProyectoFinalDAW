# interacciones/urls.py
from django.urls import path
from .views import FavoritoToggleView

urlpatterns = [
    path("favoritos/<int:receta_id>/", FavoritoToggleView.as_view(), name="favorito-toggle"),
]