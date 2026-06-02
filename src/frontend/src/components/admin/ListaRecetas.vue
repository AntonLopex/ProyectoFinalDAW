<template>
  <div class="tab-content">
    <div class="content-header">
      <h2>🍳 Recetas</h2>
      <select
        v-model="filtroLocal"
        class="form-control"
        @change="$emit('cambiar-filtro', filtroLocal)"
      >
        <option :value="null">Todas</option>
        <option :value="true">Visibles</option>
        <option :value="false">Ocultas</option>
      </select>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner-border"></div>
      <p>Cargando...</p>
    </div>

    <div v-else class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Usuario</th>
            <th>Categorías</th>
            <th>Visible</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="receta in recetas" :key="receta.id">
            <td>{{ receta.id }}</td>
            <td class="receta-titulo">{{ receta.titulo }}</td>
            <td>@{{ receta.usuario_nombre }}</td>
            <td>
              <span
                v-for="cat in receta.categorias_nombres"
                :key="cat"
                class="badge badge-cat"
              >
                {{ cat }}
              </span>
            </td>
            <td>
              <span
                :class="[
                  'badge',
                  receta.visible ? 'badge-success' : 'badge-danger',
                ]"
              >
                {{ receta.visible ? "Sí" : "No" }}
              </span>
            </td>
            <td class="acciones">
              <button
                class="btn-icon btn-view"
                @click="$router.push(`/receta/${receta.id}`)"
                title="Ver"
              >
                <i class="bi bi-eye"></i>
              </button>
              <button
                class="btn-icon btn-toggle"
                @click="$emit('toggle-visibilidad', receta)"
                :title="receta.visible ? 'Ocultar' : 'Mostrar'"
              >
                <i
                  :class="receta.visible ? 'bi bi-eye-slash' : 'bi bi-eye'"
                ></i>
              </button>
              <button
                class="btn-icon btn-delete"
                @click="$emit('eliminar-receta', receta)"
                title="Eliminar"
              >
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  recetas: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  filtroVisible: { type: [Boolean, null], default: null },
});

const emit = defineEmits([
  "cambiar-filtro",
  "toggle-visibilidad",
  "eliminar-receta",
]);

const filtroLocal = ref(props.filtroVisible);

watch(
  () => props.filtroVisible,
  (nuevo) => {
    filtroLocal.value = nuevo;
  },
);
</script>

<style scoped>
.tab-content {
  padding: 0;
}
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.content-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-texto);
  font-family: var(--fuente-titulos);
}
.form-control {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  font-size: 0.9rem;
  background: var(--fondo-crema);
  color: var(--color-texto);
}
.table-responsive {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}
.data-table th {
  background: rgba(96, 108, 56, 0.05);
  font-weight: 600;
  color: var(--color-texto);
  font-size: 0.9rem;
  text-transform: uppercase;
}
.data-table tr:hover {
  background: rgba(96, 108, 56, 0.03);
}
.receta-titulo {
  font-weight: 500;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}
.badge-success {
  background: #28a745;
  color: #fff;
}
.badge-danger {
  background: #f74545;
  color: #fff;
}
.badge-cat {
  background: var(--fondo-crema);
  color: var(--color-olea);
  border: 1px solid rgba(96, 108, 56, 0.2);
}
.acciones {
  display: flex;
  gap: 0.25rem;
}
.btn-icon {
  background: transparent;
  border: none;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}
.btn-icon:hover {
  transform: scale(1.1);
}
.btn-view:hover {
  background: rgba(23, 162, 184, 0.1);
  color: #17a2b8;
}
.btn-toggle:hover {
  background: rgba(96, 108, 56, 0.1);
  color: var(--color-olea);
}
.btn-delete:hover {
  background: rgba(247, 69, 69, 0.1);
  color: #f74545;
}
.loading-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}
.spinner-border {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  border: 0.25em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
}
@keyframes spinner-border {
  to {
    transform: rotate(360deg);
  }
}
</style>
