<!-- components/admin/ModalResolverReporte.vue -->
<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click="cerrar">
      <div class="modal-container" @click.stop>
        <div class="modal-olea modal-xl">
          <div class="modal-header modal-header-danger">
            <div class="header-content">
              <i class="bi bi-exclamation-triangle-fill modal-icon"></i>
              <h3 class="modal-title">Resolver Reporte #{{ reporte?.id }}</h3>
            </div>
            <button class="modal-close" @click="cerrar">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="modal-body">
            <div class="reporte-info card">
              <h4><i class="bi bi-info-circle"></i> Información del Reporte</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">👤 Informador:</span>
                  <span class="info-value"
                    >@{{ reporte?.informador_nombre }}</span
                  >
                </div>
                <div class="info-item">
                  <span class="info-label">🍳 Receta:</span>
                  <span class="info-value">{{
                    reporte?.receta_titulo || "N/A"
                  }}</span>
                </div>
                <div class="info-item full-width">
                  <span class="info-label">📝 Motivo:</span>
                  <span class="info-value motivo">{{ reporte?.motivo }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">📅 Fecha:</span>
                  <span class="info-value">{{
                    formatDate(reporte?.created_at)
                  }}</span>
                </div>
              </div>
            </div>

            <div class="decision-container card">
              <h4><i class="bi bi-scale"></i> ¿Es válido el reporte?</h4>
              <p class="decision-desc">
                <strong>Sí válido:</strong> Se eliminará el contenido y se
                aplicará un strike al usuario.<br />
                <strong>No válido:</strong> Se restaurará el contenido visible.
              </p>
              <div class="decision-buttons">
                <button
                  class="btn btn-success btn-lg"
                  :class="{ 'btn-active': decisionTemporal === 'valido' }"
                  @click="decisionTemporal = 'valido'"
                >
                  <i class="bi bi-check-circle-fill"></i>
                  <span>SÍ, es válido</span>
                </button>
                <button
                  class="btn btn-secondary btn-lg"
                  :class="{ 'btn-active': decisionTemporal === 'invalido' }"
                  @click="decisionTemporal = 'invalido'"
                >
                  <i class="bi bi-x-circle-fill"></i>
                  <span>NO, no es válido</span>
                </button>
              </div>
            </div>

            <transition name="slide-fade">
              <div v-if="decisionTemporal" class="motivo-strike card">
                <h4>
                  <i class="bi bi-pencil-square"></i> Motivo de la
                  {{
                    decisionTemporal === "valido" ? "sanción" : "restauración"
                  }}
                </h4>
                <textarea
                  v-model="motivoStrike"
                  class="form-control"
                  rows="3"
                  :placeholder="
                    decisionTemporal === 'valido'
                      ? 'Describe el motivo del strike...'
                      : 'Describe por qué restaurar el contenido...'
                  "
                  required
                ></textarea>
              </div>
            </transition>
          </div>

          <div class="modal-footer">
            <button class="btn btn-outline" @click="cerrar">
              <i class="bi bi-x-circle"></i> Cancelar
            </button>
            <button
              v-if="decisionTemporal"
              class="btn btn-lg btn-action"
              :class="
                decisionTemporal === 'valido' ? 'btn-danger' : 'btn-secondary'
              "
              @click="resolver"
              :disabled="guardando || !motivoStrike.trim()"
            >
              <span v-if="!guardando">
                <i class="bi bi-gavel"></i>
                {{
                  decisionTemporal === "valido"
                    ? "Aplicar Sanción"
                    : "Restaurar Contenido"
                }}
              </span>
              <span v-else>
                <div class="spinner-border spinner-border-sm"></div>
                Procesando...
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  visible: { type: Boolean, required: true },
  reporte: { type: Object, default: null },
});

const emit = defineEmits(["close", "resolver"]);

const guardando = ref(false);
const decisionTemporal = ref(null);
const motivoStrike = ref("");

watch(
  () => props.reporte,
  (nuevo) => {
    if (nuevo) {
      decisionTemporal.value = null;
      motivoStrike.value = "";
    }
  },
  { immediate: true },
);

const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const cerrar = () => {
  emit("close");
};

const resolver = async () => {
  guardando.value = true;
  try {
    await emit("resolver", {
      decision: decisionTemporal.value,
      motivo_strike: motivoStrike.value,
    });
  } finally {
    guardando.value = false;
  }
};
</script>

<style scoped>
/* Overlay con backdrop blur */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1.5rem;
  backdrop-filter: blur(8px);
}

.modal-container {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-olea {
  background: var(--fondo-crema);
  border-radius: var(--border-radius);
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.modal-xl {
  max-width: 900px;
}

.modal-header {
  background: linear-gradient(135deg, #f74545 0%, #d43 100%);
  color: #fff;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.modal-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.modal-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 600;
  font-family: var(--fuente-titulos);
}

.modal-close {
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
  transition: all 0.3s ease;
  font-size: 1.25rem;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.15) rotate(90deg);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.modal-body::-webkit-scrollbar {
  display: none;
}

.modal-footer {
  padding: 1.5rem 2rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  border-top: 1px solid rgba(96, 108, 56, 0.1);
  background: rgba(96, 108, 56, 0.02);
}

/* Card styles */
.card {
  background: var(--fondo-bloque);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(96, 108, 56, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card:last-child {
  margin-bottom: 0;
}

.card h4 {
  margin: 0 0 1rem 0;
  color: var(--color-texto);
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 0.95rem;
  color: var(--color-texto);
  font-weight: 500;
}

.info-value.motivo {
  background: rgba(96, 108, 56, 0.05);
  padding: 0.75rem;
  border-radius: 8px;
  border-left: 3px solid var(--color-olea);
}

/* Decision container */
.decision-container h4 {
  margin-bottom: 0.5rem;
}

.decision-desc {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.decision-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Buttons */
.btn {
  padding: 0.85rem 1.75rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.05rem;
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

.btn-success {
  background: #28a745;
  border-color: #28a745;
  color: #fff;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
  border-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-danger {
  background: #f74545;
  border-color: #f74545;
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #d43;
  border-color: #d43;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(247, 69, 69, 0.3);
}

.btn-secondary {
  background: #6c757d;
  border-color: #6c757d;
  color: #fff;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
  border-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-action:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-active {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

/* Form */
.form-control {
  width: 100%;
  padding: 0.85rem 1rem;
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  font-size: 1rem;
  color: var(--color-texto);
  background: var(--fondo-crema);
  box-sizing: border-box;
  transition: border-color 0.2s;
  font-family: inherit;
  resize: vertical;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-olea);
  box-shadow: 0 0 0 3px rgba(96, 108, 56, 0.1);
}

.motivo-strike h4 {
  color: var(--color-olea);
}

/* Spinner */
.spinner-border {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
  vertical-align: text-bottom;
}

@keyframes spinner-border {
  to {
    transform: rotate(360deg);
  }
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-olea,
.modal-fade-leave-active .modal-olea {
  transition:
    transform 0.3s ease,
    scale 0.3s ease;
}

.modal-fade-enter-from .modal-olea,
.modal-fade-leave-to .modal-olea {
  transform: scale(0.95) translateY(-20px);
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }

  .modal-olea {
    max-height: 95vh;
  }

  .modal-header {
    padding: 1rem 1.5rem;
  }

  .modal-icon {
    font-size: 1.5rem;
  }

  .modal-title {
    font-size: 1.1rem;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .decision-buttons {
    flex-direction: column;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
