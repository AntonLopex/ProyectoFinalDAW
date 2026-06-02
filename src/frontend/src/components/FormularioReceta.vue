<!-- components/FormularioReceta.vue -->
<template>
  <form @submit.prevent="enviarFormulario" class="formulario-receta">
    <h2 class="formulario-titulo">Nueva Receta</h2>

    <!-- Título -->
    <div class="form-group">
      <label for="titulo">Título *</label>
      <input
        id="titulo"
        v-model="formData.titulo"
        type="text"
        class="form-control"
        placeholder="Ej: Paella Valenciana"
        required
      />
    </div>

    <!-- Tiempo de elaboración (HH:MM:SS) -->
    <div class="form-group">
      <label for="tiempo">Tiempo de elaboración *</label>
      <input
        id="tiempo"
        v-model="formData.tiempo_de_elaboracion"
        type="time"
        class="form-control"
        step="1"
        required
      />
      <small class="form-help">Formato: HH:MM:SS</small>
    </div>

    <!-- Dificultad -->
    <div class="form-group">
      <label for="dificultad">Dificultad *</label>
      <select
        id="dificultad"
        v-model="formData.dificultad"
        class="form-control"
        required
      >
        <option value="" disabled>Selecciona dificultad</option>
        <option value="facil">Fácil</option>
        <option value="media">Media</option>
        <option value="dificil">Difícil</option>
      </select>
    </div>

    <!-- Raciones -->
    <div class="form-group">
      <label for="raciones">Raciones *</label>
      <input
        id="raciones"
        v-model.number="formData.raciones"
        type="number"
        class="form-control"
        min="1"
        placeholder="Ej: 4"
        required
      />
    </div>

    <!-- Categoría (select con búsqueda) -->
    <div class="form-group">
      <label for="categoria">Categoría *</label>
      <div class="searchable-select">
        <input
          id="categoria"
          v-model="busquedaCategoria"
          type="text"
          class="form-control"
          placeholder="Buscar o escribir categoría..."
          @input="filtrarCategorias"
          @focus="mostrarOpciones = true"
          autocomplete="off"
        />
        <div v-if="mostrarOpciones" class="opciones-dropdown">
          <div
            v-for="cat in categoriasFiltradas"
            :key="cat.id"
            class="opcion-item"
            :class="{ 'opcion-activa': categoriaSeleccionada === cat.id }"
            @click="seleccionarCategoria(cat)"
          >
            {{ cat.nombre }}
          </div>
          <div v-if="categoriasFiltradas.length === 0" class="no-resultados">
            No se encontraron categorías
          </div>
        </div>
      </div>
      <input type="hidden" :value="categoriaSeleccionada" />
      <small v-if="!categoriaSeleccionada" class="form-help">
        Si no encuentra su categoría, por favor créela antes en la sección
        "Crear Categoría".
      </small>
    </div>

    <!-- Ingredientes -->
    <div class="form-group">
      <label>Ingredientes *</label>
      <div class="ingredientes-list">
        <div
          v-for="(ing, index) in formData.ingredientes"
          :key="index"
          class="ingrediente-item"
        >
          <input
            v-model="ing.cantidad"
            type="text"
            class="form-control form-control-sm"
            placeholder="Cantidad"
            required
          />
          <input
            v-model="ing.nombre"
            type="text"
            class="form-control form-control-sm"
            placeholder="Nombre ingrediente"
            required
          />
          <button
            type="button"
            class="btn-remove"
            @click="eliminarIngrediente(index)"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
      <button type="button" class="btn-add" @click="agregarIngrediente">
        <i class="bi bi-plus-lg"></i> Agregar ingrediente
      </button>
    </div>

    <!-- Elaboración -->
    <div class="form-group">
      <label>Elaboración *</label>
      <div class="elaboracion-list">
        <div
          v-for="(paso, index) in formData.elaboracion"
          :key="index"
          class="paso-item"
        >
          <span class="paso-number">{{ index + 1 }}</span>
          <textarea
            v-model="paso.paso"
            class="form-control"
            rows="2"
            placeholder="Describe este paso..."
            required
          ></textarea>
          <button type="button" class="btn-remove" @click="eliminarPaso(index)">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
      <button type="button" class="btn-add" @click="agregarPaso">
        <i class="bi bi-plus-lg"></i> Agregar paso
      </button>
    </div>

    <!-- Upload Drag & Drop Imagen -->
    <div class="form-group">
      <label>Imagen *</label>
      <div
        class="upload-dropzone"
        :class="{ 'drag-over': dragOver }"
        @dragover="sobrarArchivos"
        @dragleave="salirArchivos"
        @drop="soltarArchivos"
        @click="abrirInputFile"
      >
        <input
          ref="inputFileImagen"
          type="file"
          accept="image/*"
          class="upload-input"
          @change="seleccionarArchivo"
        />
        <div class="upload-content">
          <i v-if="!imagenPreview" class="bi bi-cloud-upload upload-icon"></i>
          <img v-else :src="imagenPreview" class="upload-preview" />
          <p class="upload-text">
            {{
              imagenNombre ||
              "Arrastra tu imagen aquí o haz clic para seleccionar"
            }}
          </p>
          <p class="upload-subtext">PNG, JPG, WEBP hasta 5MB</p>
        </div>
      </div>
      <small v-if="errorImagen" class="form-help error">{{
        errorImagen
      }}</small>
    </div>

    <!-- Botón enviar -->
    <button
      type="submit"
      class="btn btn-olea btn-submit"
      :disabled="enviando || !EsValidoFormulario"
    >
      <span v-if="!enviando">Crear Receta</span>
      <span v-else>
        <div class="spinner-border spinner-border-sm" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        Enviando...
      </span>
    </button>
  </form>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";

const router = useRouter();
const emit = defineEmits(["receta-creada"]);

const enviando = ref(false);
const categorias = ref([]);
const mostrarOpciones = ref(false);
const busquedaCategoria = ref("");
const categoriaSeleccionada = ref(null);
const categoriasFiltradas = ref([]);

const inputFileImagen = ref(null);
const dragOver = ref(false);
const archivoImagen = ref(null);
const imagenNombre = ref("");
const imagenPreview = ref(null);
const errorImagen = ref("");

const formData = ref({
  titulo: "",
  tiempo_de_elaboracion: "",
  dificultad: "",
  raciones: 1,
  ingredientes: [{ cantidad: "", nombre: "" }],
  elaboracion: [{ paso: "" }],
});

const EsValidoFormulario = computed(() => {
  return (
    categoriaSeleccionada.value !== null &&
    archivoImagen.value !== null &&
    formData.value.titulo &&
    formData.value.tiempo_de_elaboracion &&
    formData.value.dificultad
  );
});

const cargarCategorias = async () => {
  try {
    const { data } = await api.get("/recetas/categorias/");
    categorias.value = data;
    categoriasFiltradas.value = data;
  } catch (error) {
    console.error("Error al cargar categorías:", error);
  }
};

const filtrarCategorias = () => {
  const busqueda = busquedaCategoria.value.toLowerCase();
  categoriasFiltradas.value = categorias.value.filter((cat) =>
    cat.nombre.toLowerCase().includes(busqueda),
  );
};

const seleccionarCategoria = (cat) => {
  categoriaSeleccionada.value = cat.id;
  busquedaCategoria.value = cat.nombre;
  mostrarOpciones.value = false;
};

const clicarFuera = (event) => {
  if (!event.target.closest(".searchable-select")) {
    mostrarOpciones.value = false;
  }
};

const abrirInputFile = () => {
  inputFileImagen.value?.click();
};

const sobrarArchivos = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragOver.value = true;
};

const salirArchivos = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragOver.value = false;
};

const soltarArchivos = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragOver.value = false;

  const archivo = e.dataTransfer.files[0];
  validarYSepararArchivo(archivo);
};

const seleccionarArchivo = (e) => {
  const archivo = e.target.files[0];
  validarYSepararArchivo(archivo);
};

const validarYSepararArchivo = (archivo) => {
  errorImagen.value = "";

  if (!archivo) return;

  if (!archivo.type.startsWith("image/")) {
    errorImagen.value = "El archivo debe ser una imagen";
    return;
  }

  if (archivo.size > 5 * 1024 * 1024) {
    errorImagen.value = "La imagen debe ser menor a 5MB";
    return;
  }

  archivoImagen.value = archivo;
  imagenNombre.value = archivo.name;

  const reader = new FileReader();
  reader.onload = (e) => {
    imagenPreview.value = e.target.result;
  };
  reader.readAsDataURL(archivo);
};

const agregarIngrediente = () => {
  formData.value.ingredientes.push({ cantidad: "", nombre: "" });
};

const eliminarIngrediente = (index) => {
  if (formData.value.ingredientes.length > 1) {
    formData.value.ingredientes.splice(index, 1);
  }
};

const agregarPaso = () => {
  formData.value.elaboracion.push({ paso: "" });
};

const eliminarPaso = (index) => {
  if (formData.value.elaboracion.length > 1) {
    formData.value.elaboracion.splice(index, 1);
  }
};

const enviarFormulario = async () => {
  if (!EsValidoFormulario.value) {
    alert("Por favor completa todos los campos requeridos");
    return;
  }

  enviando.value = true;

  try {
    const datosFormulario = new FormData();
    let tiempo = formData.value.tiempo_de_elaboracion;
    if (tiempo && tiempo.length === 5) {
      tiempo = tiempo + ":00";
    }

    datosFormulario.append("titulo", formData.value.titulo);
    datosFormulario.append("tiempo_de_elaboracion", tiempo);
    datosFormulario.append("dificultad", formData.value.dificultad);
    datosFormulario.append("raciones", formData.value.raciones);

    const ingredientesData = formData.value.ingredientes
      .filter((i) => i.cantidad && i.nombre)
      .map((i) => ({
        cantidad: i.cantidad,
        nombre: i.nombre,
      }));
    datosFormulario.append("ingredientes", JSON.stringify(ingredientesData));

    const elaboracionData = formData.value.elaboracion
      .filter((p) => p.paso)
      .map((p) => ({
        paso: p.paso,
      }));
    datosFormulario.append("elaboracion", JSON.stringify(elaboracionData));

    datosFormulario.append("categoria", categoriaSeleccionada.value);

    if (archivoImagen.value) {
      datosFormulario.append("imagen", archivoImagen.value);
    }

    const { data } = await api.post("/recetas/recetas/", datosFormulario);

    emit("receta-creada", data);

    // ✅ Redirigir al inicio después de crear
    router.push("/");
  } catch (error) {
    console.error("Error al crear receta:", error);
    if (error.response?.data) {
      console.error("Response data:", error.response.data);
      const errorMsg = Object.values(error.response.data).flat().join(", ");
      alert("Error: " + errorMsg);
    } else {
      alert("Error al crear la receta. Revisa los datos.");
    }
  } finally {
    enviando.value = false;
  }
};

onMounted(() => {
  cargarCategorias();
  document.addEventListener("click", clicarFuera);
});
</script>

<style scoped>
.formulario-receta {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.formulario-titulo {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--color-texto);
  font-size: 0.95rem;
}

.form-control {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-texto);
  background: var(--fondo-crema);
  width: 100%;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-acento);
}

.form-control-sm {
  padding: 0.5rem;
  font-size: 0.9rem;
}

.form-help {
  font-size: 0.85rem;
  color: var(--color-olea);
  margin-top: 0.25rem;
}

.form-help.error {
  color: #f74545;
}

/* Searchable Select */
.searchable-select {
  position: relative;
  width: 100%;
}

.opciones-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--fondo-crema);
  border: 1px solid var(--color-acento);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
  margin-top: 0.25rem;
  box-shadow: var(--shadow-soft);
}

.opcion-item {
  padding: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
}

.opcion-item:hover,
.opcion-activa {
  background: rgba(96, 108, 56, 0.1);
}

.no-resultados {
  padding: 0.75rem;
  color: #666;
  font-style: italic;
}

/* Drag & Drop Upload */
.upload-dropzone {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--fondo-crema);
}

.upload-dropzone:hover {
  border-color: var(--color-acento);
  background: rgba(96, 108, 56, 0.05);
}

.upload-dropzone.drag-over {
  border-color: var(--color-olea);
  background: rgba(96, 108, 56, 0.1);
  transform: scale(1.02);
}

.upload-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon {
  font-size: 3rem;
  color: var(--color-olea);
}

.upload-preview {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  object-fit: contain;
}

.upload-text {
  margin: 0;
  font-weight: 600;
  color: var(--color-texto);
}

.upload-subtext {
  margin: 0;
  font-size: 0.85rem;
  color: #666;
}

.ingredientes-list,
.elaboracion-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ingrediente-item,
.paso-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.paso-number {
  min-width: 2rem;
  height: 2rem;
  background: var(--color-olea);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.btn-remove {
  background: #f74545;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.btn-remove:hover {
  background: #d43;
}

.btn-add {
  background: transparent;
  border: 2px dashed var(--color-olea);
  color: var(--color-olea);
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
  width: 100%;
}

.btn-add:hover {
  background: rgba(96, 108, 56, 0.1);
}

.btn-submit {
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-border {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Responsive móvil */
@media (max-width: 768px) {
  .formulario-titulo {
    font-size: 1.25rem;
  }

  .upload-dropzone {
    padding: 1.5rem 1rem;
  }

  .upload-icon {
    font-size: 2.5rem;
  }

  .upload-text {
    font-size: 0.9rem;
  }

  .upload-subtext {
    font-size: 0.8rem;
  }

  .ingrediente-item,
  .paso-item {
    flex-wrap: wrap;
  }

  .form-control {
    font-size: 0.95rem;
  }

  .form-control-sm {
    font-size: 0.85rem;
    padding: 0.4rem;
  }

  .paso-number {
    min-width: 1.75rem;
    height: 1.75rem;
    font-size: 0.8rem;
  }

  .btn-remove {
    padding: 0.4rem;
  }
}

/* Responsive tablet pequeña */
@media (max-width: 480px) {
  .formulario-receta {
    gap: 1rem;
  }

  .upload-dropzone {
    padding: 1rem 0.75rem;
  }

  .upload-icon {
    font-size: 2rem;
  }

  .btn-add,
  .btn-submit {
    font-size: 1rem;
    padding: 0.85rem;
  }
}
</style>
