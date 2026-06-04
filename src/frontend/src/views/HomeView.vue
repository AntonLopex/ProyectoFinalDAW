<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../api/axios";

import ComentariosModal from "../components/ComentariosModal.vue";
import Navbar from "../components/NavBar.vue";
import RecetaCard from "../components/RecetaCard.vue";
import CategoriasCarousel from "../components/CategoriasCarousel.vue";
import UsuarioBuscador from "../components/UsuarioBuscador.vue";
import ReporteModal from "../components/ReporteModal.vue";
import Footer from "../components/Footer.vue";

const auth = useAuthStore();
const router = useRouter();
const comentariosModalOpen = ref(false);
const comentariosModalRecetaId = ref(null);
const comentariosModalReceta = ref(null);
const searchQuery = ref("");

const mostrarReporte = ref(false);
const recetaSeleccionada = ref(null);

const abrirModalReporte = (receta) => {
  recetaSeleccionada.value = receta;
  mostrarReporte.value = true;
};

const cerrarModalReporte = () => {
  mostrarReporte.value = false;
  recetaSeleccionada.value = null;
};

const openCommentsModal = (recetaId, receta) => {
  if (!auth.usuario) {
    router.push("/auth");
    return;
  }
  if (!receta) return;
  comentariosModalRecetaId.value = recetaId;
  comentariosModalReceta.value = receta;
  comentariosModalOpen.value = true;
};

const goToProfile = (user) => {
  router.push(`/perfil/${user.nombre_usuario}`);
};

const recetas = ref([]);
const loading = ref(true);

async function fetchRecetas() {
  try {
    const { data } = await api.get("/recetas/recetas/");

    recetas.value = data;
  } catch (error) {
    console.error("Error al cargar recetas:", error);
    console.error("Detalles:", error.response?.status, error.response?.data);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchRecetas();
});

const handleFavorite = async (receta) => {
  const recetaId = receta.id;

  const eraFavorito = !!receta.usuario_favorito;
  receta.usuario_favorito = !eraFavorito;
  receta.favoritos_count = eraFavorito
    ? Math.max((receta.favoritos_count || 0) - 1, 0)
    : (receta.favoritos_count || 0) + 1;

  try {
    if (eraFavorito) {
      await api.delete(`/favoritos/${recetaId}/`);
    } else {
      await api.post(`/favoritos/${recetaId}/`);
    }
  } catch (error) {
    receta.usuario_favorito = eraFavorito;
    receta.favoritos_count = eraFavorito
      ? (receta.favoritos_count || 0) + 1
      : Math.max((receta.favoritos_count || 0) - 1, 0);

    console.error("Error al actualizar favorito:", error);
    alert("No se pudo actualizar favoritos");
  }
};

const handleLike = async (recetaId) => {
  if (!auth.usuario) {
    router.push("/auth");
    return;
  }
  try {
    const { data } = await api.post(`/recetas/recetas/${recetaId}/like/`);

    const receta = recetas.value.find((r) => r.id === recetaId);
    if (receta) {
      receta.likes_count = data.likes_count;
      receta.usuario_like = data.usuario_like;
    }
  } catch (error) {
    console.error("Error al hacer like:", error);
  }
};
</script>

<template>
  <Navbar />

  <CategoriasCarousel />

  <!-- Buscador de usuarios (siempre visible) -->
  <div class="buscar-wrapper">
    <UsuarioBuscador v-model="searchQuery" @user-selected="goToProfile" />
  </div>

  <div class="container mt-5 pt-4">
    <!-- Loader -->
    <div v-if="loading" class="loader-wrapper">
      <div class="olea-loader">
        <img src="../../public/logo.png" alt="OLEA" class="loader-icon" />
      </div>
      <p class="loader-text">Cargando recetas...</p>
    </div>

    <!-- Recetas -->
    <div v-else-if="recetas.length > 0" class="row g-3">
      <div
        v-for="receta in recetas"
        :key="receta.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <RecetaCard
          :receta="receta"
          @open-report="abrirModalReporte"
          @like="handleLike(receta.id)"
          @favorite="handleFavorite(receta)"
          @open-comments="openCommentsModal(receta.id, receta)"
        />
      </div>
      <ComentariosModal
        v-model:open="comentariosModalOpen"
        :receta-id="comentariosModalRecetaId"
        :receta="comentariosModalReceta"
      />
      <ReporteModal
        v-if="mostrarReporte"
        :receta="recetaSeleccionada"
        @close="cerrarModalReporte"
      />
    </div>

    <div v-else class="text-center text-muted py-5">
      No hay recetas disponibles todavía.
    </div>
  </div>
  <Footer />
</template>

<style>
.text-olea {
  color: var(--color-olea);
}

.buscar-wrapper {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
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
</style>
