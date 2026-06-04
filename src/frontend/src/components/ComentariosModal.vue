<template>
  <Transition name="slide-up">
    <div v-if="open" class="comentarios-modal-backdrop" @click.self="close">
      <div class="comentarios-modal comentarios-modal--large">
        <!-- Botón cerrar (solo móvil) -->
        <button
          v-if="isMobile"
          class="comentarios-modal__close-btn"
          @click="close"
          aria-label="Cerrar"
        >
          <i class="bi bi-chevron-down"></i>
        </button>

        <!-- Sección izquierda: imagen + título + likes (solo escritorio) -->
        <div class="comentarios-modal__left">
          <div class="comentarios-modal__img-container">
            <img
              v-if="receta.imagen"
              :src="receta.imagen"
              alt="Foto de la receta"
              class="comentarios-modal__img"
            />
            <div v-else class="comentarios-modal__img-placeholder">
              🖼️ Sin imagen
            </div>
          </div>

          <h3 class="comentarios-modal__titulo">
            {{ receta.titulo }}
          </h3>

          <div class="comentarios-modal__meta">
            <button
              class="comentarios-modal__btn-like d-flex align-items-center"
              type="button"
              @click.stop="handleLike"
            >
              <i
                class="bi"
                :class="receta.usuario_like ? 'bi-heart-fill' : 'bi-heart'"
              ></i>
              <span class="ms-1">{{ receta.likes_count }}</span>
            </button>
          </div>
        </div>

        <!-- Sección derecha: comentarios + formulario -->
        <div class="comentarios-modal__right">
          <!-- Versión móvil: imagen + título + likes -->
          <div class="comentarios-modal__mobile-header">
            <div class="comentarios-modal__img-container-mobile">
              <img
                v-if="receta.imagen"
                :src="receta.imagen"
                alt="Foto de la receta"
                class="comentarios-modal__img-mobile"
              />
              <div v-else class="comentarios-modal__img-placeholder-mobile">
                🖼️ Sin imagen
              </div>
            </div>

            <div class="comentarios-modal__mobile-title-like">
              <h3 class="comentarios-modal__titulo-mobile">
                {{ receta.titulo }}
              </h3>
              <button
                class="comentarios-modal__btn-like d-flex align-items-center"
                type="button"
                @click.stop="handleLike"
              >
                <i
                  class="bi"
                  :class="receta.usuario_like ? 'bi-heart-fill' : 'bi-heart'"
                ></i>
                <span class="ms-1">{{ receta.likes_count }}</span>
              </button>
            </div>
          </div>

          <!-- Lista de comentarios (scroll vertical) -->
          <div class="comentarios-modal__body">
            <div v-if="loading" class="text-center py-3">
              <div class="spinner-border text-olea" role="status">
                <span class="visually-hidden">Cargando comentarios...</span>
              </div>
            </div>

            <div
              v-else-if="comentarios.length === 0"
              class="text-muted text-center py-3"
            >
              No hay comentarios todavía.
            </div>

            <ul v-else class="comentarios-modal__list">
              <li
                v-for="c in comentarios"
                :key="c.id"
                class="comentarios-modal__item"
              >
                <div class="comentarios-modal__item-header">
                  <span class="comentarios-modal__autor">
                    @{{ c.usuario_nombre }}
                  </span>
                  <span class="comentarios-modal__fecha">
                    {{ formatDate(c.created_at) }}
                  </span>
                </div>
                <p class="comentarios-modal__texto">
                  {{ c.contenido }}
                </p>
              </li>
            </ul>
          </div>

          <!-- Cuadro de envío de comentario -->
          <div class="comentarios-modal__footer">
            <div
              v-if="!auth.usuario"
              class="alert alert-warning text-center mb-0"
            >
              Debes
              <a href="/auth" @click.prevent="close">iniciar sesión</a> para
              comentar.
            </div>

            <div v-else class="comentarios-modal__input-container">
              <textarea
                v-model="nuevoComentario"
                class="comentarios-modal__textarea"
                placeholder="Escribe un comentario..."
              ></textarea>

              <!-- Botón de enviar como ícono -->
              <button
                class="btn btn-olea comentarios-modal__send-btn"
                :disabled="loading || !nuevoComentario.trim()"
                @click="enviarComentario"
              >
                <i class="bi bi-send-fill"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";

const auth = useAuthStore();

const open = defineModel("open", { type: Boolean, default: false });
const props = defineProps({
  recetaId: { type: Number, required: false },
  receta: { type: Object, required: true },
});

// Detectar si es móvil
const isMobile = computed(() => {
  return window.innerWidth <= 768;
});

const comentarios = ref([]);
const loading = ref(false);
const nuevoComentario = ref("");

const formatDate = (isoDate) => {
  const d = new Date(isoDate);
  return (
    d.toLocaleDateString("es-ES") +
    " " +
    d.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" })
  );
};

const loadComentarios = async () => {
  if (!open.value || !props.recetaId) return;

  loading.value = true;
  try {
    const { data } = await api.get(
      `/recetas/recetas/${props.recetaId}/comentarios/`,
    );
    comentarios.value = data;
  } catch (error) {
    console.error("[ComentariosModal] Error al cargar comentarios:", error);
  } finally {
    loading.value = false;
  }
};

watch(open, (v) => {
  if (v) {
    loadComentarios();
  }
});

const enviarComentario = async () => {
  if (!auth.usuario) return;
  if (!nuevoComentario.value.trim()) return;

  const payload = {
    receta: props.recetaId,
    contenido: nuevoComentario.value.trim(),
  };

  try {
    const { data } = await api.post("/recetas/comentarios/", payload);
    comentarios.value.unshift(data);
    nuevoComentario.value = "";
  } catch (error) {
    console.error("[ComentariosModal] Error al enviar comentario:", error);
  }
};

const handleLike = () => {};

const close = () => {
  open.value = false;
};
</script>

<style scoped>
.comentarios-modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.comentarios-modal--large {
  --max-width: 1000px;
}

.comentarios-modal {
  background-color: var(--fondo-crema);
  border-radius: var(--border-radius);
  box-shadow:
    var(--shadow-soft),
    0 12px 36px rgba(0, 0, 0, 0.12);
  width: 90%;
  max-width: var(--max-width);
  max-height: 90vh;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* Botón cerrar (solo móvil) */
.comentarios-modal__close-btn {
  position: absolute;
  top: 0;
  left: 50%;
  display: none;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  margin-top: 0.75rem;
  background: var(--fondo-olea);
  border: 1px solid var(--color-olea);
  border-radius: 9999px;
  color: var(--color-olea);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.comentarios-modal__close-btn:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.comentarios-modal__close-btn i.bi {
  font-size: 1rem;
}

.comentarios-modal__close-btn:hover i.bi {
  transform: rotate(180deg);
}

/* ============================= */
/* ESCRITORIO */
/* ============================= */
.comentarios-modal__left {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background-color: var(--fondo-crema);
  border-right: 1px solid rgba(96, 108, 56, 0.15);
  min-width: 280px;
}

.comentarios-modal__img-container {
  width: 100%;
  height: 220px;
  overflow: hidden;
  border-radius: var(--border-radius);
  margin-bottom: 0.75rem;
  background-color: #f0f0f0;
}

.comentarios-modal__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.comentarios-modal__img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.9rem;
}

.comentarios-modal__titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
  text-align: center;
}

.comentarios-modal__btn-like {
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

.comentarios-modal__btn-like:hover {
  background-color: rgba(96, 108, 56, 0.1);
}

.comentarios-modal__btn-like i.bi {
  color: #f74545;
  font-size: 1.2rem;
  transition: all 0.25s ease;
  transform-origin: center;
}

.comentarios-modal__meta {
  margin-top: 0.5rem;
}

.comentarios-modal__right {
  flex: 2;
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

.comentarios-modal__mobile-header {
  display: none;
}

.comentarios-modal__body {
  padding: 1rem;
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  color: var(--color-texto);
  min-height: 0;
}

.comentarios-modal__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comentarios-modal__item {
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(96, 108, 56, 0.1);
}

.comentarios-modal__item:last-child {
  border-bottom: none;
}

.comentarios-modal__item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.comentarios-modal__autor {
  font-weight: 500;
  color: var(--color-olea);
}

.comentarios-modal__fecha {
  font-size: 0.75rem;
  color: #666;
}

.comentarios-modal__texto {
  margin-bottom: 0;
  line-height: 1.4;
}

.comentarios-modal__footer {
  flex-shrink: 0;
  padding: 1rem;
  background-color: var(--fondo-bloque);
  border-top: 1px solid rgba(96, 108, 56, 0.1);
}

.comentarios-modal__input-container {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.comentarios-modal__textarea {
  flex: 1;
  resize: none;
  padding: 0.75rem;
  border-radius: var(--border-radius);
  border: 1px solid #ddd;
  font-size: 0.9rem;
  color: var(--color-texto);
  max-height: 80px;
}

.comentarios-modal__textarea:focus {
  outline: none;
  border-color: var(--color-acento);
}

.comentarios-modal__send-btn {
  padding: 0.75rem 0.9rem;
  border-radius: 50%;
  min-width: fit-content;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.comentarios-modal__send-btn:hover {
  transform: scale(1.05);
}

.comentarios-modal__send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Animación para escritorio (no cambia) */
.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

/* ============================= */
/* RESPONSIVE: Móvil */
/* ============================= */
@media (max-width: 768px) {
  .comentarios-modal-backdrop {
    align-items: flex-end;
  }

  .comentarios-modal {
    width: 100%;
    max-width: 100%;
    height: 90vh;
    max-height: 90vh;
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    flex-direction: column;
  }

  /* Mostrar botón cerrar en móvil */
  .comentarios-modal__close-btn {
    display: flex;
  }

  .comentarios-modal__left {
    display: none;
  }

  .comentarios-modal__right {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 100%;
  }

  /* Mostrar header móvil */
  .comentarios-modal__mobile-header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    padding-top: 4.5rem; /* Espacio para el botón cerrar centrado */
    flex-shrink: 0;
    border-bottom: 1px solid rgba(96, 108, 56, 0.1);
  }

  .comentarios-modal__img-container-mobile {
    width: 100%;
    height: 160px;
    overflow: hidden;
    border-radius: var(--border-radius);
    background-color: #f0f0f0;
  }

  .comentarios-modal__img-mobile {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .comentarios-modal__img-placeholder-mobile {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 0.9rem;
  }

  .comentarios-modal__mobile-title-like {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .comentarios-modal__titulo-mobile {
    font-family: var(--fuente-titulos);
    color: var(--color-olea);
    margin: 0;
    font-size: 1.1rem;
    flex: 1;
  }

  /* Cuerpo con scroll */
  .comentarios-modal__body {
    flex: 1;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    padding: 0.75rem;
    min-height: 0;
  }

  .comentarios-modal__footer {
    flex-shrink: 0;
    padding: 0.75rem;
  }

  /* Animación específica para móvil: slide con opacity */
  .slide-up-enter-active,
  .slide-up-leave-active {
    transition:
      transform 0.4s cubic-bezier(0.32, 0.72, 0, 1),
      opacity 0.3s ease;
  }

  .slide-up-enter-from {
    transform: translateY(100%);
    opacity: 0;
  }

  .slide-up-leave-to {
    transform: translateY(100%);
    opacity: 0;
  }
}

@media (max-width: 480px) {
  .comentarios-modal__img-container-mobile {
    height: 140px;
  }

  .comentarios-modal__titulo-mobile {
    font-size: 1rem;
  }
}
</style>
