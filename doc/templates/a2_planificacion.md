# Planificación do proxecto

## Metodoloxía prevista

Empregarase unha metodoloxía áxil simplificada, baseada en tarefas curtas semanais.

O desenvolvemento organizarase en entregas incrementais de funcionalidade, priorizando e garantindo a integración continua entre o backend (Django API) e o frontend (Vue.js).

### Características principais:
- Desenvolvemento incremental por funcionalidades
- Integración continua frontend <---> backend
- Prioridade ao funcionamento fronte á optimización inicial
- Uso de Docker como contorno de desenvolvemento
- Probas constantes durante todo o desenvolvemento

---

## Fases planificadas

---

### Fase 1: Estudo preliminar (COMPLETADO)

**Duración:** ata o 7 de abril  

Nesta fase realizouse:
- Análise inicial do problema
- Definición de usuarios e funcionalidades principais
- Estudo de tecnoloxías (Django, Vue, MySQL, Docker)
- Definición da arquitectura do sistema

**Estado:** Entregado o 7 de abril

---

### Fase 2: Análise 🟡 (EN ENTREGA)

**Duración:** 7 – 21 abril  

Nesta fase defínese:
- Requisitos funcionais e non funcionais
- Modelado da base de datos:
  - usuarios
  - receitas
  - comentarios
  - likes
  - favoritos
  - reportes
  - strikes
- Casos de uso
- Estrutura inicial da API

**Estado:** En finalización (entrega inminente)

---

### 📌 Fase 3: Deseño (EN ENTREGA)

**Duración:** 7 – 21 abril  

Nesta fase realízase:
- Deseño da arquitectura do sistema (Django + Vue + Docker)
- Estrutura de carpetas do proxecto
- Deseño da SPA en Vue.js
- Definición de vistas e navegación
- Configuración inicial do contorno con Docker
- Deseño da base de datos relacional

📌 **Estado:** En finalización (entrega inminente)

---

### 📌 Fase 4: Codificación e probas

**Duración:** 22 abril – 9 xuño  

Nesta fase desenvólvese toda a aplicación.

#### Backend (Django API)
- Modelos principais:
  - usuarios
  - receitas
  - comentarios
  - likes
  - favoritos
  - reportes
  - strikes
- API REST con Django REST Framework
- Sistema de autenticación
- Endpoints para toda a lóxica da aplicación
- Panel de administración
- Xestión de reportes e strikes

#### Frontend (Vue.js)
- Vue Router (navegación)
- Layout xeral (Header e Footer)
- Páxinas:
  - Home
  - Lista de receitas
  - Detalle de receita
  - Perfil de usuario
  - Login / Rexistro
  - Panel de administración
- Consumo da API con Axios
- Componentes reutilizables

#### Probas
- Probas de integración frontend <---> backend
- Validación de formularios
- Probas de seguridade básicas
- Corrección de erros
- Optimización de chamadas API

**Resultado:** Aplicación funcional completa

---

### Fase 5: Manuais do proxecto

**Duración:** 5 – 9 xuño  

Nesta fase realízase a documentación final:

- Manual de instalación (Docker)
- Manual técnico do desenvolvemento
- Manual de usuario
- Documentación da API
- Instrucións de despregue do proxecto
- Preparación da defensa oral

**Resultado:** Proxecto documentado e listo para entrega final

---

## Resumo do calendario

| Fase | Estado | Datas |
|------|--------|------|
| Estudo preliminar | completado | ata 7 abril |
| Análise | en entrega | 7 – 21 abril |
| Deseño | en entrega | 7 – 21 abril |
| Codificación e probas | pendente | 22 abril – 9 xuño |
| Manuais do proxecto | pendente | 5 – 9 xuño |