<!-- RecetaCard.vue -->
<template>
  <!-- Card: al hacer click en la card, va a la receta -->
  <div class="receta-card" @click="$router.push(`/receta/${receta.id}`)">
    <!-- Imagen -->
    <div class="receta-card__image-container">
      <img
        v-if="receta.imagen"
        :src="receta.imagen"
        alt="Imagen de receta"
        class="receta-card__image"
        @error="onImageError"
      />
      <div v-else class="receta-card__image-placeholder">
        🖼️ Receta sin imagen
      </div>
    </div>

    <!-- Bandera de reportes (debajo de la foto, a la derecha) -->
    <button
      class="reporte-flag"
      @click.stop="abrirReporte"
      title="Reportar receta"
    >
      <i class="bi bi-flag-fill"></i>
    </button>

    <!-- Contenido -->
    <div class="receta-card__body">
      <!-- Título -->
      <h3 class="receta-card__title">{{ receta.titulo }}</h3>

      <!-- Usuario que publicó la receta (link al perfil) -->
      <div class="receta-card__usuario">
        <div class="receta-card__usuario-avatar">
          <img
            v-if="receta.usuario_foto"
            :src="receta.usuario_foto"
            alt="Foto de perfil"
            class="receta-card__avatar-img"
          />
          <i v-else class="bi bi-person-circle receta-card__avatar-icon"></i>
        </div>
        <router-link
          :to="`/perfil/${receta.usuario_username}`"
          class="usuario-link"
          @click.stop
        >
          @{{ receta.usuario_username }}
        </router-link>
      </div>

      <!-- Categorías -->
      <div class="receta-card__categorias">
        <span
          v-for="cat in receta.categorias"
          :key="cat.id"
          class="receta-card__categoria-tag"
        >
          {{ cat.nombre }}
        </span>
      </div>

      <!-- Descripción truncada -->
      <p class="receta-card__descripcion">
        {{
          receta.descripcion
            ? receta.descripcion.substring(0, 80) +
              (receta.descripcion.length > 80 ? "..." : "")
            : ""
        }}
      </p>

      <!-- Likes, comentarios y favoritos -->
      <div class="receta-card__meta">
        <button
          class="receta-card__btn-like d-flex align-items-center"
          type="button"
          @click.stop="handleLike"
        >
          <i
            class="bi"
            :class="receta.usuario_like ? 'bi-heart-fill' : 'bi-heart'"
          ></i>
          <span class="ms-1">{{ receta.likes_count }}</span>
        </button>

        <button
          class="receta-card__btn-favorito d-flex align-items-center"
          type="button"
          @click.stop="handleFavorito"
          :title="
            receta.usuario_favorito
              ? 'Quitar de favoritos'
              : 'Añadir a favoritos'
          "
        >
          <i
            class="bi"
            :class="
              receta.usuario_favorito ? 'bi-bookmark-fill' : 'bi-bookmark'
            "
          ></i>
        </button>

        <button
          class="receta-card__btn-comentarios d-flex align-items-center"
          type="button"
          @click.stop="$emit('open-comments', receta)"
        >
          <i class="bi bi-chat-left-text"></i>
          <span class="ms-1">{{ receta.comentarios_count }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  receta: {
    type: Object,
    required: true,
  },
});

const emits = defineEmits(["like", "open-comments", "favorite", "open-report"]);

const onImageError = (e) => {
  e.target.style.display = "none";
  const placeholder = e.target.parentElement.querySelector(
    ".receta-card__image-placeholder",
  );
  if (placeholder) {
    placeholder.style.display = "flex";
  }
};

const handleLike = () => {
  emits("like");
};

const handleFavorito = () => {
  emits("favorite");
};

const abrirReporte = () => {
  emits("open-report", props.receta);
};
</script>

<style scoped>
.receta-card {
  background-color: var(--fondo-bloque);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition);
  height: 100%;
  min-height: 380px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.receta-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.receta-card__image-container {
  position: relative;
  height: 180px;
  min-height: 180px;
  overflow: hidden;
  background-color: #f5f5f5;
  flex-shrink: 0;
}

.receta-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: var(--transition);
}

.receta-card__image:hover {
  transform: scale(1.05);
}

.receta-card__image-placeholder {
  display: none;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--color-texto);
  font-size: 0.9rem;
  background-color: var(--fondo-crema);
}

/* Bandera de reportes (debajo de la foto, a la derecha) */
.reporte-flag {
  position: absolute;
  top: 190px; /* justo debajo de la imagen */
  right: 0.7rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  z-index: 10;
  opacity: 1;
  transition: all 0.2s;
}

.reporte-flag:hover {
  transform: scale(1.2);
}

.reporte-flag i.bi {
  font-size: 1rem;
  color: #f74545;
}

.receta-card__body {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-top: 1.5rem; /* espacio para la bandera */
}

.receta-card__title {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.receta-card__usuario {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-texto);
  margin-bottom: 0.5rem;
}

.receta-card__usuario-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background-color: var(--fondo-crema);
}

.receta-card__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.receta-card__avatar-icon {
  font-size: 28px;
  color: var(--color-olea);
}

.receta-card__usuario-link {
  color: var(--color-olea);
  text-decoration: none;
  font-weight: 500;
  transition: var(--transition);
  cursor: pointer;
}

.receta-card__usuario-link:hover {
  text-decoration: underline;
  color: var(--color-acento);
}

.receta-card__categorias {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.5rem;
  margin-bottom: 0.5rem;
}

.receta-card__categoria-tag {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--fondo-crema);
  background-color: var(--color-olea);
  border-radius: 9999px;
  padding: 0.25rem 0.75rem;
  border: 1px solid rgba(96, 108, 56, 0.2);
}

.receta-card__descripcion {
  color: var(--color-texto);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.receta-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--color-texto);
  font-size: 0.8rem;
  margin-top: auto;
  padding-top: 0.5rem;
}

.receta-card__btn-like,
.receta-card__btn-comentarios,
.receta-card__btn-favorito {
  background: none;
  border: none;
  color: inherit;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  transition: var(--transition);
}

.receta-card__btn-like:hover,
.receta-card__btn-comentarios:hover,
.receta-card__btn-favorito:hover {
  background-color: rgba(96, 108, 56, 0.1);
}

.receta-card__btn-like i.bi {
  color: #f74545;
  font-size: 1.2rem;
  transition: all 0.25s ease;
  transform-origin: center;
}

.receta-card__btn-favorito i.bi {
  color: var(--color-olea);
  font-size: 1.2rem;
  transition: all 0.25s ease;
}

.receta-card__btn-comentarios i.bi {
  color: var(--color-olea);
  font-size: 1.15rem;
}

/* Responsive */
@media (max-width: 768px) {
  .receta-card {
    min-height: 320px;
  }

  .receta-card__image-container {
    height: 200px;
    min-height: 200px;
  }

  .reporte-flag {
    top: 200px; /* ajustar según altura imagen móvil */
    right: 0.85rem;
  }

  .reporte-flag i.bi {
    font-size: 0.9rem;
  }

  .receta-card__body {
    padding-top: 1.25rem;
  }

  .receta-card__title {
    font-size: 1rem;
  }

  .receta-card__descripcion {
    font-size: 0.85rem;
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }
}

@media (max-width: 480px) {
  .receta-card {
    min-height: 280px;
  }

  .receta-card__image-container {
    height: 130px;
    min-height: 130px;
  }

  .reporte-flag {
    top: 130px; /* ajustar según altura imagen móvil pequeño */
    right: 0.75rem;
  }

  .reporte-flag i.bi {
    font-size: 0.85rem;
  }

  .receta-card__body {
    padding-top: 1rem;
  }

  .receta-card__title {
    font-size: 0.95rem;
  }

  .receta-card__btn-like i.bi,
  .receta-card__btn-comentarios i.bi,
  .receta-card__btn-favorito i.bi {
    font-size: 1.1rem;
  }
}
</style>
