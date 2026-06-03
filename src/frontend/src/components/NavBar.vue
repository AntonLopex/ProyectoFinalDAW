<template>
  <nav class="navbar navbar-expand-lg olea-navbar fixed-top">
    <div class="container">
      <!-- Logo -->
      <router-link to="/" class="navbar-brand">
        <span class="logo-icon">🍃</span>
        Olea
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
      <!-- Menú -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mx-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link" active-class="active">
              <i class="bi bi-book"></i>
              Recetas
            </router-link>
          </li>
          <li class="nav-item">
            <router-link
              to="/top-recetas"
              class="nav-link"
              active-class="active"
            >
              <i class="bi bi-trophy"></i>
              Top recetas
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/crear" class="nav-link" active-class="active">
              <i class="bi bi-plus-circle"></i>
              Añadir receta
            </router-link>
          </li>
        </ul>
        <!-- Usuario -->
        <div
          v-if="auth.isLoggedIn && auth.usuario.nombre_usuario"
          class="navbar-user"
        >
          <div class="dropdown">
            <button
              class="btn user-toggle dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <div class="user-avatar">
                <img
                  v-if="auth.usuario.foto_perfil"
                  :src="getFullImageUrl(auth.usuario.foto_perfil)"
                  alt="Avatar"
                />
                <div v-else class="avatar-placeholder">
                  {{
                    auth.usuario.nombre_usuario?.charAt(0)?.toUpperCase() || "U"
                  }}
                </div>
              </div>
              <span class="user-name">{{ auth.usuario.nombre_usuario }}</span>
            </button>

            <ul class="dropdown-menu" :class="{ show: isDropdownOpen }">
              <li class="dropdown-header">
                <div class="dropdown-avatar">
                  <img
                    v-if="auth.usuario.foto_perfil"
                    :src="getFullImageUrl(auth.usuario.foto_perfil)"
                    alt="Avatar"
                  />
                  <div v-else class="avatar-placeholder">
                    {{
                      auth.usuario.nombre_usuario?.charAt(0)?.toUpperCase() ||
                      "U"
                    }}
                  </div>
                </div>
                <div class="dropdown-info">
                  <strong>{{ auth.usuario.nombre_usuario }}</strong>
                  <small
                    >{{ auth.usuario.nombre }}
                    {{ auth.usuario.apellido1 }}</small
                  >
                </div>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <router-link
                  to="/editar-mi-perfil"
                  class="dropdown-item"
                  @click="closeMobileMenu"
                >
                  <i class="bi bi-pencil-square"></i>
                  <span>Editar Perfil</span>
                </router-link>
              </li>
              <li>
                <router-link
                  to="/mi-perfil"
                  class="dropdown-item"
                  @click="closeMobileMenu"
                >
                  <i class="bi bi-person"></i>
                  <span>Ver mi Perfil</span>
                </router-link>
              </li>
              <li v-if="auth.usuario.rol === 'admin'">
                <router-link
                  to="/admin"
                  class="dropdown-item admin-link"
                  @click="closeMobileMenu"
                >
                  <i class="bi bi-shield-lock"></i>
                  <span>Panel de administración</span>
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <a class="dropdown-item logout" @click="logout">
                  <i class="bi bi-box-arrow-right"></i>
                  <span>Cerrar sesión</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Botones Auth -->
        <div v-else class="navbar-auth">
          <router-link to="/auth" class="btn btn-outline-light btn-sm"
            >Entrar</router-link
          >
          <router-link to="/auth" class="btn btn-primary btn-sm"
            >Rexistrarse</router-link
          >
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import { onMounted } from "vue";

const auth = useAuthStore();
const router = useRouter();

async function logout() {
  await auth.logout();
  router.push("/auth");
}

const getFullImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const baseUrl = "http://localhost:8000";
  return baseUrl + path;
};

function closeMobileMenu() {
  const navbarCollapse = document.querySelector(".navbar-collapse");
  if (navbarCollapse && navbarCollapse.classList.contains("show")) {
    new bootstrap.Collapse(navbarCollapse);
  }
}

// Animación del dropdown después de que Bootstrap lo muestre
onMounted(() => {
  const dropdownElement = document.querySelector(".user-toggle");
  if (dropdownElement) {
    dropdownElement.addEventListener("shown.bs.dropdown", (event) => {
      const dropdownMenu = event.target.querySelector(".dropdown-menu");
      if (dropdownMenu) {
        dropdownMenu.classList.add("show");
      }
    });

    dropdownElement.addEventListener("hidden.bs.dropdown", (event) => {
      const dropdownMenu = event.target.querySelector(".dropdown-menu");
      if (dropdownMenu) {
        setTimeout(() => {
          dropdownMenu.classList.remove("show");
        }, 250);
      }
    });
  }
});
</script>

<style scoped>
.olea-navbar {
  background: linear-gradient(
    135deg,
    var(--color-olea) 0%,
    #5a6b35 100%
  ) !important;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  color: white !important;
  font-family: var(--fuente-titulos);
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 1.75rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  font-size: 0.95rem;
  font-weight: 500;
  padding: 0.5rem 1rem !important;
  margin: 0 0.25rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link i {
  font-size: 1.1rem;
}

.nav-link:hover {
  color: white !important;
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  color: white !important;
  background: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.navbar-toggler {
  border-color: rgba(255, 255, 255, 0.5);
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(255, 255, 255, 1)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

/* Usuario */
.navbar-user {
  display: flex;
  align-items: center;
}

.user-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1) !important;
  border: 2px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  padding: 0.5rem 1rem !important;
  border-radius: 50px !important;
  font-weight: 600;
  position: relative;
}

.user-toggle:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
}

.user-toggle::after {
  transition: transform 0.3s ease;
  border-top: 0.3em solid;
  border-right: 0.3em solid transparent;
  border-bottom: 0;
  border-left: 0.3em solid transparent;
  margin-left: 0.25rem;
}

.user-toggle[aria-expanded="true"]::after {
  transform: rotate(180deg);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  background: rgb(255, 255, 255);
  object-fit: contain;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-olea), #8b7355);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
}

.user-name {
  display: none;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  min-width: 260px;
  width: fit-content;
  max-width: 300px;
  border: none;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  background: white;
  list-style: none;
  padding: 0.75rem 0.5rem;
  margin: 0;
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
  transform-origin: top right;
  transition:
    opacity 0.25s ease-out,
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  overflow: hidden;
}

.dropdown-menu.show {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  margin: -0.75rem -0.5rem 0.75rem -0.5rem;
  background: linear-gradient(135deg, #606c38 0%, #5a6b35 100%);
  border-radius: 16px 16px 0 0;
}

.dropdown-avatar {
  width: 52px;
  height: 52px;
  min-width: 52px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgb(255, 255, 255);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dropdown-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-olea), #8b7355);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.25rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.dropdown-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow: hidden;
}

.dropdown-info strong {
  display: block;
  font-size: 0.95rem;
  font-weight: 700;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.dropdown-info small {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
  font-weight: 400;
}

.dropdown-divider {
  border: 0;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  margin: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.75rem 1rem;
  margin: 0.125rem 0;
  border-radius: 10px;
  font-size: 0.925rem;
  font-weight: 500;
  color: #333;
  text-decoration: none;
  transition: all 0.2s ease;
}

.dropdown-item i {
  width: 22px;
  height: 22px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-olea);
  flex-shrink: 0;
}

.dropdown-item span {
  flex: 1;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: rgba(90, 107, 53, 0.08);
  color: var(--color-olea);
  transform: translateX(3px);
}

.dropdown-item:hover i {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}

.admin-link {
  color: #dc3545 !important;
}

.admin-link i {
  color: #dc3545 !important;
}

.admin-link:hover {
  background: rgba(220, 53, 69, 0.08) !important;
  color: #dc3545 !important;
}

.logout {
  color: #dc3545 !important;
}

.logout i {
  color: #dc3545 !important;
}

.logout:hover {
  background: rgba(220, 53, 69, 0.08) !important;
  color: #dc3545 !important;
}

/* Responsive - Móvil */
@media (max-width: 991px) {
  .dropdown-menu {
    right: 50%;
    transform: translateX(30%) translateY(-8px) scale(0.97);
    min-width: 260px;
    max-width: calc(100vw - 32px);
  }

  .dropdown-menu.show {
    transform: translateX(30%) translateY(0) scale(1);
  }

  .dropdown-header {
    padding: 0.875rem 1rem;
    margin: -0.75rem -0.5rem 0.625rem -0.5rem;
  }

  .dropdown-avatar {
    width: 46px;
    height: 46px;
    min-width: 46px;
  }

  .dropdown-info strong {
    font-size: 0.9rem;
  }

  .dropdown-info small {
    font-size: 0.75rem;
  }

  .dropdown-item {
    padding: 0.7rem 0.875rem;
    font-size: 0.9rem;
  }
}

@media (min-width: 992px) {
  .dropdown-menu {
    transform-origin: top right;
  }
}

/* Botones */
.navbar-auth {
  display: flex;
  gap: 0.5rem;
}

.btn-primary {
  background: white;
  color: var(--color-olea);
  border-color: white;
}

.btn-primary:hover {
  background: var(--fondo-crema);
  color: var(--color-olea);
}

@media (max-width: 991px) {
  .navbar-auth {
    flex-direction: column;
    width: 100%;
    margin-top: 1rem;
  }

  .btn {
    width: 100%;
  }
}
</style>
