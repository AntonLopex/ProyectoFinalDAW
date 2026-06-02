<!-- views/CrearView.vue -->
<template>
  <div class="crear-page">
    <Navbar />

    <div class="crear-container">
      <h1 class="crear-titulo">Crear nuevo</h1>

      <!-- Botones de selección -->
      <div class="crear-botones">
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
          v-if="modoSeleccionado === 'receta'"
          key="receta"
          class="crear-formulario"
        >
          <FormularioReceta @receta-creada="manejarRecetaCreada" />
        </div>
        <div v-else key="categoria" class="crear-formulario">
          <FormularioCategoria @categoria-creada="manejarCategoriaCreada" />
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import Navbar from "../components/NavBar.vue";
import FormularioReceta from "../components/FormularioReceta.vue";
import FormularioCategoria from "../components/FormularioCategoria.vue";
import api from "../api/axios";

const router = useRouter();
const modoSeleccionado = ref("receta");

const manejarRecetaCreada = (receta) => {
  console.log("Receta creada:", receta);
  // Opcional: redirigir a la receta creada
  router.push(`/recetas/${receta.id}/`);
};

const manejarCategoriaCreada = (categoria) => {
  console.log("Categoría creada:", categoria);
  // Opcional: mostrar mensaje de éxito
};
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
