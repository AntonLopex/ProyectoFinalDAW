<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const mode = ref("login");

const loginForm = ref({
  nombre_usuario: "",
  password: "",
});

const registerForm = ref({
  nombre: "",
  apellidos: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const error = ref("");
const loading = ref(false);

const passwordsMatch = computed(() => {
  return (
    registerForm.value.password &&
    registerForm.value.confirmPassword &&
    registerForm.value.password === registerForm.value.confirmPassword
  );
});

const passwordsDontMatch = computed(() => {
  return (
    registerForm.value.confirmPassword &&
    registerForm.value.password !== registerForm.value.confirmPassword
  );
});

async function handleLogin() {
  error.value = "";
  loading.value = true;

  try {
    await auth.login(loginForm.value);

    router.push("/");
  } catch (e) {
    error.value = e.response?.data?.error || "Error al iniciar sesión.";
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  error.value = "";

  if (!passwordsMatch.value) {
    error.value = "Las contraseñas no coinciden.";
    return;
  }

  loading.value = true;

  try {
    await auth.register({
      nombre: registerForm.value.nombre,
      apellidos: registerForm.value.apellidos,
      email: registerForm.value.email,
      password: registerForm.value.password,
    });

    mode.value = "login";
  } catch (e) {
    const data = e.response?.data;

    error.value = data
      ? Object.values(data).flat().join(" ")
      : "Error al registrarse.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div
    class="auth-page container-fluid d-flex justify-content-center align-items-center min-vh-100"
  >
    <div class="auth-card">
      <!-- IMAGEN -->
      <div class="auth-image d-none d-lg-block">
        <div class="overlay">
          <h1>OLEA</h1>

          <p>
            Comparte recetas, descubre sabores y conecta con amantes de la
            cocina.
          </p>
        </div>
      </div>

      <!-- FORMULARIO -->
      <div class="auth-content">
        <!-- SWITCH -->
        <div class="auth-switch">
          <!-- SLIDER -->
          <div
            class="switch-slider"
            :class="{
              'move-right': mode === 'register',
            }"
          ></div>

          <button
            class="switch-btn"
            :class="{ active: mode === 'login' }"
            @click="mode = 'login'"
          >
            Inicio de sesión
          </button>

          <button
            class="switch-btn"
            :class="{ active: mode === 'register' }"
            @click="mode = 'register'"
          >
            Registro
          </button>
        </div>

        <!-- ERROR -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        <div class="auth-form-wrapper">
          <Transition
    name="fade-slide"
    mode="out-in"
  >
          <!-- LOGIN -->
          <div v-if="mode === 'login'" key="login">
            <h2 class="auth-title">Bienvenido de nuevo</h2>

            <div class="mb-3">
              <label class="form-label"> Nombre de usuario </label>

              <input
                v-model="loginForm.nombre_usuario"
                type="text"
                class="form-control"
              />
            </div>

            <div class="mb-4">
              <label class="form-label"> Contraseña </label>

              <input
                v-model="loginForm.password"
                type="password"
                class="form-control"
              />
            </div>

            <button
              class="btn btn-auth w-100"
              :disabled="loading"
              @click="handleLogin"
            >
              <span
                v-if="loading"
                class="spinner-border spinner-border-sm me-2"
              ></span>

              Iniciar sesión
            </button>
          </div>

          <!-- REGISTER -->
          <div v-else key="register">

            <div class="mb-2">
              <label class="form-label"> Nombre </label>

              <input
                v-model="registerForm.nombre"
                type="text"
                class="form-control"
              />
            </div>

            <div class="mb-2">
              <label class="form-label"> Apellidos </label>

              <input
                v-model="registerForm.apellidos"
                type="text"
                class="form-control"
              />
            </div>

            <div class="mb-2">
              <label class="form-label"> Email </label>

              <input
                v-model="registerForm.email"
                type="email"
                class="form-control"
              />
            </div>

            <div class="mb-2">
              <label class="form-label"> Contraseña </label>

              <input
                v-model="registerForm.password"
                type="password"
                class="form-control"
              />
            </div>

            <div class="mb-3">
              <label class="form-label"> Confirmar contraseña </label>

              <input
                v-model="registerForm.confirmPassword"
                type="password"
                class="form-control"
                :class="{
                  'is-valid': passwordsMatch,
                  'is-invalid': passwordsDontMatch,
                }"
              />

              <div v-if="passwordsDontMatch" class="invalid-feedback">
                Las contraseñas no coinciden.
              </div>

              <div v-if="passwordsMatch" class="valid-feedback">
                Las contraseñas coinciden.
              </div>
            </div>

            <button
              class="btn btn-auth w-100"
              :disabled="loading || passwordsDontMatch"
              @click="handleRegister"
            >
              <span
                v-if="loading"
                class="spinner-border spinner-border-sm me-2"
              ></span>

              Registrarse
            </button>
          </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  background: linear-gradient(135deg, var(--fondo-crema), #f6f1d7);
}

/* CARD */

.auth-card {
  width: 100%;
  max-width: 1050px;

  height: 720px;

  background: white;

  border-radius: 28px;

  overflow: hidden;

  display: flex;

  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.08);
}
/* TRANSICION */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition:
    all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
/* IMAGEN */

.auth-image {
  flex: 1;

  background:
    linear-gradient(rgba(40, 54, 24, 0.45), rgba(40, 54, 24, 0.45)),
    url("../assets/img/cocina_login.png");

  background-size: cover;
  background-position: center;

  position: relative;
}

.overlay {
  height: 100%;

  display: flex;
  flex-direction: column;

  justify-content: center;

  padding: 4rem;

  color: white;
}

.overlay h1 {
  font-family: var(--fuente-titulos);

  font-size: 4rem;

  color: white;

  margin-bottom: 1rem;
}

.overlay p {
  font-size: 1.1rem;

  max-width: 400px;

  line-height: 1.8;
}

/* CONTENT */
.auth-content {
  width: 100%;
  max-width: 480px;

  padding: 2rem 2.2rem;

  display: flex;
  flex-direction: column;

  height: 100%;
  overflow: hidden;
}

.auth-form-wrapper {
  flex: 1;

  display: flex;
  align-items: center;
}

.auth-form-wrapper > div {
  width: 100%;
}

/* SWITCH */

.auth-switch {
  position: relative;

  background: var(--fondo-bloque);

  border-radius: 14px;

  padding: 0.35rem;

  display: flex;

  margin-bottom: 2rem;

  overflow: hidden;
}

/* SLIDER */

.switch-slider {
  position: absolute;

  top: 5px;
  left: 5px;

  width: calc(50% - 5px);
  height: calc(100% - 10px);

  background-color: var(--color-olea);

  border-radius: 10px;

  transition: transform 0.35s ease;
}

.switch-slider.move-right {
  transform: translateX(100%);
}

/* BOTONES */

.switch-btn {
  position: relative;

  z-index: 2;

  flex: 1;

  border: none;

  background: transparent;

  padding: 0.65rem;

  border-radius: 10px;

  font-weight: 600;

  color: var(--color-texto);

  transition: color 0.3s ease;
}

.switch-btn.active {
  color: white;
}

/* TITULO */

.auth-title {
  font-family: var(--fuente-titulos);

  color: var(--color-olea);

  font-size: 2rem;

  margin-bottom: 1.3rem;
}

/* INPUTS */

.form-label {
  color: var(--color-texto);

  font-weight: 500;
}

.form-control {
  border-radius: 14px;

  padding: 0.72rem 1rem;

  border: 1px solid #ddd;

  background-color: var(--fondo-bloque);

  transition: var(--transition);
}

.form-control:focus {
  border-color: var(--color-acento);

  box-shadow: 0 0 0 0.2rem rgba(221, 161, 94, 0.25);
}

/* BOTON */

.btn-auth {
  background-color: var(--color-olea);

  border: none;

  border-radius: 14px;

  padding: 0.9rem;

  color: white;

  font-weight: 600;

  transition: var(--transition);
}

.btn-auth:hover {
  background-color: var(--color-acento);

  transform: translateY(-1px);
}

/* ALERT */

.alert {
  border-radius: 14px;

  border: none;
}

/* MOBILE */

@media (max-width: 991px) {
  .auth-card {
    max-width: 480px;

    min-height: auto;
  }

  .auth-content {
    max-width: 100%;
  }
}
</style>
