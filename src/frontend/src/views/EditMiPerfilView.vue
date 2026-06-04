<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import Navbar from "../components/NavBar.vue";
import Footer from "../components/Footer.vue";

const auth = useAuthStore();

const loading = ref(true);
const guardando = ref(false);
const cambiandoContrasena = ref(false);
const fotoPreview = ref(null);
const fotoNombre = ref("");
const usernameSugerido = ref("");

const formData = ref({
  nombre: "",
  apellido1: "",
  apellido2: "",
  nombre_usuario: "",
  email: "",
  foto_perfil: "",
  biografia_y_enlaces: "",
});

const contrasena = ref({
  password_actual: "",
  password_nueva: "",
  password_confirmar: "",
});

// Función para obtener la URL completa de la imagen
const getFullImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path; // Ya es una URL completa

  // Detectar si estamos en producción o desarrollo
  const isProduction = window.location.hostname !== "localhost";
  const backendHost = isProduction
    ? "https://backolea.up.railway.app" // Tu backend en producción
    : "http://localhost:8000";

  return backendHost + path;
};

const fotoActual = computed(() => {
  if (fotoPreview.value) return fotoPreview.value;
  return getFullImageUrl(formData.value.foto_perfil);
});

const cargarDatos = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/auth/edit-mi-perfil/");
    formData.value = {
      nombre: data.nombre || "",
      apellido1: data.apellido1 || "",
      apellido2: data.apellido2 || "",
      nombre_usuario: data.nombre_usuario || "",
      email: data.email || "",
      foto_perfil: data.foto_perfil || "",
      biografia_y_enlaces: data.biografia_y_enlaces || "",
    };
  } catch (error) {
    console.error("Error al cargar perfil:", error);
    alert("No se pudo cargar el perfil");
  } finally {
    loading.value = false;
  }
};

const generarUsernameSugerido = () => {
  const nombre = formData.value.nombre?.toLowerCase().trim() || "";
  const apellido1 = formData.value.apellido1?.toLowerCase().trim() || "";
  const apellido2 = formData.value.apellido2?.toLowerCase().trim() || "";

  if (nombre && apellido1) {
    let sugerencia = `${nombre}.${apellido1}`;
    if (apellido2) sugerencia += `.${apellido2}`;
    usernameSugerido.value = sugerencia.replace(/[^a-z0-9.]/g, "");
  } else {
    usernameSugerido.value = "";
  }
};

const handleFotoChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    fotoPreview.value = URL.createObjectURL(file);
    fotoNombre.value = file.name;
  }
};

const guardarPerfil = async () => {
  guardando.value = true;

  try {
    const dataEnviar = new FormData();
    dataEnviar.append("nombre", formData.value.nombre);
    dataEnviar.append("apellido1", formData.value.apellido1);
    dataEnviar.append("apellido2", formData.value.apellido2);
    dataEnviar.append("nombre_usuario", formData.value.nombre_usuario);
    dataEnviar.append("email", formData.value.email);
    dataEnviar.append(
      "biografia_y_enlaces",
      formData.value.biografia_y_enlaces || "",
    );

    const inputFoto = document.getElementById("foto-perfil");
    if (inputFoto && inputFoto.files[0]) {
      dataEnviar.append("foto_perfil", inputFoto.files[0]);
    }

    const response = await api.put("/auth/edit-mi-perfil/", dataEnviar);

    if (response.status >= 200 && response.status < 300) {
      await auth.fetchMe();
      alert("Perfil actualizado correctamente");
      fotoPreview.value = null;
      fotoNombre.value = "";
      if (inputFoto) inputFoto.value = "";
      usernameSugerido.value = "";
      await cargarDatos();
    }
  } catch (error) {
    console.error("Error al guardar perfil:", error);
    alert(error.response?.data?.detail || "Error al guardar el perfil");
  } finally {
    guardando.value = false;
  }
};

const cambiarContrasena = async () => {
  if (contrasena.value.password_nueva !== contrasena.value.password_confirmar) {
    alert("Las nuevas contraseñas no coinciden");
    return;
  }

  if (contrasena.value.password_nueva.length < 8) {
    alert("La nueva contraseña debe tener al menos 8 caracteres");
    return;
  }

  cambiandoContrasena.value = true;
  try {
    await api.put("/auth/cambiar-contrasena/", contrasena.value);
    alert("Contraseña cambiada correctamente");
    contrasena.value = {
      password_actual: "",
      password_nueva: "",
      password_confirmar: "",
    };
  } catch (error) {
    console.error("Error al cambiar contraseña:", error);
    alert(error.response?.data?.detail || "Error al cambiar la contraseña");
  } finally {
    cambiandoContrasena.value = false;
  }
};

onMounted(() => {
  cargarDatos();
});
</script>

<template>
  <div class="mi-perfil-page">
    <Navbar />

    <div class="container py-5">
      <h1 class="mi-perfil-titulo">Editar mi perfil</h1>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-olea" role="status">
          <span class="visually-hidden">Cargando perfil...</span>
        </div>
      </div>

      <div v-else class="mi-perfil-container">
        <div class="row">
          <div class="col-lg-4 mb-4">
            <div class="card mi-perfil-card">
              <div class="card-body text-center">
                <div class="mi-perfil-avatar-wrapper">
                  <img
                    v-if="fotoActual"
                    :src="fotoActual"
                    alt="Foto de perfil"
                    class="mi-perfil-avatar"
                  />
                  <div v-else class="mi-perfil-avatar-placeholder">
                    {{
                      formData.nombre_usuario?.charAt(0)?.toUpperCase() || "U"
                    }}
                  </div>
                </div>

                <div class="mt-3">
                  <label for="foto-perfil" class="btn btn-outline-olea btn-sm">
                    <i class="bi bi-camera"></i>
                    {{ fotoPreview ? "Cambiar foto" : "Subir foto" }}
                  </label>
                  <input
                    id="foto-perfil"
                    type="file"
                    accept="image/*"
                    @change="handleFotoChange"
                    class="d-none"
                  />
                </div>

                <p v-if="fotoNombre" class="text-muted small mt-2">
                  Archivo: {{ fotoNombre }}
                </p>
              </div>
            </div>
          </div>

          <!-- Resto del template igual... -->
          <div class="col-lg-8">
            <div class="card mi-perfil-card">
              <div class="card-header">
                <h3 class="mb-0">Información personal</h3>
              </div>
              <div class="card-body">
                <form @submit.prevent="guardarPerfil">
                  <div class="row">
                    <div class="col-md-4 mb-3">
                      <label class="form-label">Nombre *</label>
                      <input
                        v-model="formData.nombre"
                        type="text"
                        class="form-control"
                        required
                        @input="generarUsernameSugerido"
                      />
                    </div>
                    <div class="col-md-4 mb-3">
                      <label class="form-label">Apellido 1 *</label>
                      <input
                        v-model="formData.apellido1"
                        type="text"
                        class="form-control"
                        required
                        @input="generarUsernameSugerido"
                      />
                    </div>
                    <div class="col-md-4 mb-3">
                      <label class="form-label">Apellido 2</label>
                      <input
                        v-model="formData.apellido2"
                        type="text"
                        class="form-control"
                        @input="generarUsernameSugerido"
                      />
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Nombre de usuario *</label>
                    <input
                      v-model="formData.nombre_usuario"
                      type="text"
                      class="form-control"
                      required
                    />
                    <small class="text-muted">
                      {{
                        usernameSugerido
                          ? `Sugerencia: ${usernameSugerido}`
                          : ""
                      }}
                    </small>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Email *</label>
                    <input
                      v-model="formData.email"
                      type="email"
                      class="form-control"
                      required
                    />
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Biografía y enlaces</label>
                    <textarea
                      v-model="formData.biografia_y_enlaces"
                      class="form-control"
                      rows="3"
                      placeholder="Cuéntate algo más o añade enlaces a tus redes sociales..."
                    ></textarea>
                  </div>

                  <div class="d-flex gap-2">
                    <button
                      type="submit"
                      class="btn btn-olea"
                      :disabled="guardando"
                    >
                      <i class="bi bi-check-circle"></i>
                      {{ guardando ? "Guardando..." : "Guardar cambios" }}
                    </button>
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="cargarDatos"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <div class="card mi-perfil-card mt-4">
              <div class="card-header">
                <h3 class="mb-0">Cambiar contraseña</h3>
              </div>
              <div class="card-body">
                <form @submit.prevent="cambiarContrasena">
                  <div class="mb-3">
                    <label class="form-label">Contraseña actual *</label>
                    <input
                      v-model="contrasena.password_actual"
                      type="password"
                      class="form-control"
                      required
                    />
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Nueva contraseña *</label>
                    <input
                      v-model="contrasena.password_nueva"
                      type="password"
                      class="form-control"
                      required
                      minlength="8"
                    />
                    <small class="text-muted">Mínimo 8 caracteres</small>
                  </div>
                  <div class="mb-3">
                    <label class="form-label"
                      >Confirmar nueva contraseña *</label
                    >
                    <input
                      v-model="contrasena.password_confirmar"
                      type="password"
                      class="form-control"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    class="btn btn-outline-danger"
                    :disabled="cambiandoContrasena"
                  >
                    <i class="bi bi-key"></i>
                    {{
                      cambiandoContrasena
                        ? "Cambiando..."
                        : "Cambiar contraseña"
                    }}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <Footer />
</template>

<style scoped>
.mi-perfil-page {
  background-color: var(--fondo-crema);
  min-height: 100vh;
  padding-top: 80px;
}

.mi-perfil-titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  margin-bottom: 2rem;
}

.mi-perfil-container {
  max-width: 1000px;
  margin: 0 auto;
}

.mi-perfil-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mi-perfil-card-header {
  background-color: white;
  border-bottom: 1px solid #eee;
}

.mi-perfil-card-header h3 {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 1.25rem;
}

.mi-perfil-avatar-wrapper {
  width: 150px;
  height: 150px;
  margin: 0 auto;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 2px solid var(--color-olea);
}

.mi-perfil-avatar {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: white;
}

.mi-perfil-avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-olea), #8b7355);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.5rem;
  font-weight: 700;
}

.btn-olea {
  background-color: var(--color-olea);
  color: white;
  border: none;
}

.btn-olea:hover {
  background-color: var(--color-acento);
  color: white;
}

.btn-outline-olea {
  border-color: var(--color-olea);
  color: var(--color-olea);
}

.btn-outline-olea:hover {
  background-color: var(--color-olea);
  color: white;
}
</style>
