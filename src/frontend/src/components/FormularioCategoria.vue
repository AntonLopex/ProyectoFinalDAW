<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";

const router = useRouter();
const emit = defineEmits(["categoria-creada"]);

const enviando = ref(false);
const mostrarModal = ref(false);
const categoriaNombre = ref("");

const formData = ref({
  nombre: "",
});

const enviarFormulario = async () => {
  if (!formData.value.nombre.trim()) {
    alert("Por favor, escribe el nombre de la categoría");
    return;
  }

  enviando.value = true;

  try {
    const payload = {
      nombre: formData.value.nombre.trim(),
    };

    const { data } = await api.post("/recetas/categorias/", payload);
    emit("categoria-creada", data);

    // Mostrar modal de éxito
    categoriaNombre.value = data.nombre;
    mostrarModal.value = true;

    // Resetear formulario
    formData.value.nombre = "";
  } catch (error) {
    console.error("Error al crear categoría:", error);
    alert("Error al crear la categoría. Revisa los datos.");
  } finally {
    enviando.value = false;
  }
};

const añadirOtraCategoria = () => {
  mostrarModal.value = false;
  formData.value.nombre = "";
};

const volverAlInicio = () => {
  mostrarModal.value = false;
  router.push("/");
};
</script>

<template>
  <form @submit.prevent="enviarFormulario" class="formulario-categoria">
    <h2 class="formulario-titulo">Nueva Categoría</h2>

    <!-- Nombre -->
    <div class="form-group">
      <label for="nombre">Nombre de la categoría *</label>
      <input
        id="nombre"
        v-model="formData.nombre"
        type="text"
        class="form-control"
        placeholder="Ej: Postres, Desayunos, Veganas, Picoteo..."
        required
        autofocus
      />
    </div>

    <!-- Botón enviar -->
    <button type="submit" class="btn btn-olea btn-submit" :disabled="enviando">
      <span v-if="!enviando">Crear Categoría</span>
      <span v-else>
        <div class="spinner-border spinner-border-sm" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        Enviando...
      </span>
    </button>
  </form>

  <!-- Modal de confirmación -->
  <transition name="modal">
    <div v-if="mostrarModal" class="modal-overlay" @click="volverAlInicio">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <i class="bi bi-check-circle-fill modal-icon"></i>
          <h3>¡Éxito!</h3>
        </div>
        <div class="modal-body">
          <p>
            Categoría <strong>{{ categoriaNombre }}</strong> creada con éxito.
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="añadirOtraCategoria">
            <i class="bi bi-plus-lg"></i> Añadir otra categoría
          </button>
          <button class="btn btn-olea" @click="volverAlInicio">
            <i class="bi bi-house-door"></i> Volver al inicio
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.formulario-categoria {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 500px;
  margin: 0 auto;
}

.formulario-titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--color-texto);
  font-size: 0.95rem;
}

.form-control {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-texto);
  background: #fff;
  width: 100%;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-acento);
}

.btn-submit {
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  width: 100%;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-border {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: var(--fondo-crema);
  border-radius: 16px;
  max-width: 400px;
  width: 100%;
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.modal-header {
  background: var(--color-olea);
  color: #fff;
  padding: 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.modal-icon {
  font-size: 3rem;
}

.modal-body {
  padding: 1.5rem;
  text-align: center;
}

.modal-body p {
  margin: 0;
  color: var(--color-texto);
  font-size: 1rem;
  line-height: 1.6;
}

.modal-footer {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-footer .btn {
  width: 100%;
  padding: 0.85rem;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-outline {
  background: transparent;
  border: 2px solid var(--color-olea);
  color: var(--color-olea);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: rgba(96, 108, 56, 0.1);
}

.btn-olea {
  background: var(--color-olea);
  border: 2px solid var(--color-olea);
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-olea:hover {
  background: #4a552a;
  border-color: #4a552a;
}

/* Transición modal */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
}

/* Responsive */
@media (max-width: 768px) {
  .formulario-titulo {
    font-size: 1.25rem;
  }

  .form-control {
    font-size: 0.95rem;
  }

  .btn-submit {
    font-size: 1rem;
    padding: 0.85rem;
  }

  .modal-header {
    padding: 1.25rem;
  }

  .modal-header h3 {
    font-size: 1.25rem;
  }

  .modal-icon {
    font-size: 2.5rem;
  }

  .modal-body {
    padding: 1.25rem;
  }

  .modal-footer {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .formulario-categoria {
    gap: 1rem;
  }

  .modal-content {
    margin: 0.5rem;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-body {
    padding: 1rem;
    font-size: 0.9rem;
  }

  .modal-footer {
    padding: 0.75rem;
  }

  .modal-footer .btn {
    padding: 0.75rem;
    font-size: 0.95rem;
  }
}
</style>
