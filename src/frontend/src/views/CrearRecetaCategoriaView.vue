<template>
  <div class="crear-page">
    <Navbar />

    <div class="crear-container">
      <h1 class="crear-titulo">Crear nuevo</h1>

      <!-- Loader -->
      <div v-if="loading" class="loader-wrapper">
        <div class="olea-loader">
          <img src="../../public/logo.png" alt="OLEA" class="loader-icon" />
        </div>
        <p class="loader-text">Cargando...</p>
      </div>

      <!-- Botones de selección -->
      <div v-else class="crear-botones">
        <button
          class="crear-btn"
          :class="{ 'crear-btn-active': modoSeleccionado === 'receta' }"
          @click="modoSeleccionado = 'receta'"
        >
          <i class="bi bi-journal-text"></i>
          Crear Receta
        </button>
        <button
          class="crear-btn"
          :class="{ 'crear-btn-active': modoSeleccionado === 'categoria' }"
          @click="modoSeleccionado = 'categoria'"
        >
          <i class="bi bi-tags"></i>
          Crear Categoría
        </button>
      </div>

      <!-- Formulario de Receta -->
      <transition name="fade" mode="out-in">
        <div
          v-if="modoSeleccionado === 'receta' && !loading"
          key="receta"
          class="crear-formulario"
        >
          <FormularioReceta @receta-creada="manejarRecetaCreada" />
        </div>
        <div v-else-if="!loading" key="categoria" class="crear-formulario">
          <FormularioCategoria @categoria-creada="manejarCategoriaCreada" />
        </div>
      </transition>
    </div>
  </div>
  <Footer />
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import Navbar from "../components/NavBar.vue";
import FormularioReceta from "../components/FormularioReceta.vue";
import FormularioCategoria from "../components/FormularioCategoria.vue";
import Footer from "../components/Footer.vue";

const router = useRouter();
const modoSeleccionado = ref("receta");
const loading = ref(true);




onMounted(() => {
  // Simular carga inicial (puedes eliminar esto si no necesitas carga asíncrona)
  setTimeout(() => {
    loading.value = false;
  }, 500);
});
</script>

<style scoped>
.crear-page {
  background-color: var(--fondo-crema);
  min-height: 100vh;
  padding-top: 80px;
}

.crear-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.crear-titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 2rem;
  text-align: center;
  margin-bottom: 2rem;
}

.crear-botones {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.crear-btn {
  flex: 1;
  max-width: 250px;
  padding: 1rem 1.5rem;
  border: 2px solid var(--color-olea);
  border-radius: 12px;
  background: transparent;
  color: var(--color-olea);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.crear-btn:hover {
  background: rgba(96, 108, 56, 0.1);
}

.crear-btn-active {
  background: var(--color-olea);
  color: #fff;
}

.crear-btn-active:hover {
  background: #4a552a;
}

.crear-formulario {
  background: var(--fondo-bloque);
  border-radius: 14px;
  padding: 2rem;
  box-shadow: var(--shadow-soft);
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

/* Transición fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .crear-container {
    padding: 1rem;
  }

  .crear-botones {
    flex-direction: column;
    align-items: center;
  }

  .crear-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
