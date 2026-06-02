<!-- components/admin/ListaUsuarios.vue -->
<template>
  <div class="tab-content">
    <div class="content-header">
      <h2>👥 Usuarios</h2>
      <button class="btn btn-olea" @click="$emit('abrir-modal-usuario')">
        <i class="bi bi-plus-lg"></i> Nuevo
      </button>
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
            <th>Usuario</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Recetas</th>
            <th>Strikes</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="usuario in usuarios"
            :key="usuario.id"
            :class="getRowClass(usuario.strikes_count)"
          >
            <td>{{ usuario.id }}</td>
            <td class="username">@{{ usuario.nombre_usuario }}</td>
            <td>{{ usuario.nombre }} {{ usuario.apellido1 }}</td>
            <td>{{ usuario.email }}</td>
            <td>
              <span
                :class="[
                  'badge',
                  usuario.es_admin === true ? 'badge-admin' : 'badge-user',
                ]"
              >
                {{ usuario.es_admin === true ? "Admin" : "Usuario" }}
              </span>
            </td>
            <td>{{ usuario.recetas_count }}</td>
            <td>
              <span
                :class="[
                  'strikes-count',
                  getStrikeClass(usuario.strikes_count),
                ]"
              >
                {{ usuario.strikes_count }}
              </span>
            </td>
            <td class="acciones">
              <button
                class="btn-icon btn-edit"
                @click="$emit('editar-usuario', usuario)"
                title="Editar"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button
                class="btn-icon btn-delete"
                @click="$emit('eliminar-usuario', usuario)"
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
defineProps({
  usuarios: { type: Array, required: true },
  loading: { type: Boolean, default: false },
});

defineEmits(["abrir-modal-usuario", "editar-usuario", "eliminar-usuario"]);

const getRowClass = (strikesCount) => {
  const strikes = parseInt(strikesCount) || 0;

  if (strikes >= 3) {
    return "row-danger";
  } else if (strikes >= 2) {
    return "row-warning";
  }
  return "";
};

const getStrikeClass = (strikesCount) => {
  const strikes = parseInt(strikesCount) || 0;

  if (strikes >= 3) {
    return "strike-danger";
  } else if (strikes >= 2) {
    return "strike-warning";
  }
  return "";
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

/* Filas con strikes - 2 strikes = naranja suave */
.data-table tr.row-warning {
  background-color: #fff3cd !important;
  border-left: 4px solid #ffc107;
  margin-left: -1rem;
  padding-left: 1rem;
}

/* Filas con strikes - 3+ strikes = rojo suave */
.data-table tr.row-danger {
  background-color: #f8d7da !important;
  border-left: 4px solid #dc3545;
  margin-left: -1rem;
  padding-left: 1rem;
}

/* Hover mejorado en filas con strikes */
.data-table tr.row-warning:hover {
  background-color: #ffeaa7 !important;
}

.data-table tr.row-danger:hover {
  background-color: #f5c6cb !important;
}

.username {
  font-weight: 600;
  color: var(--color-olea);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-admin {
  background: var(--color-olea);
  color: #fff;
}

.badge-user {
  background: #6c757d;
  color: #fff;
}

.strikes-count {
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
  min-width: 24px;
  text-align: center;
}

.strike-warning {
  color: #856404;
  background: #fff3cd;
  font-weight: 700;
  border: 1px solid #ffc107;
}

.strike-danger {
  color: #721c24;
  background: #f8d7da;
  font-weight: 700;
  border: 1px solid #dc3545;
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

.btn-edit:hover {
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
  margin-right: 0.5rem;
  vertical-align: text-bottom;
}

@keyframes spinner-border {
  to {
    transform: rotate(360deg);
  }
}
</style>
