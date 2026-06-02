<template>
  <div
    class="categorias-carousel"
    ref="carousel"
    @mouseenter="pauseAutoScroll"
    @mouseleave="handleMouseLeave"
    @mousedown="startDrag"
    @mousemove="onDrag"
    @mouseup="stopDrag"
    @touchstart="startTouch"
    @touchmove="onTouchMove"
    @touchend="stopDrag"
  >
    <div class="categorias-track">
      <div
        v-for="(categoria, index) in duplicatedCategorias"
        :key="index"
        class="categoria-badge"
        @click="goToCategoria(categoria.id)"
      >
        {{ categoria.nombre }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import api from "../api/axios";
import { useRouter } from "vue-router";

const router = useRouter();

const categorias = ref([]);

const carousel = ref(null);

let animationFrame = null;
let autoScrolling = true;

let isDragging = false;
let startX = 0;
let scrollLeft = 0;

const duplicatedCategorias = computed(() => {
  if (categorias.value.length <= 1) {
    return categorias.value;
  }

  return [...categorias.value, ...categorias.value];
});

const loadCategorias = async () => {
  try {
    const { data } = await api.get("/recetas/categorias/");
    categorias.value = data;
  } catch (error) {
    console.error("Error cargando categorías:", error);
  }
};

const goToCategoria = (id) => {
  router.push(`/categoria/${id}`);
};

const handleMouseLeave = () => {
  stopDrag();
  resumeAutoScroll();
};

const autoScroll = () => {
  if (!carousel.value || !autoScrolling) return;

  carousel.value.scrollLeft += 0.5;

  const maxScroll = carousel.value.scrollWidth / 2;

  if (carousel.value.scrollLeft >= maxScroll) {
    carousel.value.scrollLeft = 0;
  }

  animationFrame = requestAnimationFrame(autoScroll);
};

const pauseAutoScroll = () => {
  autoScrolling = false;
};

const resumeAutoScroll = () => {
  if (!autoScrolling) {
    autoScrolling = true;
    autoScroll();
  }
};

const startDrag = (e) => {
  isDragging = true;
  pauseAutoScroll();

  startX = e.pageX - carousel.value.offsetLeft;
  scrollLeft = carousel.value.scrollLeft;
};

const onDrag = (e) => {
  if (!isDragging) return;

  e.preventDefault();

  const x = e.pageX - carousel.value.offsetLeft;
  const walk = (x - startX) * 1.5;

  carousel.value.scrollLeft = scrollLeft - walk;
};

const stopDrag = () => {
  isDragging = false;
  resumeAutoScroll();
};

const startTouch = (e) => {
  isDragging = true;
  pauseAutoScroll();

  startX = e.touches[0].pageX;
  scrollLeft = carousel.value.scrollLeft;
};

const onTouchMove = (e) => {
  if (!isDragging) return;

  const x = e.touches[0].pageX;
  const walk = (x - startX) * 1.5;

  carousel.value.scrollLeft = scrollLeft - walk;
};

onMounted(async () => {
  await loadCategorias();
  autoScroll();
});

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrame);
});
</script>

<style scoped>
.categorias-carousel {
  width: 100%;
  overflow-x: scroll;
  overflow-y: hidden;
  cursor: grab;
  user-select: none;
  scrollbar-width: none;
  padding: 1rem 0;
  margin-top: 80px;
}

.categorias-carousel::-webkit-scrollbar {
  display: none;
}

.categorias-track {
  display: flex;
  gap: 1rem;
  width: max-content;
  padding-inline: 2rem;
}

.categoria-badge {
  flex-shrink: 0;

  background-color: var(--color-olea);
  color: white;

  border: 1px solid var(--color-olea);

  border-radius: 9999px;

  padding: 0.65rem 1.25rem;

  font-size: 0.9rem;
  font-weight: 500;

  transition: all 0.25s ease;

  box-shadow: var(--shadow-soft);

  cursor: pointer;
}

.categoria-badge:hover {
  background-color: white;
  color: var(--color-olea);

  transform: translateY(-2px);
}

.categoria-badge:active {
  transform: scale(0.96);
}
</style>
