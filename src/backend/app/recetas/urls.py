# urls.py (app recetas)
from django.urls import path, include
from .views import CategoriaCreateView, CategoriaListView, ComentariosPorRecetaView, RecetaAPIView, RecetaCreateView, RecetaDetailView, RecetasPorCategoriaAPIView, SearchUserView, TopRecetasAPIView, UserProfileView, crear_comentario_view, receta_like_view, comentarios_receta_view

urlpatterns = [
    # Recetas
    path("recetas/", RecetaAPIView.as_view(), name="recetas-list"),
    path("recetas/", RecetaCreateView.as_view(), name="recetas-create"),
    path("recetas/<int:receta_id>/like/", receta_like_view, name="receta-like"),
    path("recetas/<int:id>/", RecetaDetailView.as_view(), name="receta-detail"),
    path("recetas/<int:receta_id>/comentarios/", comentarios_receta_view, name="receta-comentarios"),
    
    # Comentarios
    path("comentarios/", crear_comentario_view, name="crear-comentario"),
    path("comentarios/recetas/<int:receta_id>/", ComentariosPorRecetaView.as_view(), name="comentarios-receta"),
    
    # Categorías
    path("categorias/", CategoriaListView.as_view(), name="categorias-list"),
    path("categorias/", CategoriaCreateView.as_view(), name="categorias-create"),
    path(
        "categorias/<int:categoria_id>/recetas/",
        RecetasPorCategoriaAPIView.as_view(),
        name="recetas-por-categoria",
    ),
    
    # Otros
    path("top-recetas/", TopRecetasAPIView.as_view(), name="top-recetas"),
    path("perfil/<str:username>/", UserProfileView.as_view(), name="user-profile"),
    path("buscar-usuario/", SearchUserView.as_view(), name="search-user"),
    
        # Moderación (reportes)
    path("", include("moderacion.urls")),   
]
