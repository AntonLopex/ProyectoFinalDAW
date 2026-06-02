<template>
  <div class="categoria-page">
    <Navbar />

    <div class="container py-5">
      <h1 class="categoria-title">
        {{ nombreCategoria }}
      </h1>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-olea"></div>
      </div>

      <div v-else-if="recetas.length" class="recetas-grid">
        <RecetaCard
          v-for="receta in recetas"
          :key="receta.id"
          :receta="receta"
          @like="toggleLike(receta)"
          @open-comments="openComentarios"
        />
      </div>
      <div v-else class="text-center text-muted py-5">
        No hay recetas en esta categoría.
      </div>
      <ComentariosModal
        v-model:open="showComentariosModal"
        :receta="recetaSeleccionada"
        :receta-id="recetaSeleccionada?.id"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import Navbar from "../components/NavBar.vue";
import RecetaCard from "../components/RecetaCard.vue";
import ComentariosModal from "../components/ComentariosModal.vue";

import api from "../api/axios";

const route = useRoute();
const router = useRouter();

const recetas = ref([]);
const loading = ref(true);

const showComentariosModal = ref(false);
const recetaSeleccionada = ref(null);

const categoriaId = computed(() => parseInt(route.params.id));

const nombreCategoria = computed(() => {
  if (!recetas.value.length) return "Categoría";

  return (
    recetas.value[0]?.categorias?.find((c) => c.id === categoriaId.value)
      ?.nombre || "Categoría"
  );
});

const openComentarios = (receta) => {
  recetaSeleccionada.value = receta;
  showComentariosModal.value = true;
};

const fetchRecetas = async () => {
  loading.value = true;

  try {
    const { data } = await api.get(
      `/recetas/categorias/${categoriaId.value}/recetas/`,
    );

    recetas.value = data;
  } catch (error) {
    console.error(error);
    router.push("/");
  } finally {
    loading.value = false;
  }
};

const toggleLike = async (receta) => {
  try {
    const { data } = await api.post(`/recetas/recetas/${receta.id}/like/`);

    receta.likes_count = data.likes_count;
    receta.usuario_like = data.usuario_like;
  } catch (error) {
    console.error(error);
  }
};

onMounted(fetchRecetas);
</script>

<style scoped>
.categoria-page {
  margin-top: 56px;
  min-height: 100vh;
  background-color: var(--fondo-crema);
}

.categoria-title {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);

  margin-bottom: 2rem;

  text-align: center;
}

.recetas-grid {
  display: grid;

  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));

  gap: 1.5rem;
}
</style>
