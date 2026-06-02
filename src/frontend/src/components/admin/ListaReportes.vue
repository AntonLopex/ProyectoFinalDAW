<template>
  <div class="tab-content">
    <div class="content-header">
      <h2>🚩 Reportes</h2>
      <select
        v-model="filtroLocal"
        class="form-control"
        @change="$emit('cambiar-filtro', filtroLocal)"
      >
        <option value="">Todos</option>
        <option value="pendiente">Pendientes</option>
        <option value="revisado">Revisados</option>
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
            <th>Informador</th>
            <th>Motivo</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="reporte in reportes" :key="reporte.id">
            <td>{{ reporte.id }}</td>
            <td>@{{ reporte.informador_nombre }}</td>
            <td class="motivo">{{ reporte.motivo }}</td>
            <td>
              <span
                :class="[
                  'badge',
                  reporte.estado === 'pendiente'
                    ? 'badge-warning'
                    : 'badge-secondary',
                ]"
              >
                {{ reporte.estado === "pendiente" ? "Pendiente" : "Revisado" }}
              </span>
            </td>
            <td>{{ formatDate(reporte.created_at) }}</td>
            <td class="acciones">
              <button
                class="btn-icon btn-resolve"
                @click="$emit('resolver-reporte', reporte)"
                :disabled="reporte.estado === 'revisado'"
                title="Resolver"
              >
                <i class="bi bi-check-lg"></i>
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
  reportes: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  filtroEstado: { type: String, default: "" },
});

const emit = defineEmits(["cambiar-filtro", "resolver-reporte"]);

const filtroLocal = ref(props.filtroEstado);

watch(
  () => props.filtroEstado,
  (nuevo) => {
    filtroLocal.value = nuevo;
  },
);

const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};
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
.motivo {
  max-width: 300px;
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
.badge-warning {
  background: #ffc107;
  color: #000;
}
.badge-secondary {
  background: #6c757d;
  color: #fff;
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
.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  transform: none;
}
.btn-resolve:hover {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
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
