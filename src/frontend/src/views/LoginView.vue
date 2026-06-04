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
const showSuccessModal = ref(false);
const generatedUsername = ref("");

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
    const response = await auth.register({
      nombre: registerForm.value.nombre,
      apellidos: registerForm.value.apellidos,
      email: registerForm.value.email,
      password: registerForm.value.password,
    });

    // Obtener el nombre de usuario de la respuesta del backend
    generatedUsername.value =
      response.data?.nombre_usuario || response.nombre_usuario;

    // Mostrar modal y cambiar a login
    showSuccessModal.value = true;
    mode.value = "login";

    // Pre-fill el nombre de usuario en el login
    loginForm.value.nombre_usuario = generatedUsername.value;
  } catch (e) {
    const data = e.response?.data;

    error.value = data
      ? Object.values(data).flat().join(" ")
      : "Error al registrarse.";
  } finally {
    loading.value = false;
  }
}

function closeModal() {
  showSuccessModal.value = false;
}
</script>

<template>
  <div
    class="auth-page container-fluid d-flex justify-content-center align-items-center min-vh-100"
  >
    <!-- Botón volver -->
    <router-link to="/" class="btn-back">
      <i class="bi bi-arrow-left"></i>
      <span>Seguir viendo recetas</span>
    </router-link>

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
          <Transition name="fade-slide" mode="out-in">
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

    <!-- MODAL DE ÉXITO -->
    <Transition name="fade-modal">
      <div v-if="showSuccessModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <i class="bi bi-check-circle-fill modal-icon"></i>
            <h3>¡Registro exitoso!</h3>
          </div>
          <div class="modal-body">
            <p>
              Has sido registrado correctamente. Tu nombre de usuario se creó a
              partir de las iniciales de los nombres y apellidos indicados:
            </p>
            <div class="username-display">
              <strong>nombre de usuario:</strong> {{ generatedUsername }}
            </div>
            <p class="modal-hint">
              Puedes editar dicho nombre de usuario una vez logueado en el
              apartado de la web
              <strong>"Editar Perfil"</strong>.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-modal" @click="closeModal">Entendido</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.auth-page {
  background: linear-gradient(135deg, var(--fondo-crema), #f6f1d7);
}

/* BOTÓN VOLVER */
.btn-back {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 1rem;
  background: var(--fondo-crema);
  border: 2px solid var(--color-olea);
  color: var(--color-olea);
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.8rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.btn-back:hover {
  background: var(--color-olea);
  color: white;
  transform: translateX(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.btn-back i {
  font-size: 1.1rem;
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
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
}

/* TRANSICION */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem 1.5rem 1rem;
  background: linear-gradient(135deg, #606c38 0%, #5a6b35 100%);
  border-radius: 20px 20px 0 0;
  color: white;
}

.modal-header h3 {
  font-family: var(--fuente-titulos);
  font-size: 1.4rem;
  color: white;
  margin: 0;
  font-weight: 700;
}

.modal-icon {
  font-size: 2rem;
  color: #4ade80;
}

.modal-body {
  padding: 1.5rem;
  color: var(--color-texto);
  line-height: 1.6;
}

.modal-body p {
  margin: 0 0 1rem;
  font-size: 0.95rem;
}

.username-display {
  background: var(--fondo-bloque);
  border: 2px solid var(--color-olea);
  border-radius: 12px;
  padding: 1rem;
  margin: 1rem 0;
  text-align: center;
}

.username-display strong {
  display: block;
  font-size: 0.85rem;
  color: var(--color-texto);
  margin-bottom: 0.5rem;
}

.username-display:not(:last-child) {
  margin-bottom: 1rem;
}

.username-display span,
.username-display:where(:not(:has(> span))) {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-olea);
  letter-spacing: 1px;
}

.modal-hint {
  font-size: 0.9rem;
  color: #666;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.modal-hint strong {
  color: var(--color-olea);
}

.modal-footer {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  justify-content: center;
}

.btn-modal {
  background: var(--color-olea);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-modal:hover {
  background: var(--color-acento);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* TRANSICIÓN MODAL */
.fade-modal-enter-active,
.fade-modal-leave-active {
  transition: all 0.3s ease;
}

.fade-modal-enter-from {
  opacity: 0;
}

.fade-modal-enter-from .modal-content {
  transform: scale(0.9) translateY(-20px);
}

.fade-modal-leave-to {
  opacity: 0;
}

.fade-modal-leave-to .modal-content {
  transform: scale(0.9) translateY(-20px);
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

.auth-title {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 2rem;
  margin-bottom: 1.3rem;
}

/* MOBILE */
@media (max-width: 991px) {
  .auth-page {
    padding: 0.75rem;
  }

  .auth-card {
    max-width: 100%;
    min-height: auto;
    height: auto;
  }

  .auth-content {
    max-width: 100%;
    padding: 1.5rem 1.25rem;
  }

  .auth-switch {
    margin-bottom: 1.5rem;
  }

  .auth-title {
    font-size: 1.6rem;
    margin-bottom: 1rem;
  }

  .btn-back {
    padding: 0.5rem 0.875rem;
    font-size: 0.85rem;
  }

  .btn-back i {
    font-size: 1rem;
  }

  .btn-back-text {
    display: none;
  }

  .switch-btn {
    padding: 0.5rem 0.25rem;
    font-size: 0.85rem;
  }

  .form-control {
    padding: 0.65rem 0.9rem;
    font-size: 0.95rem;
  }

  .btn-auth {
    padding: 0.8rem;
    font-size: 0.95rem;
  }
}

@media (max-width: 576px) {
  .btn-back {
    padding: 0.45rem 0.75rem;
    font-size: 0.8rem;
  }

  .auth-card {
    flex-direction: column;
    height: auto;
    margin-top: 4rem;
  }

  .auth-content {
    padding: 1.25rem 1rem;
  }

  .auth-title {
    font-size: 1.4rem;
  }

  .switch-btn {
    font-size: 0.8rem;
  }

  .modal-content {
    max-width: 340px;
  }

  .modal-header {
    padding: 1.25rem 1.25rem 0.75rem;
  }

  .modal-body {
    padding: 1.25rem;
    font-size: 0.9rem;
  }

  .username-display span,
  .username-display:where(:not(:has(> span))) {
    font-size: 1.25rem;
  }

  .modal-footer {
    padding: 0.75rem 1.25rem 1.25rem;
  }
}
</style>
