from rest_framework.views import APIView
from rest_framework.response import Response
from recetas.permissions import IsAdminOrRegistrado
from rest_framework import status

from recetas.models import Receta
from recetas.views import get_logged_user
from .models import Favorito


class FavoritoToggleView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, receta_id):
        receta = Receta.objects.get(pk=receta_id)
        favorito, created = Favorito.objects.get_or_create(
            usuario=get_logged_user(request),
            receta=receta,
        )

        return Response(
            {
                "favorito": True,
                "favoritos_count": receta.favoritos.count(),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, receta_id):
        receta = Receta.objects.get(pk=receta_id)
        Favorito.objects.filter(usuario=get_logged_user(request), receta=receta).delete()

        return Response(
            {
                "favorito": False,
                "favoritos_count": receta.favoritos.count(),
            },
            status=status.HTTP_200_OK,
        )