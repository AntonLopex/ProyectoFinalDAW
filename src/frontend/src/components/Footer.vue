<template>
  <footer class="olea-footer">
    <div class="footer-container">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="footer-logo">
            <span class="logo-icon">🍃</span>
            <span class="logo-text">Olea</span>
          </div>
          <p class="footer-description">
            Tu plataforma de recetas saludables. Cocina con sabor, cocina con
            Olea.
          </p>
          <div class="footer-social">
            <a href="#" class="social-link" title="Facebook">
              <i class="bi bi-facebook"></i>
            </a>
            <a href="#" class="social-link" title="Instagram">
              <i class="bi bi-instagram"></i>
            </a>
            <a href="#" class="social-link" title="Twitter">
              <i class="bi bi-twitter-x"></i>
            </a>
            <a href="#" class="social-link" title="YouTube">
              <i class="bi bi-youtube"></i>
            </a>
          </div>
        </div>
        <div class="footer-links">
          <h3 class="footer-title">Enlaces rápidos</h3>
          <ul class="footer-list">
            <li>
              <router-link to="/" class="footer-link">Inicio</router-link>
            </li>
            <li>
              <router-link to="/top-recetas" class="footer-link"
                >Top recetas</router-link
              >
            </li>
            <li>
              <router-link to="/crear" class="footer-link"
                >Añadir Recetas</router-link
              >
            </li>
            <li>
              <router-link to="/crear" class="footer-link"
                >Añadir Categorías</router-link
              >
            </li>
            <li>
              <router-link to="/mi-perfil" class="footer-link"
                >Mi perfil</router-link
              >
            </li>
          </ul>
        </div>

        <!-- Columna 3: Ayuda -->
        <div class="footer-links">
          <h3 class="footer-title">Ayuda</h3>
          <ul class="footer-list">
            <li class="footer-link">Preguntas frecuentes</li>
            <li class="footer-link">Contacto</li>
            <li class="footer-link">Política de privacidad</li>
            <li class="footer-link">Términos y condiciones</li>
            <li class="footer-link">Política de cookied</li>
          </ul>
        </div>

        <!-- Columna 4: Contacto -->
        <div class="footer-contact">
          <h3 class="footer-title">Contacto</h3>
          <ul class="footer-contact-list">
            <li class="contact-item">
              <i class="bi bi-envelope-fill"></i>
              <a href="mailto:info@olea.com">info@olea.com</a>
            </li>
            <li class="contact-item">
              <i class="bi bi-telephone-fill"></i>
              <a href="tel:+34900000000">+34 900 000 000</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Sección inferior: Copyright -->
      <div class="footer-bottom">
        <p class="copyright">
          © {{ currentYear }} Olea. Todos los derechos reservados.
        </p>
        <p class="made-with">
          Hecho con
          <span class="heart"><i class="bi bi-heart-fill"></i></span> y aceite
          de oliva 🫒
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from "vue";

const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
.olea-footer {
  background: linear-gradient(135deg, var(--color-olea) 0%, #5a6b35 100%);
  color: white;
  padding: 3rem 0 1.5rem;
  margin-top: 3rem;
  border-top: 3px solid #8b7355;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Sección superior */
.footer-top {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

/* Logo y descripción */
.footer-brand {
  text-align: center;
}

.footer-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.logo-icon {
  font-size: 2.5rem;
}

.logo-text {
  font-family: var(--fuente-titulos);
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 1px;
}

.footer-description {
  font-size: 0.95rem;
  line-height: 1.6;
  max-width: 350px;
  margin: 0 auto 1.5rem;
  opacity: 0.95;
}

/* Redes sociales */
.footer-social {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.social-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.social-link:hover {
  background: white;
  color: var(--color-olea);
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Enlaces */
.footer-title {
  font-family: var(--fuente-titulos);
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: white;
  position: relative;
  padding-bottom: 0.5rem;
}

.footer-title::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background: #8b7355;
}

.footer-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-link {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  display: block;
  padding: 0.4rem 0;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  position: relative;
  padding-left: 1.2rem;
}

.footer-link::before {
  content: "→";
  position: absolute;
  left: 0;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.3s ease;
}

.footer-link:hover {
  color: white;
  padding-left: 1.5rem;
}

.footer-link:hover::before {
  opacity: 1;
  transform: translateX(0);
}

/* Contacto */
.footer-contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
  font-size: 0.95rem;
}

.contact-item i {
  font-size: 1.1rem;
  color: #8b7355;
  min-width: 20px;
}

.contact-item a {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  transition: color 0.3s ease;
}

.contact-item a:hover {
  color: white;
}

/* Sección inferior */
.footer-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.copyright {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.made-with {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.85;
}

.made-with .heart {
  color: #ff0000;
  display: inline-block;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

/* Responsive */
@media (min-width: 768px) {
  .footer-top {
    grid-template-columns: repeat(2, 1fr);
    gap: 2.5rem;
  }

  .footer-brand {
    text-align: left;
  }

  .footer-description {
    margin: 0 0 1.5rem;
  }

  .footer-social {
    justify-content: flex-start;
  }
}

@media (min-width: 992px) {
  .footer-top {
    grid-template-columns: 1.2fr 1fr 1fr 1fr;
    gap: 2rem;
  }

  .footer-bottom {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
}

@media (max-width: 576px) {
  .olea-footer {
    padding: 2rem 0 1rem;
  }

  .logo-icon {
    font-size: 2rem;
  }

  .logo-text {
    font-size: 1.75rem;
  }

  .footer-description {
    font-size: 0.9rem;
  }

  .footer-title {
    font-size: 1.1rem;
  }

  .social-link {
    width: 40px;
    height: 40px;
    font-size: 1.1rem;
  }
}
</style>
