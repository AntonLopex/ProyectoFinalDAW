<!-- views/RecetaDetailView.vue -->
<template>
  <div class="receta-detail-page">
    <Navbar />

    <!-- Loader -->
    <div v-if="loading" class="loader-wrapper">
      <div class="olea-loader">
        <img src="../../public/logo.png" alt="OLEA" class="loader-icon" />
      </div>
      <p class="loader-text">Cargando receta...</p>
    </div>

    <div v-else-if="receta" class="receta-detail-container">
      <div class="receta-detail__img-wrapper">
        <div class="receta-detail__img-container">
          <img
            v-if="receta.imagen"
            :src="receta.imagen"
            :alt="receta.titulo"
            class="receta-detail__img"
          />
          <div v-else class="receta-detail__img-placeholder">🖼️ Sin imagen</div>
        </div>

        <div class="receta-detail__meta">
          <button
            class="receta-detail__btn-like"
            type="button"
            @click="handleLike"
          >
            <i
              class="bi"
              :class="receta.usuario_like ? 'bi-heart-fill' : 'bi-heart'"
            ></i>
            <span>{{ receta.likes_count || 0 }}</span>
          </button>

          <button
            class="receta-detail__btn-comments"
            type="button"
            @click="scrollToComments"
          >
            <i class="bi bi-chat-left-text"></i>
            <span>{{ comentarios.length }}</span>
          </button>
        </div>
      </div>

      <div class="receta-detail__data">
        <h1 class="receta-detail__titulo">
          {{ receta.titulo }}
        </h1>

        <div class="receta-detail__info">
          <div class="receta-detail__info-item">
            <span class="label">Tiempo</span>
            <span class="value">{{
              formatTiempo(receta.tiempo_de_elaboracion)
            }}</span>
          </div>
          <div class="receta-detail__info-item">
            <span class="label">Dificultad</span>
            <span class="value dificultad-iconos">
              <i
                v-for="(icono, index) in dificultadIconosArray"
                :key="index"
                class="bi bi-fire bi-icon-color"
                :class="[dificultadColorClase]"
              ></i>
            </span>
          </div>
          <div class="receta-detail__info-item">
            <span class="label">Raciones</span>
            <span class="value">{{ receta.raciones }}</span>
          </div>
        </div>

        <div class="receta-detail__separador"></div>

        <div class="receta-detail__seccion">
          <h3 class="receta-detail__subtitulo">Ingredientes</h3>
          <ul class="receta-detail__ingredientes">
            <li
              v-for="ing in receta.ingredientes"
              :key="ing.id"
              class="receta-detail__ingrediente"
            >
              <span class="receta-detail__ing-cant">{{ ing.cantidad }}</span>
              <span class="receta-detail__ing-nombre">{{ ing.nombre }}</span>
            </li>
          </ul>
        </div>

        <div class="receta-detail__seccion">
          <h3 class="receta-detail__subtitulo">Preparación</h3>
          <div class="receta-detail__preparacion">
            <ol>
              <li v-for="(paso, index) in receta.elaboracion" :key="index">
                {{ paso.paso }}
              </li>
            </ol>
          </div>
        </div>

        <div class="receta-detail__separador"></div>

        <div
          ref="comentariosSection"
          class="receta-detail__seccion comentarios-seccion"
        >
          <h3 class="receta-detail__subtitulo">Comentarios</h3>

          <div v-if="loadingComentarios" class="text-center py-3">
            <div class="spinner-border text-olea" role="status">
              <span class="visually-hidden">Cargando comentarios...</span>
            </div>
          </div>

          <div
            v-else-if="comentarios.length === 0"
            class="text-muted text-center py-3"
          >
            Aún no hay comentarios.
          </div>

          <ul v-else class="comentarios-list">
            <li v-for="c in comentarios" :key="c.id" class="comentario-item">
              <div class="comentario-item__header">
                <span class="comentario-item__autor"
                  >@{{ c.usuario_nombre }}</span
                >
                <span class="comentario-item__fecha">
                  {{ formatDate(c.created_at) }}
                </span>
              </div>
              <p class="comentario-item__texto">
                {{ c.contenido }}
              </p>
            </li>
          </ul>

          <div v-if="auth.usuario" class="comment-form mt-3">
            <h4 class="comentario-title">Deja tu comentario</h4>
            <textarea
              v-model="nuevoComentario"
              class="comentario-textarea"
              placeholder="Escribe tu comentario aquí..."
            ></textarea>
            <button
              :disabled="loading || !nuevoComentario.trim()"
              class="btn btn-olea mt-2"
              @click="enviarComentario"
            >
              Publicar comentario
            </button>
          </div>

          <div v-else class="alert alert-light">
            Debes <a href="/auth">iniciar sesión</a> para comentar.
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center text-muted py-5">Receta no encontrada.</div>
  </div>
  <Footer />
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import Navbar from "../components/NavBar.vue";
import Footer from "../components/Footer.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const recetaId = computed(() => parseInt(route.params.id));
const receta = ref(null);
const comentarios = ref([]);
const loading = ref(true);
const loadingComentarios = ref(false);
const nuevoComentario = ref("");

const comentariosSection = ref(null);

const handleLike = async () => {
  try {
    const { data } = await api.post(`/recetas/recetas/${recetaId.value}/like/`);
    receta.value.likes_count = data.likes_count;
    receta.value.usuario_like = data.usuario_like;
  } catch (error) {
    console.error("Error al dar like:", error);
    if (error.response?.status === 401) {
      router.push("/auth");
    }
  }
};

const scrollToComments = () => {
  comentariosSection.value?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
};

const formatTiempo = (tiempo) => {
  if (!tiempo) return "—";
  const partes = tiempo.split(":").map(Number);
  const horas = partes[0];
  const minutos = partes[1];

  if (horas > 0 && minutos > 0) return `${horas}h ${minutos}min`;
  if (horas > 0) return `${horas}h`;
  if (minutos > 0) return `${minutos}min`;
  return "—";
};

const formatDate = (isoDate) => {
  const d = new Date(isoDate);
  return (
    d.toLocaleDateString("es-ES") +
    " " +
    d.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" })
  );
};

const fetchReceta = async () => {
  loading.value = true;
  try {
    const { data } = await api.get(`/recetas/recetas/${recetaId.value}/`);
    receta.value = data;
    if (!receta.value.ingredientes) {
      receta.value.ingredientes = [];
    }
  } catch (error) {
    console.error("Error al cargar receta:", error);
    router.push("/");
  } finally {
    loading.value = false;
  }
};

const loadComentarios = async () => {
  loadingComentarios.value = true;
  try {
    const { data } = await api.get(
      `/recetas/comentarios/recetas/${recetaId.value}`,
    );
    comentarios.value = data;
  } catch (error) {
    console.error("Error al cargar comentarios:", error);
  } finally {
    loadingComentarios.value = false;
  }
};

const enviarComentario = async () => {
  if (!auth.usuario || !nuevoComentario.value.trim()) return;

  const payload = {
    receta: recetaId.value,
    contenido: nuevoComentario.value.trim(),
  };

  try {
    const { data } = await api.post("/recetas/comentarios/", payload);
    comentarios.value.unshift(data);
    nuevoComentario.value = "";
  } catch (error) {
    console.error("Error al enviar comentario:", error);
  }
};

const dificultadCount = computed(() => {
  if (!receta.value?.dificultad) return 0;
  const dificultad = receta.value.dificultad.toLowerCase();

  if (dificultad.includes("fácil") || dificultad.includes("facil")) {
    return 1;
  } else if (dificultad.includes("media")) {
    return 2;
  } else if (dificultad.includes("difícil") || dificultad.includes("dificil")) {
    return 3;
  }
  return 0;
});

const dificultadIconosArray = computed(() => {
  return Array(dificultadCount.value).fill(0);
});

const dificultadColorClase = computed(() => {
  const count = dificultadCount.value;
  if (count === 1) return "dificultad-facil";
  if (count === 2) return "dificultad-media";
  if (count === 3) return "dificultad-dificil";
  return "";
});

onMounted(() => {
  if (!recetaId.value) {
    router.push("/");
    return;
  }
  fetchReceta();
  loadComentarios();
});
</script>

<style scoped>
.receta-detail-page {
  background-color: var(--fondo-crema);
  min-height: 100vh;
  padding-top: 80px;
}

/* Loader */
.loader-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  text-align: center;
}

.olea-loader {
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
  animation: spin 1.5s linear infinite;
}

.loader-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loader-text {
  font-size: 1.1rem;
  color: var(--color-texto);
  font-weight: 500;
  margin: 0;
}

.receta-detail__btn-like,
.receta-detail__btn-comments {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  padding: 0.45rem 0.9rem;
  border-radius: 9999px;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.receta-detail__btn-like:hover,
.receta-detail__btn-comments:hover {
  background-color: rgba(96, 108, 56, 0.1);
}

.receta-detail__btn-like i {
  color: #f74545;
  font-size: 1.2rem;
  transition: all 0.25s ease;
}

.receta-detail__btn-comments i {
  font-size: 1.1rem;
  color: var(--color-olea);
}

.receta-detail-container {
  display: flex;
  gap: 2rem;
  padding: 1rem 2rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

.receta-detail__img-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.receta-detail__img-container {
  width: 100%;
  max-height: 350px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  background-color: #f0f0f0;
}

.receta-detail__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.receta-detail__img-placeholder {
  width: 100%;
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.9rem;
}

.receta-detail__meta {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
  width: 100%;
}

.receta-detail__data {
  flex: 2;
  overflow-y: auto;
  max-height: 80vh;
  padding-right: 1rem;
}

.receta-detail__titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 1.5rem;
  margin-bottom: 0;
}

.receta-detail__info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}

.receta-detail__info-item {
  background-color: var(--fondo-bloque);
  border-radius: 8px;
  padding: 0.6rem;
  text-align: center;
}

.receta-detail__info-item .label {
  display: block;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.receta-detail__info-item .value {
  font-weight: 500;
  color: var(--color-texto);
}

/* ⭐ Iconos bi-fork-knife con color */
.dificultad-iconos {
  display: inline-flex;
  gap: 0.2rem;
  align-items: center;
}

.bi-icon-color {
  font-size: 1.1rem !important;
  display: inline-block !important;
}

.bi-icon-color.dificultad-facil {
  color: var(--color-olea) !important;
}
.bi-icon-color.dificultad-media {
  color: var(--color-acento) !important;
}
.bi-icon-color.dificultad-dificil {
  color: var(--color-alerta) !important;
}

.receta-detail__separador {
  height: 1px;
  background-color: rgba(96, 108, 56, 0.15);
  margin: 1.5rem 0;
}

.receta-detail__subtitulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
}

.receta-detail__ingredientes {
  list-style: none;
  padding: 0;
  margin: 0;
}

.receta-detail__ingrediente {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.receta-detail__ing-cant {
  min-width: 5rem;
  font-weight: 500;
  color: var(--color-olea);
}

.receta-detail__ing-nombre {
  flex: 1;
  color: var(--color-texto);
}

.receta-detail__preparacion {
  line-height: 1.7;
  color: var(--color-texto);
}

.comentarios-seccion {
  margin-top: 1rem;
}

.comentarios-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comentario-item {
  border-bottom: 1px solid rgba(96, 108, 56, 0.15);
  padding: 0.75rem 0;
}

.comentario-item:last-child {
  border-bottom: none;
}

.comentario-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.comentario-item__autor {
  font-weight: 500;
  color: var(--color-olea);
}

.comentario-item__fecha {
  font-size: 0.75rem;
  color: #666;
}

.comentario-item__texto {
  margin-bottom: 0;
  line-height: 1.5;
}

.comentario-textarea {
  width: 100%;
  resize: vertical;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  color: var(--color-texto);
}

.comentario-textarea:focus {
  outline: none;
  border-color: var(--color-acento);
}

.alert {
  border-radius: 14px;
  text-align: center;
}

@media (max-width: 991px) {
  .receta-detail-container {
    flex-direction: column;
  }

  .receta-detail__data {
    max-height: none;
    padding-right: 0;
  }
}
</style>
