<template>
  <div class="perfil-page">
    <Navbar />

    <div v-if="loading" class="text-center py-5 mt-5">
      <div class="spinner-border text-olea" role="status">
        <span class="visually-hidden">Cargando perfil...</span>
      </div>
    </div>

    <div v-else-if="usuario" class="perfil-container">
      <!-- Buscador de usuarios -->
      <UsuarioBuscador v-model="searchQuery" @user-selected="goToProfile" />

      <!-- Header del perfil -->
      <div class="perfil-header">
        <div class="perfil-avatar">
          <img
            v-if="usuario.foto_perfil"
            :src="getFullImageUrl(usuario.foto_perfil)"
            :alt="usuario.nombre_usuario"
          />
          <span v-else>{{ usuario.nombre_usuario[0].toUpperCase() }}</span>
        </div>
        <div class="perfil-info">
          <h1 class="perfil-nombre">
            {{ usuario.full_name || usuario.nombre_usuario }}
          </h1>
          <p class="perfil-usuario">@{{ usuario.nombre_usuario }}</p>
          <p v-if="usuario.biografia_y_enlaces" class="perfil-bio">
            {{ usuario.biografia_y_enlaces }}
          </p>
          <div class="perfil-estadisticas">
            <div class="estadistica">
              <strong>{{ totalRecetas }}</strong>
              <span>Recetas</span>
            </div>
            <div class="estadistica">
              <strong>{{ totalLikes }}</strong>
              <span>Likes</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Título de recetas -->
      <h2 class="perfil-titulo">
        Recetas de {{ usuario.full_name || usuario.nombre_usuario }}
      </h2>

      <!-- Grid de recetas -->
      <div v-if="recetas.length > 0" class="perfil-recetas-grid">
        <div
          v-for="receta in recetas"
          :key="receta.id"
          class="receta-card-item"
        >
          <RecetaCard
            :receta="receta"
            @like="handleLike(receta.id)"
            @open-comments="openCommentsModal(receta.id, receta)"
          />
        </div>
      </div>

      <div v-else class="text-center text-muted py-5">
        <i class="bi bi-inbox fs-1"></i>
        <p class="mt-3">Este usuario aún no tiene recetas.</p>
      </div>
    </div>

    <div v-else class="text-center text-muted py-5 mt-5">
      <i class="bi bi-person-x fs-1"></i>
      <p class="mt-3">Usuario no encontrado.</p>
    </div>

    <!-- Modal de comentarios -->
    <ComentariosModal
      v-model:open="comentariosModalOpen"
      :receta-id="comentariosModalRecetaId"
      :receta="comentariosModalReceta"
    />
  </div>
  <Footer />
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";

import ComentariosModal from "../components/ComentariosModal.vue";
import Navbar from "../components/NavBar.vue";
import Footer from "../components/Footer.vue";
import RecetaCard from "../components/RecetaCard.vue";
import UsuarioBuscador from "../components/UsuarioBuscador.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const usuario = ref(null);
const recetas = ref([]);
const loading = ref(true);
const searchQuery = ref("");
const comentariosModalOpen = ref(false);
const comentariosModalRecetaId = ref(null);
const comentariosModalReceta = ref(null);

const totalRecetas = ref(0);
const totalLikes = ref(0);

const getFullImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const baseUrl = "http://localhost:8000";
  return baseUrl + path;
};

const fetchUserProfile = async (username) => {
  loading.value = true;
  try {
    const { data } = await api.get(`/recetas/perfil/${username}/`);
    usuario.value = data.usuario;
    recetas.value = data.recetas;
    totalRecetas.value = data.total_recetas;
    totalLikes.value = data.total_likes;
  } catch (error) {
    console.error("Error al cargar perfil:", error);
    usuario.value = null;
  } finally {
    loading.value = false;
  }
};

const goToProfile = (user) => {
  router.push(`/perfil/${user.nombre_usuario}`);
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
    console.error("Error al dar like:", error);
  }
};

watch(
  () => route.params.username,
  (newUsername) => {
    if (newUsername) {
      fetchUserProfile(newUsername);
    }
  },
);

onMounted(() => {
  if (route.params.username) {
    fetchUserProfile(route.params.username);
  }
});
</script>

<style scoped>
.perfil-page {
  background-color: var(--fondo-crema);
  min-height: 100vh;
  padding-top: 80px;
}

.perfil-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.perfil-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin: 2rem;
  padding: 2.5rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.perfil-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-olea), #8b7355);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 700;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.perfil-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.perfil-info {
  flex: 1;
}

.perfil-nombre {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 2.25rem;
  margin: 0 0 0.25rem 0;
}

.perfil-usuario {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0 0 0.5rem 0;
}

.perfil-bio {
  color: #495057;
  font-size: 1rem;
  margin: 0 0 1rem 0;
  line-height: 1.6;
}

.perfil-estadisticas {
  display: flex;
  gap: 2.5rem;
}

.estadistica {
  text-align: center;
}

.estadistica strong {
  display: block;
  font-size: 1.75rem;
  color: var(--color-olea);
  font-weight: 700;
}

.estadistica span {
  font-size: 0.9rem;
  color: #6c757d;
}

.perfil-titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.perfil-recetas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.receta-card-item {
  width: 100%;
}

@media (max-width: 768px) {
  .perfil-container {
    padding: 1rem;
  }

  .perfil-header {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }

  .perfil-avatar {
    width: 100px;
    height: 100px;
    font-size: 2.5rem;
  }

  .perfil-estadisticas {
    justify-content: center;
    gap: 1.5rem;
  }

  .perfil-nombre {
    font-size: 1.75rem;
  }
}

.text-olea {
  color: var(--color-olea);
}
</style>
