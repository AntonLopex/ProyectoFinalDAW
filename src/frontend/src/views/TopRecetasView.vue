<template>
  <Navbar />

  <div v-if="loading" class="text-center py-5 mt-5">
    <div class="spinner-border text-olea" role="status">
      <span class="visually-hidden">Cargando top recetas...</span>
    </div>
  </div>

  <div v-else-if="recetas.length > 0" class="top-recetas-container">
    <div class="top-recetas-header">
      <i class="bi bi-trophy-fill top-recetas__icon"></i>
      <h1 class="top-recetas__titulo">Top 6 Recetas más Liked</h1>
      <p class="top-recetas__subtitle">Las recetas Favoritas de la comunidad</p>
    </div>

    <div class="top-recetas__grid">
      <div
        v-for="(receta, index) in recetas"
        :key="receta.id"
        class="top-receta-wrapper"
        :class="getRankClass(index)"
      >
        <div class="rank-badge" :class="getBadgeClass(index)">
          <span class="rank-number">{{ index + 1 }}</span>
          <i
            v-if="index < 3"
            :class="getBadgeIcon(index)"
            class="rank-icon"
          ></i>
        </div>
        <RecetaCard
          :receta="receta"
          @like="handleLike(receta.id)"
          @favorite="handleFavorite(receta)"
          @open-comments="openCommentsModal(receta.id, receta)"
        />
      </div>
    </div>

    <ComentariosModal
      v-model:open="comentariosModalOpen"
      :receta-id="comentariosModalRecetaId"
      :receta="comentariosModalReceta"
    />
  </div>

  <div v-else class="text-center text-muted py-5 mt-5">
    <i class="bi bi-inbox fs-1"></i>
    <p class="mt-3">No hay recetas disponibles.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../api/axios";

import ComentariosModal from "../components/ComentariosModal.vue";
import Navbar from "../components/NavBar.vue";
import RecetaCard from "../components/RecetaCard.vue";

const auth = useAuthStore();
const router = useRouter();

const comentariosModalOpen = ref(false);
const comentariosModalRecetaId = ref(null);
const comentariosModalReceta = ref(null);

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

const recetas = ref([]);
const loading = ref(true);

const fetchTopRecetas = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/recetas/top-recetas/");
    recetas.value = data;
  } catch (error) {
    console.error("Error al cargar top recetas:", error);
  } finally {
    loading.value = false;
  }
};

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
    console.error("Error al dar like:", error);
  }
};

const getRankClass = (index) => {
  if (index === 0) return "rank-1";
  if (index === 1) return "rank-2";
  if (index === 2) return "rank-3";
  return "";
};

const getBadgeClass = (index) => {
  if (index === 0) return "badge-gold";
  if (index === 1) return "badge-silver";
  if (index === 2) return "badge-bronze";
  return "badge-default";
};

const getBadgeIcon = (index) => {
  if (index === 0) return "bi bi-trophy-fill";
  if (index === 1) return "bi bi-trophy-fill";
  if (index === 2) return "bi bi-trophy-fill";
  return "";
};

onMounted(() => {
  fetchTopRecetas();
});
</script>

<style scoped>
.top-recetas-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.top-recetas-header {
  text-align: center;
  margin: 3rem;
}

.top-recetas__icon {
  font-size: 3.5rem;
  color: var(--color-olea);
  margin-bottom: 1rem;
  display: block;
}

.top-recetas__titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.top-recetas__subtitle {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

.top-recetas__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.top-receta-wrapper {
  position: relative;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.top-receta-wrapper:hover {
  transform: translateY(-5px);
}

.rank-badge {
  position: absolute;
  top: -10px;
  left: -10px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  padding: 2px 0;
}

.rank-number {
  font-weight: 700;
  font-size: 1rem;
  color: #fff;
  line-height: 1;
}

.rank-icon {
  font-size: 0.65rem;
  color: #fff;
  margin-top: 2px;
}

.badge-gold {
  background: linear-gradient(135deg, #ffd700, #ffb300);
  border: 2px solid #ffd700;
}

.badge-silver {
  background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
  border: 2px solid #c0c0c0;
}

.badge-bronze {
  background: linear-gradient(135deg, #cd7f32, #b87333);
  border: 2px solid #cd7f32;
}

.badge-default {
  background: linear-gradient(135deg, #6c757d, #495057);
  border: 2px solid #6c757d;
}

/* Top 1 - Sombra dorada más notable */
.rank-1 {
  box-shadow: 0 12px 40px rgba(255, 215, 0, 0.75);
  border-radius: 12px;
}

/* Top 2 - Sombra plateada más notable */
.rank-2 {
  box-shadow: 0 12px 40px rgba(192, 192, 192, 0.75);
  border-radius: 12px;
}

/* Top 3 - Sombra bronce más notable */
.rank-3 {
  box-shadow: 0 12px 40px rgba(205, 127, 50, 0.75);
  border-radius: 12px;
}

@media (max-width: 768px) {
  .top-recetas-container {
    padding: 1rem;
  }

  .top-recetas__titulo {
    font-size: 1.75rem;
  }

  .top-recetas__icon {
    font-size: 2.5rem;
  }

  .top-recetas__grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.text-olea {
  color: var(--color-olea);
}
</style>
