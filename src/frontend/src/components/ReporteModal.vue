<template>
  <div class="reporte-modal-overlay" @click="cerrar">
    <div class="reporte-modal-content" @click.stop>
      <div class="reporte-modal-header">
        <i class="bi bi-exclamation-triangle-fill reporte-modal-icon"></i>
        <h2>Reportar Receta</h2>
        <button class="reporte-modal-close" @click="cerrar">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <div class="reporte-modal-body">
        <p class="reporte-modal-desc">
          Estás a punto de reportar la receta:
          <strong>{{ receta?.titulo }}</strong>
        </p>
        <p class="reporte-modal-warning">
          ⚠️ Explica claramente el motivo del reporte. Esto ayudará a moderar el
          contenido.
        </p>

        <div class="form-group">
          <label for="motivo-reporte">Motivo del reporte *</label>
          <textarea
            id="motivo-reporte"
            v-model="motivo"
            class="form-control reporte-textarea"
            rows="5"
            placeholder="Ej: La receta contiene información incorrecta, contenido inapropiado, spam, derechos de autor, otro problema..."
            required
          ></textarea>
          <small v-if="!motivo" class="form-help">
            Por favor, describe el motivo del reporte con detalle.
          </small>
        </div>
      </div>

      <div class="reporte-modal-footer">
        <button class="btn btn-outline" @click="cerrar">Cancelar</button>
        <button
          class="btn btn-red"
          @click="enviarReporte"
          :disabled="enviando || !motivoValido"
        >
          <span v-if="!enviando">
            <i class="bi bi-send"></i> Enviar Reporte
          </span>
          <span v-else>
            <div class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">Enviando...</span>
            </div>
            Enviando...
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";

const router = useRouter();

const props = defineProps({
  receta: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close"]);

const motivo = ref("");
const enviando = ref(false);

const motivoValido = computed(() => {
  return motivo.value.trim().length >= 10;
});

const cerrar = () => {
  emit("close");
  // Recargar la página para que la receta desaparezca
  router.go(0);
};

const enviarReporte = async () => {
  if (!motivoValido.value) {
    alert("Por favor, escribe un motivo de al menos 10 caracteres.");
    return;
  }

  enviando.value = true;

  try {
    const payload = {
      receta: props.receta.id,
      motivo: motivo.value.trim(),
    };

    const { data } = await api.post("/recetas/reportes/", payload);

    alert(
      data.mensaje ||
        "✅ Reporte enviado con éxito. Gracias por ayudar a la comunidad.",
    );
    cerrar();
  } catch (error) {
    console.error("Error al enviar reporte:", error);
    if (error.response?.data) {
      alert(
        "Error: " +
          (error.response.data.detail || JSON.stringify(error.response.data)),
      );
    } else {
      alert("❌ Error al enviar el reporte. Inténtalo de nuevo más tarde.");
    }
  } finally {
    enviando.value = false;
  }
};

watch(
  () => props.receta,
  () => {
    motivo.value = "";
  },
  { immediate: true },
);
</script>

<style scoped>
.reporte-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.reporte-modal-content {
  background: var(--fondo-crema);
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
  /* Ocultar barra de scroll pero mantener scrollable */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE y Edge */
}

.reporte-modal-content::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.reporte-modal-header {
  background: linear-gradient(135deg, #f74545 0%, #d43 100%);
  color: #fff;
  padding: 1.5rem 1.5rem 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.reporte-modal-header h2 {
  margin: 0;
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  flex: 1;
}

.reporte-modal-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.reporte-modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.reporte-modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.reporte-modal-close i.bi {
  font-size: 1.25rem;
}

.reporte-modal-body {
  padding: 1.5rem 2rem;
}

.reporte-modal-desc {
  margin: 0 0 1rem 0;
  color: var(--color-texto);
  font-size: 1rem;
  line-height: 1.6;
}

.reporte-modal-desc strong {
  color: var(--color-olea);
  font-weight: 600;
}

.reporte-modal-warning {
  margin: 0 0 1.5rem 0;
  padding: 1rem;
  background: rgba(247, 69, 69, 0.1);
  border-left: 4px solid #f74545;
  border-radius: 8px;
  color: var(--color-texto);
  font-size: 0.9rem;
  line-height: 1.6;
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

.reporte-textarea {
  width: 100%;
  padding: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  color: var(--color-texto);
  background: var(--fondo-crema);
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  min-height: 120px;
}

.reporte-textarea:focus {
  outline: none;
  border-color: #f74545;
  box-shadow: 0 0 0 3px rgba(247, 69, 69, 0.1);
}

.form-help {
  font-size: 0.85rem;
  color: #f74545;
  margin-top: 0.25rem;
}

.reporte-modal-footer {
  padding: 1.25rem 2rem 1.5rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  border-top: 1px solid #eee;
  background: rgba(0, 0, 0, 0.02);
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 2px solid transparent;
}

.btn-outline {
  background: transparent;
  border-color: #ddd;
  color: var(--color-texto);
}

.btn-outline:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.05);
  border-color: #ccc;
}

.btn-red {
  background: #f74545;
  border-color: #f74545;
  color: #fff;
}

.btn-red:hover:not(:disabled) {
  background: #d43;
  border-color: #d43;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(247, 69, 69, 0.3);
}

.btn-red:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner-border {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Responsive */
@media (max-width: 768px) {
  .reporte-modal-overlay {
    padding: 0.5rem;
  }

  .reporte-modal-content {
    max-height: 95vh;
    border-radius: 12px;
  }

  .reporte-modal-header {
    padding: 1.25rem 1.25rem 1.25rem 1.5rem;
    gap: 0.75rem;
  }

  .reporte-modal-header h2 {
    font-size: 1.25rem;
  }

  .reporte-modal-icon {
    font-size: 1.75rem;
  }

  .reporte-modal-close {
    width: 32px;
    height: 32px;
    top: 0.75rem;
    right: 0.75rem;
  }

  .reporte-modal-body {
    padding: 1.25rem 1.5rem;
  }

  .reporte-modal-desc {
    font-size: 0.95rem;
  }

  .reporte-modal-warning {
    font-size: 0.85rem;
    padding: 0.85rem;
  }

  .reporte-textarea {
    font-size: 0.9rem;
    padding: 0.75rem;
    min-height: 100px;
  }

  .reporte-modal-footer {
    padding: 1rem 1.5rem 1.25rem;
    flex-direction: column-reverse;
    gap: 0.75rem;
  }

  .btn {
    width: 100%;
    justify-content: center;
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .reporte-modal-header {
    padding: 1rem 1rem 1rem 1.25rem;
  }

  .reporte-modal-header h2 {
    font-size: 1.1rem;
  }

  .reporte-modal-icon {
    font-size: 1.5rem;
  }

  .reporte-modal-body {
    padding: 1rem 1.25rem;
  }

  .reporte-modal-desc {
    font-size: 0.9rem;
  }

  .reporte-modal-warning {
    font-size: 0.8rem;
    padding: 0.75rem;
  }

  .reporte-textarea {
    font-size: 0.85rem;
    padding: 0.65rem;
  }

  .reporte-modal-footer {
    padding: 0.85rem 1.25rem 1rem;
  }
}
</style>
