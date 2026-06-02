import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import LoginView from "../views/LoginView.vue";
import HomeView from "../views/HomeView.vue";
import RecetaDetailView from "../views/RecetaDetailView.vue";
import CategoriaView from "../views/CategoriaView.vue";
import TopRecetasView from "../views/TopRecetasView.vue";
import UserProfileView from "../views/UserProfileView.vue";
import EditMiPerfilView from "../views/EditMiPerfilView.vue";
import VerPerfilView from "../views/VerPerfilView.vue";
import CrearRecetaCategoriaView from "../views/CrearRecetaCategoriaView.vue";
import AdminPanelView from "../views/AdminPanelView.vue";

// Puedes añadir aquí más vistas cuando las crees
// import CrearRecetaView from "../views/CrearRecetaView.vue";
// import AdminView from "../views/AdminView.vue";

const routes = [
  // Ruta de login (solo para invitados)
  { path: "/auth", component: LoginView, meta: { guest: true } },

  // Rutas públicas
  { path: "/", component: HomeView, meta: { requiresAuth: false } },
  {
    path: "/receta/:id",
    component: RecetaDetailView,
    meta: { requiresAuth: false },
  },

  // Rutas privadas para cualquier usuario logueado (Registrado o Admin)
  {
    path: "/categoria/:id",
    name: "categoria",
    component: CategoriaView,
    meta: {
      requiresAuth: true,
      allowedRoles: ["registrado", "admin"],
    },
  },
  {
    path: "/top-recetas",
    name: "top-recetas",
    component: TopRecetasView,
    meta: { requiresAuth: false },
  },
  {
    path: "/perfil/:username",
    name: "user-profile",
    component: UserProfileView,
    meta: { requiresAuth: false },
  },
  {
    path: "/editar-mi-perfil",
    name: "editar-mi-perfil",
    component: EditMiPerfilView,
    meta: { requiresAuth: true },
  },
  {
    path: "/mi-perfil",
    name: "mi-perfil",
    component: VerPerfilView,
    meta: { requiresAuth: true },
  },
  {
    path: "/crear",
    name: "crear-receta-categoria",
    component: CrearRecetaCategoriaView,
    meta: { requiresAuth: true, allowedRoles: ["registrado", "admin"] },
  },
  {
    path: "/admin",
    name: "admin-panel",
    component: AdminPanelView,
    meta: { requiresAuth: true, allowedRoles: ["admin"] },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guard global para controlar acceso por roles
router.beforeEach(async (to) => {
  const auth = useAuthStore();

  console.log("[Router Guard] Antes de fetchMe, auth.usuario:", auth.usuario);

  // Si no sabemos si hay sesión, vamos al backend
  if (auth.usuario === null) {
    console.log("[Router Guard] auth.usuario es null, llamando a fetchMe()");
    await auth.fetchMe();
    console.log(
      "[Router Guard] Después de fetchMe, auth.usuario:",
      auth.usuario,
    );
  }

  const user = auth.usuario;
  const role = user?.rol;

  console.log("[Router Guard] usuario:", user);
  console.log("[Router Guard] rol:", role);
  console.log("[Router Guard] meta:", to.meta);

  // Si la ruta requiere auth y no hay usuario, ir a login
  if (to.meta.requiresAuth && !user) {
    console.log("[Router Guard] Requiere auth, pero no hay usuario → /auth");
    return { path: "/auth" };
  }

  // Página de login/registro solo para invitados
  if (to.meta.guest && user) {
    console.log("[Router Guard] guest y hay usuario → /");
    return { path: "/" };
  }

  // Admin puede acceder a todo
  if (user && role === "admin") {
    console.log("[Router Guard] Es Admin → permitir");
    return true;
  }

  // Si la ruta tiene allowedRoles, validar que el rol del usuario esté en la lista
  if (to.meta.allowedRoles && user) {
    const allowed = to.meta.allowedRoles.includes(role);
    console.log("[Router Guard] allowedRoles:", to.meta.allowedRoles);
    console.log("[Router Guard] ¿permite este rol?", allowed);
    if (!allowed) {
      console.log("[Router Guard] Rol no permitido → /no-autorizado");
      return { path: "/no-autorizado" };
    }
  }

  console.log("[Router Guard] Permitir navegación");
  return true;
});
export default router;
