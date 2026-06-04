<template>
  <div class="perfil-page">
    <Navbar />

    <div class="container py-4 py-md-5">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-olea" role="status">
          <span class="visually-hidden">Cargando perfil...</span>
        </div>
      </div>

      <div v-else class="perfil-layout">
        <section class="perfil-hero card perfil-card">
          <div class="perfil-hero__top">
            <div class="perfil-hero__avatar">
              <img
                v-if="usuario.foto_perfil"
                :src="usuario.foto_perfil"
                alt="Foto de perfil"
                class="perfil-hero__avatar-img"
              />
              <div v-else class="perfil-hero__avatar-placeholder">
                {{ usuario.nombre_usuario?.charAt(0)?.toUpperCase() || "U" }}
              </div>
            </div>

            <div class="perfil-hero__info">
              <h1 class="perfil-hero__name">
                {{ usuario.nombre }} {{ usuario.apellido1 }}
                {{ usuario.apellido2 }}
              </h1>
              <p class="perfil-hero__username">@{{ usuario.nombre_usuario }}</p>
              <p class="perfil-hero__email">{{ usuario.email }}</p>

              <div class="perfil-hero__actions">
                <router-link
                  to="/editar-mi-perfil"
                  class="perfil-edit-link"
                  title="Editar perfil"
                >
                  <i class="bi bi-pencil-square"></i>
                </router-link>
              </div>
            </div>
          </div>

          <p v-if="usuario.biografia_y_enlaces" class="perfil-hero__bio">
            {{ usuario.biografia_y_enlaces }}
          </p>

          <div class="perfil-stats">
            <div
              class="perfil-stats__item"
              :class="getStrikeItemClass(strikesCount)"
            >
              <span class="perfil-stats__label">Strikes</span>
              <span
                :class="['perfil-stats__value', getStrikeClass(strikesCount)]"
              >
                {{ strikesCount }}
              </span>
            </div>
            <div class="perfil-stats__item">
              <span class="perfil-stats__label">Likes</span>
              <span class="perfil-stats__value">{{ likesRecetas.length }}</span>
            </div>
            <div class="perfil-stats__item">
              <span class="perfil-stats__label">Favoritos</span>
              <span class="perfil-stats__value">
                {{ favoritosRecetas.length }}
              </span>
            </div>
          </div>
        </section>

        <section class="perfil-content card perfil-card">
          <div class="perfil-content__header">
            <button
              type="button"
              class="perfil-toggle"
              :class="{ active: activeTab === 'likes' }"
              @click="activeTab = 'likes'"
            >
              <i class="bi bi-heart-fill me-1"></i>
              Likes
            </button>

            <button
              type="button"
              class="perfil-toggle"
              :class="{ active: activeTab === 'favoritos' }"
              @click="activeTab = 'favoritos'"
            >
              <i class="bi bi-bookmark-fill me-1"></i>
              Favoritos
            </button>
          </div>

          <div class="perfil-content__body">
            <div v-if="activeTab === 'likes'">
              <div v-if="likesRecetas.length" class="recetas-grid">
                <RecetaCard
                  v-for="receta in likesRecetas"
                  :key="`like-${receta.id}`"
                  :receta="receta"
                  @like="handleLike(receta)"
                  @favorite="handleFavorite(receta)"
                  @open-comments="openComments(receta)"
                />
              </div>
              <p v-else class="empty-state">
                No has dado like a ninguna receta todavía.
              </p>
            </div>

            <div v-else>
              <div v-if="favoritosRecetas.length" class="recetas-grid">
                <RecetaCard
                  v-for="receta in favoritosRecetas"
                  :key="`fav-${receta.id}`"
                  :receta="receta"
                  @like="handleLike(receta)"
                  @favorite="handleFavorite(receta)"
                  @open-comments="openComments(receta)"
                />
              </div>
              <p v-else class="empty-state">
                No has guardado recetas en favoritos todavía.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
  <Footer />
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/axios";
import Navbar from "../components/NavBar.vue";
import Footer from "../components/Footer.vue";
import RecetaCard from "../components/RecetaCard.vue";

const loading = ref(true);
const activeTab = ref("likes");
const usuario = ref({});
const strikesCount = ref(0);
const likesRecetas = ref([]);
const favoritosRecetas = ref([]);

const cargarPerfil = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/auth/mi-perfil/");
    usuario.value = data.usuario || {};
    strikesCount.value = data.strikes_count || 0;
    likesRecetas.value = data.likes_recetas || [];
    favoritosRecetas.value = data.favoritos_recetas || [];
  } catch (error) {
    console.error("Error al cargar perfil:", error);
  } finally {
    loading.value = false;
  }
};

const handleLike = async (receta) => {
  const eraLike = !!receta.usuario_like;
  receta.usuario_like = !eraLike;
  receta.likes_count = eraLike
    ? Math.max((receta.likes_count || 0) - 1, 0)
    : (receta.likes_count || 0) + 1;

  try {
    if (eraLike) {
      await api.delete(`/likes/${receta.id}/`);
    } else {
      await api.post(`/likes/${receta.id}/`);
    }
  } catch (error) {
    receta.usuario_like = eraLike;
    receta.likes_count = eraLike
      ? (receta.likes_count || 0) + 1
      : Math.max((receta.likes_count || 0) - 1, 0);
    console.error("Error al actualizar like:", error);
    alert("No se pudo actualizar el like");
  }
};

const handleFavorite = async (receta) => {
  const eraFavorito = !!receta.usuario_favorito;
  receta.usuario_favorito = !eraFavorito;
  receta.favoritos_count = eraFavorito
    ? Math.max((receta.favoritos_count || 0) - 1, 0)
    : (receta.favoritos_count || 0) + 1;

  try {
    if (eraFavorito) {
      await api.delete(`/favoritos/${receta.id}/`);
    } else {
      await api.post(`/favoritos/${receta.id}/`);
    }
  } catch (error) {
    receta.usuario_favorito = eraFavorito;
    receta.favoritos_count = eraFavorito
      ? (receta.favoritos_count || 0) + 1
      : Math.max((receta.favoritos_count || 0) - 1, 0);
    console.error("Error al actualizar favorito:", error);
    alert("No se pudo actualizar favoritos");
  }
};

const getStrikeItemClass = (strikes) => {
  const strikesNum = parseInt(strikes) || 0;

  if (strikesNum >= 3) {
    return "perfil-stats__item--danger";
  } else if (strikesNum >= 2) {
    return "perfil-stats__item--warning";
  }
  return "";
};

const getStrikeClass = (strikes) => {
  const strikesNum = parseInt(strikes) || 0;

  if (strikesNum >= 3) {
    return "perfil-stats-value-danger";
  } else if (strikesNum >= 2) {
    return "perfil-stats-value-warning";
  }
  return "";
};

onMounted(() => {
  cargarPerfil();
});
</script>

<style scoped>
.perfil-hero__actions {
  margin-top: 0.75rem;
}

.perfil-edit-link {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--fondo-bloque);
  color: var(--color-olea);
  text-decoration: none;
  border: 1px solid rgba(96, 108, 56, 0.2);
  transition: var(--transition);
  flex-shrink: 0;
}

.perfil-edit-link:hover {
  background: var(--color-olea);
  color: white;
  transform: translateY(-1px);
}

.perfil-edit-link i {
  font-size: 1.1rem;
}

.perfil-page {
  background-color: var(--fondo-crema);
  min-height: 100vh;
  padding-top: 80px;
}

.perfil-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.perfil-card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.perfil-hero {
  padding: 1.25rem;
}

.perfil-hero__top {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.perfil-hero__avatar {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--color-olea), #8b7355);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-olea);
}

.perfil-hero__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: white;
}

.perfil-hero__avatar-placeholder {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
}

.perfil-hero__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.perfil-hero__name {
  font-family: var(--fuente-titulos);
  color: var(--color-olea);
  margin-bottom: 0.25rem;
  font-size: 1.25rem;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.perfil-hero__username,
.perfil-hero__email {
  margin-bottom: 0.25rem;
  color: var(--color-texto);
  font-size: 0.95rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
}

.perfil-hero__email {
  font-size: 0.9rem;
  color: #666;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  max-width: 100%;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

.perfil-hero__bio {
  margin-top: 1rem;
  margin-bottom: 0;
  color: var(--color-texto);
  line-height: 1.5;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.perfil-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.perfil-stats__item {
  background: var(--fondo-bloque);
  border-radius: 12px;
  padding: 0.85rem;
  text-align: center;
  transition: all 0.2s;
}

/* 2 strikes - naranja suave solo en el item de strikes */
.perfil-stats__item--warning {
  background: #fff3cd;
  border: 2px solid #ffc107;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.25);
}

/* 3+ strikes - rojo suave solo en el item de strikes */
.perfil-stats__item--danger {
  background: #f8d7da;
  border: 2px solid #dc3545;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.perfil-stats__label {
  display: block;
  font-size: 0.8rem;
  color: var(--color-texto);
}

.perfil-stats__value {
  display: block;
  margin-top: 0.2rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-olea);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.perfil-stats-value-warning {
  color: #856404;
  background: #fff3cd;
  font-weight: 700;
  border: 1px solid #ffc107;
}

.perfil-stats-value-danger {
  color: #721c24;
  background: #f8d7da;
  font-weight: 700;
  border: 1px solid #dc3545;
}

.perfil-content__header {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.perfil-toggle {
  border: 1px solid rgba(96, 108, 56, 0.2);
  background: white;
  color: var(--color-olea);
  padding: 0.6rem 1rem;
  border-radius: 9999px;
  font-weight: 600;
  transition: var(--transition);
}

.perfil-toggle.active,
.perfil-toggle:hover {
  background: var(--color-olea);
  color: white;
}

.perfil-content__body {
  padding: 1rem;
}

.recetas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.empty-state {
  margin: 0;
  color: var(--color-texto);
  text-align: center;
  padding: 2rem 0;
}

@media (min-width: 768px) {
  .perfil-layout {
    grid-template-columns: 320px 1fr;
    align-items: start;
  }

  .perfil-hero__top {
    flex-direction: row;
    align-items: center;
  }

  .recetas-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) {
  .recetas-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1200px) {
  .recetas-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 576px) {
  .perfil-content__header {
    flex-direction: column;
  }

  .perfil-stats {
    grid-template-columns: 1fr;
  }

  .perfil-hero {
    padding: 1rem;
  }

  .perfil-content__body {
    padding: 0.75rem;
  }

  .perfil-hero__name {
    font-size: 1.15rem;
  }

  .recetas-grid {
    grid-template-columns: 1fr;
  }
}
</style>
