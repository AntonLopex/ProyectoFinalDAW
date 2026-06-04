<template>
  <div class="admin-page">
    <div class="navbar-container">
      <nav-bar />
    </div>

    <!-- Contenido Admin -->
    <div class="admin-container">
      <div class="admin-header">
        <h1 class="admin-titulo">
          <i class="bi bi-shield-check"></i> Panel de Administrador
        </h1>
        <p class="admin-subtitulo">Gestiona usuarios, recetas y reportes</p>
      </div>

      <!-- Stats -->
      <div class="admin-stats">
        <div class="stat-card">
          <div class="stat-icon bg-primary">
            <i class="bi bi-people-fill"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.total_usuarios }}</h3>
            <p>Usuarios</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-success">
            <i class="bi bi-journal-text"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.total_recetas }}</h3>
            <p>Recetas</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-info"><i class="bi bi-eye-fill"></i></div>
          <div class="stat-info">
            <h3>{{ stats.recetas_visibles }}</h3>
            <p>Visibles</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-warning">
            <i class="bi bi-eye-slash-fill"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.recetas_ocultas }}</h3>
            <p>Ocultas</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-danger"><i class="bi bi-flag-fill"></i></div>
          <div class="stat-info">
            <h3>{{ stats.reportes_pendientes }}</h3>
            <p>Reportes</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-secondary">
            <i class="bi bi-x-circle-fill"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.total_strikes }}</h3>
            <p>Strikes</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="admin-tabs">
        <button
          :class="['tab-btn', { active: tabActual === 'usuarios' }]"
          @click="tabActual = 'usuarios'"
        >
          <i class="bi bi-people"></i> Usuarios
        </button>
        <button
          :class="['tab-btn', { active: tabActual === 'recetas' }]"
          @click="tabActual = 'recetas'"
        >
          <i class="bi bi-journal-text"></i> Recetas
        </button>
        <button
          :class="['tab-btn', { active: tabActual === 'reportes' }]"
          @click="tabActual = 'reportes'"
        >
          <i class="bi bi-flag"></i> Reportes<span
            v-if="stats.reportes_pendientes > 0"
            class="tab-badge"
            >{{ stats.reportes_pendientes }}</span
          >
        </button>
      </div>

      <!-- Contenido -->
      <div class="admin-content card">
        <ListaUsuarios
          v-if="tabActual === 'usuarios'"
          :usuarios="usuarios"
          :loading="loading"
          @abrir-modal-usuario="abrirModalUsuario(null)"
          @editar-usuario="abrirModalUsuario"
          @eliminar-usuario="eliminarUsuario"
        />

        <ListaRecetas
          v-if="tabActual === 'recetas'"
          :recetas="recetas"
          :loading="loading"
          :filtro-visible="filtroVisible"
          @cambiar-filtro="
            filtroVisible = $event;
            cargarRecetas();
          "
          @toggle-visibilidad="toggleVisibilidad"
          @eliminar-receta="eliminarReceta"
        />

        <ListaReportes
          v-if="tabActual === 'reportes'"
          :reportes="reportes"
          :loading="loading"
          :filtro-estado="filtroEstado"
          @cambiar-filtro="
            filtroEstado = $event;
            cargarReportes();
          "
          @resolver-reporte="abrirModalResolver"
        />
      </div>
    </div>

    <!-- Modales -->
    <ModalUsuario
      :visible="mostrarModalUsuario"
      :usuario="usuarioEdicion"
      @close="mostrarModalUsuario = false"
      @guardar="guardarUsuario"
    />

    <ModalResolverReporte
      :visible="mostrarModalResolver"
      :reporte="reporteSeleccionado"
      @close="mostrarModalResolver = false"
      @resolver="resolverReporte"
    />
  </div>
  <Footer />
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";
import ListaUsuarios from "../components/admin/ListaUsuarios.vue";
import ListaRecetas from "../components/admin/ListaRecetas.vue";
import ListaReportes from "../components/admin/ListaReportes.vue";
import ModalUsuario from "../components/admin/ModalUsuario.vue";
import ModalResolverReporte from "../components/admin/ModalResolverReporte.vue";
import NavBar from "../components/NavBar.vue";
import Footer from "../components/Footer.vue";

const router = useRouter();
const mobileMenuOpen = ref(false);
const usuarioActual = ref(null);

const stats = ref({
  total_usuarios: 0,
  total_recetas: 0,
  recetas_visibles: 0,
  recetas_ocultas: 0,
  reportes_pendientes: 0,
  total_strikes: 0,
});
const usuarios = ref([]);
const recetas = ref([]);
const reportes = ref([]);
const tabActual = ref("usuarios");
const loading = ref(false);

const filtroVisible = ref(null);
const filtroEstado = ref("");
const mostrarModalUsuario = ref(false);
const mostrarModalResolver = ref(false);
const usuarioEdicion = ref(null);
const reporteSeleccionado = ref(null);

const cargarStats = async () => {
  try {
    const { data } = await api.get("/recetas/admin/");
    stats.value = data;
  } catch (error) {
    console.error("Error stats:", error);
  }
};

const cargarUsuarios = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/recetas/admin/usuarios/");
    usuarios.value = data;
  } catch (error) {
    console.error("Error usuarios:", error);
  } finally {
    loading.value = false;
  }
};

const cargarRecetas = async () => {
  loading.value = true;
  try {
    const params =
      filtroVisible.value !== null ? { visible: filtroVisible.value } : {};
    const { data } = await api.get("/recetas/admin/recetas/", { params });
    recetas.value = data;
  } catch (error) {
    console.error("Error recetas:", error);
  } finally {
    loading.value = false;
  }
};

const cargarReportes = async () => {
  loading.value = true;
  try {
    const params = filtroEstado.value ? { estado: filtroEstado.value } : {};
    const { data } = await api.get("/recetas/admin/reportes/", { params });
    reportes.value = data;
  } catch (error) {
    console.error("Error reportes:", error);
  } finally {
    loading.value = false;
  }
};

const abrirModalUsuario = (usuario = null) => {
  usuarioEdicion.value = usuario;
  mostrarModalUsuario.value = true;
};

const guardarUsuario = async (formData) => {
  try {
    if (usuarioEdicion.value) {
      await api.patch(
        `/recetas/admin/usuarios/${usuarioEdicion.value.id}/`,
        formData,
      );
    } else {
      await api.post("/recetas/admin/usuarios/", formData);
    }
    mostrarModalUsuario.value = false;
    usuarioEdicion.value = null;
    cargarUsuarios();
    cargarStats();
  } catch (error) {
    console.error("Error guardar:", error);
    alert("Error: " + JSON.stringify(error.response?.data));
  }
};

const eliminarUsuario = async (usuario) => {
  if (!confirm(`¿Eliminar @${usuario.nombre_usuario}?`)) return;
  try {
    await api.delete(`/recetas/admin/usuarios/${usuario.id}/`);
    cargarUsuarios();
    cargarStats();
  } catch (error) {
    console.error("Error eliminar:", error);
  }
};

const toggleVisibilidad = async (receta) => {
  try {
    await api.patch(`/recetas/admin/recetas/${receta.id}/`, {
      visible: !receta.visible,
    });
    cargarRecetas();
    cargarStats();
  } catch (error) {
    console.error("Error visibilidad:", error);
  }
};

const eliminarReceta = async (receta) => {
  if (!confirm(`¿Eliminar "${receta.titulo}"?`)) return;
  try {
    await api.delete(`/recetas/admin/recetas/${receta.id}/`);
    cargarRecetas();
    cargarStats();
  } catch (error) {
    console.error("Error eliminar:", error);
  }
};

const abrirModalResolver = (reporte) => {
  reporteSeleccionado.value = reporte;
  mostrarModalResolver.value = true;
};

const resolverReporte = async ({ decision, motivo_strike }) => {
  try {
    await api.patch(
      `/recetas/admin/reportes/${reporteSeleccionado.value.id}/`,
      { decision, motivo_strike },
    );
    mostrarModalResolver.value = false;
    reporteSeleccionado.value = null;
    cargarReportes();
    cargarStats();
    alert(
      decision === "valido"
        ? "✅ Reporte válido. Contenido eliminado y strike aplicado."
        : "✅ Reporte inválido. Contenido restaurado.",
    );
  } catch (error) {
    console.error("Error resolver:", error);
    alert("Error: " + JSON.stringify(error.response?.data));
  }
};

const cerrarSesion = () => router.push("/");

onMounted(async () => {
  await cargarStats();
  await cargarUsuarios();
  await cargarRecetas();
  await cargarReportes();
});
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: var(--fondo-principal);
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
.admin-header {
  margin-bottom: 2rem;
  text-align: center;
}
.admin-titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}
.admin-subtitulo {
  color: #666;
  font-size: 1rem;
  margin: 0;
}
.admin-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: var(--fondo-bloque);
  border-radius: var(--border-radius);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow-soft);
}
.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #fff;
}
.bg-primary {
  background: #6f42c1;
}
.bg-success {
  background: #28a745;
}
.bg-info {
  background: #17a2b8;
}
.bg-warning {
  background: #ffc107;
  color: #000;
}
.bg-danger {
  background: #f74545;
}
.bg-secondary {
  background: #6c757d;
}
.stat-info h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-texto);
}
.stat-info p {
  margin: 0;
  font-size: 0.85rem;
  color: #666;
}
.admin-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0;
}
.tab-btn {
  padding: 0.85rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  color: #666;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.tab-btn:hover {
  color: var(--color-olea);
}
.tab-btn.active {
  color: var(--color-olea);
  border-bottom-color: var(--color-olea);
}
.tab-badge {
  background: #f74545;
  color: #fff;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
}
.admin-content {
  background: var(--fondo-bloque);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-soft);
  min-height: 400px;
}
.card {
  background: var(--fondo-bloque);
  border-radius: var(--border-radius);
}
@media (max-width: 768px) {
  .navbar-toggle {
    display: block;
  }
  .navbar-menu {
    display: none;
    position: absolute;
    top: 70px;
    left: 0;
    right: 0;
    background: var(--fondo-bloque);
    flex-direction: column;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  .navbar-menu.open {
    display: flex;
  }
  .admin-container {
    padding: 1rem;
  }
  .admin-titulo {
    font-size: 1.5rem;
  }
  .admin-stats {
    grid-template-columns: 1fr;
  }
  .admin-tabs {
    overflow-x: auto;
  }
}
</style>
