<template>
  <div v-if="visible" class="modal-overlay" @click="cerrar">
    <div class="modal-olea modal-lg" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="bi bi-person-fill"></i>
          {{ usuario ? "Editar Usuario" : "Nuevo Usuario" }}
        </h3>
        <button class="modal-close" @click="cerrar">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Nombre de usuario *</label>
          <input
            v-model="formData.nombre_usuario"
            type="text"
            class="form-control"
            required
          />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Nombre *</label>
            <input
              v-model="formData.nombre"
              type="text"
              class="form-control"
              required
            />
          </div>
          <div class="form-group">
            <label>Apellido 1 *</label>
            <input
              v-model="formData.apellido1"
              type="text"
              class="form-control"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label>Apellido 2</label>
          <input
            v-model="formData.apellido2"
            type="text"
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label>Email *</label>
          <input
            v-model="formData.email"
            type="email"
            class="form-control"
            required
          />
        </div>
        <div class="form-group">
          <label>Biografía</label>
          <textarea
            v-model="formData.biografia_y_enlaces"
            class="form-control"
            rows="3"
          ></textarea>
        </div>
        <div class="form-group">
          <label>Rol *</label>
          <select v-model="formData.rol" class="form-control" required>
            <option value="registrado">Registrado</option>
            <option value="admin">Administrador</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" @click="cerrar">Cancelar</button>
        <button class="btn btn-olea" @click="guardar" :disabled="guardando">
          {{ guardando ? "Guardando..." : "Guardar" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";

const props = defineProps({
  visible: { type: Boolean, required: true },
  usuario: { type: Object, default: null },
});

const emit = defineEmits(["close", "guardar"]);

const guardando = ref(false);

const formData = ref({
  nombre_usuario: "",
  nombre: "",
  apellido1: "",
  apellido2: "",
  email: "",
  biografia_y_enlaces: "",
  rol: "registrado",
});

console.log("ModalUsuario mounted, visible:", props.visible);

watch(
  () => props.usuario,
  (nuevo) => {
    console.log("Usuario cambiado en ModalUsuario:", nuevo);
    if (nuevo) {
      formData.value = {
        nombre_usuario: nuevo.nombre_usuario || "",
        nombre: nuevo.nombre || "",
        apellido1: nuevo.apellido1 || "",
        apellido2: nuevo.apellido2 || "",
        email: nuevo.email || "",
        biografia_y_enlaces: nuevo.biografia_y_enlaces || "",
        rol: nuevo.rol || "registrado",
      };
    } else {
      formData.value = {
        nombre_usuario: "",
        nombre: "",
        apellido1: "",
        apellido2: "",
        email: "",
        biografia_y_enlaces: "",
        rol: "registrado",
      };
    }
  },
  { immediate: true },
);

const cerrar = () => {
  console.log("Cerrando modal usuario");
  emit("close");
};

const guardar = async () => {
  console.log("Guardando formulario:", formData.value);
  guardando.value = true;
  try {
    await emit("guardar", formData.value);
  } finally {
    guardando.value = false;
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
  backdrop-filter: blur(4px);
}
.modal-olea {
  background: var(--fondo-crema);
  border-radius: var(--border-radius);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;

  display: flex;
  flex-direction: column;

  overflow: hidden;
}

.modal-lg {
  max-width: 700px;
}

.modal-xl {
  max-width: 900px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;

  /* Ocultar scrollbar */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE y Edge antiguos */
}

.modal-body::-webkit-scrollbar {
  display: none; /* Chrome, Edge, Safari */
}
.modal-header {
  background: var(--color-olea);
  color: #fff;
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: var(--border-radius) var(--border-radius) 0 0;
}
.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.modal-footer {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  border-top: 1px solid #eee;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-texto);
}
.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  font-size: 1rem;
  color: var(--color-texto);
  background: var(--fondo-crema);
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.form-control:focus {
  outline: none;
  border-color: var(--color-olea);
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-outline {
  background: transparent;
  border-color: #ddd;
  color: var(--color-texto);
}
.btn-outline:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.05);
  border-color: #ccc;
}
.btn-olea {
  background: var(--color-olea);
  border-color: var(--color-olea);
  color: #fff;
}
.btn-olea:hover:not(:disabled) {
  background: #4a552a;
  border-color: #4a552a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(96, 108, 56, 0.3);
}
</style>
