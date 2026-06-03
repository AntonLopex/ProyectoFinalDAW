<template>
  <div class="usuario-buscador">
    <div class="input-group-pill">
      <span class="input-icon">
        <i class="bi bi-search"></i>
      </span>
      <input
        v-model="searchQuery"
        @input="debounceSearch"
        type="text"
        class="form-control-pill"
        placeholder="Buscar usuarios"
      />
    </div>

    <!-- Resultados del buscador -->
    <div
      v-if="searchResults.length > 0 && searchQuery.length >= 2"
      class="buscador-resultados"
    >
      <div
        v-for="user in searchResults"
        :key="user.id"
        class="buscador-item"
        @click="selectUser(user)"
      >
        <div class="buscador-avatar">
          <img
            v-if="user.foto_perfil"
            :src="user.foto_perfil"
            :alt="user.nombre_usuario"
          />
          <span v-else>{{ user.nombre_usuario[0].toUpperCase() }}</span>
        </div>
        <div class="buscador-info">
          <strong>{{ user.full_name }}</strong>
          <span>@{{ user.nombre_usuario }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/axios";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["update:modelValue", "user-selected"]);

const searchQuery = ref(props.modelValue);
const searchResults = ref([]);
let searchTimeout = null;

const searchUser = async () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = [];
    return;
  }

  try {
    const { data } = await api.get(
      `/recetas/buscar-usuario/?q=${searchQuery.value}`,
    );
    searchResults.value = data.usuarios;
  } catch (error) {
    console.error("Error al buscar usuario:", error);
  }
};

const debounceSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchUser();
    emit("update:modelValue", searchQuery.value);
  }, 300);
};

const selectUser = (user) => {
  emit("user-selected", user);
  searchQuery.value = "";
  searchResults.value = [];
};
</script>

<style scoped>
.usuario-buscador {
  position: relative;
}

.input-group-pill {
  display: flex;
  align-items: center;
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 50px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid var(--color-olea);
  transition:
    border-color 0.3s,
    box-shadow 0.3s;
}

.input-group-pill:focus-within {
  border-color: var(--color-olea);
  box-shadow: 0 4px 20px rgba(139, 115, 85, 0.2);
}

.input-icon {
  padding: 0.75rem 1rem;
  color: var(--fondo-crema);
  font-size: 1.2rem;
  background: var(--color-olea);
}

.form-control-pill {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  background: transparent;
}

.form-control-pill::placeholder {
  color: #adb5bd;
}

.buscador-resultados {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 100;
  margin-top: 8px;
  overflow: hidden;
}

.buscador-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.buscador-item:hover {
  background: #f8f9fa;
}

.buscador-item:last-child {
  border-bottom: none;
}

.buscador-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-olea), #8b7355);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  overflow: hidden;
  flex-shrink: 0;
}

.buscador-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.buscador-info {
  flex: 1;
}

.buscador-info strong {
  display: block;
  color: var(--color-olea);
  font-size: 0.95rem;
}

.buscador-info span {
  font-size: 0.85rem;
  color: #6c757d;
}
</style>
