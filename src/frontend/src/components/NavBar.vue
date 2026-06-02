<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-olea shadow-sm">
    <div class="container-fluid">
      <!-- Logo -->
      <router-link to="/" class="navbar-brand fs-4 fw-bold text-white">
        Olea <span class="text-acento">Recetas</span>
      </router-link>

      <!-- Botón hamburguesa -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Menú principal -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto gap-3">
          <li class="nav-item">
            <router-link to="/" class="nav-link text-uppercase fw-medium">
              Recetas
            </router-link>
          </li>
          <li class="nav-item">
            <router-link
              to="/top-recetas"
              class="nav-link text-uppercase fw-medium"
            >
              Top recetas
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/crear" class="nav-link text-uppercase fw-medium">
              Añadir receta/categoría
            </router-link>
          </li>
        </ul>

        <!-- Usuario logueado -->
        <div v-if="auth.isLoggedIn && auth.usuario.nombre_usuario">
          <div class="dropdown">
            <a
              class="nav-link dropdown-toggle d-flex align-items-center"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <span class="fw-medium">
                {{ auth.usuario.nombre_usuario || "Usuario" }}
              </span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <router-link to="/editar-mi-perfil" class="dropdown-item">
                  Editar Perfil
                </router-link>
              </li>
              <li>
                <router-link to="/mi-perfil" class="dropdown-item">
                  Ver mi Perfil
                </router-link>
              </li>
              <li v-if="auth.usuario.rol === 'admin'">
                <router-link to="/admin" class="dropdown-item text-danger">
                  Panel de administración
                </router-link>
              </li>
              <li>
                <hr class="dropdown-divider" />
              </li>
              <li>
                <a class="dropdown-item" @click="logout"> Cerrar sesión </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Botones Entrar / Rexistrarse -->
        <div v-else class="d-flex gap-2">
          <router-link to="/auth" class="btn btn-sm btn-olea text-white">
            Entrar
          </router-link>
          <router-link
            to="/auth"
            class="btn btn-sm btn-outline-olea text-white"
          >
            Rexistrarse
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

async function logout() {
  await auth.logout();
  router.push("/auth");
}
</script>

<style scoped>
.navbar {
  background-color: var(--color-olea) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
  font-family: var(--fuente-cuerpo);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 999;
}

.navbar-brand {
  color: white;
  font-family: var(--fuente-titulos);
}

.nav-link {
  color: white;
  font-size: 0.9rem;
}

.nav-link:hover,
.nav-link.active {
  color: var(--fondo-crema);
}

.dropdown-item {
  color: var(--color-texto);
  font-family: var(--fuente-cuerpo);
}

.dropdown-item:hover,
.dropdown-item.active {
  background-color: var(--color-acento);
  color: white;
}

.navbar-toggler {
  border-color: white;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='white' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

.btn-olea {
  background-color: var(--color-olea);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.btn-olea:hover {
  background-color: var(--color-acento);
  color: white;
}

.btn-outline-olea {
  border: 1px solid var(--fondo-crema);
  color: var(--fondo-crema);
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.btn-outline-olea:hover {
  background-color: var(--fondo-crema);
  color: var(--color-olea);
}
</style>
