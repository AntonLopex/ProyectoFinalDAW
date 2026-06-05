# Proxecto de fin de ciclo DAW

O proxecto consiste no desenvolvemento dunha aplicación web de receitas pensada para que calquera persoa poida descubrir, publicar e compartir pratos dunha forma sinxela e organizada. A plataforma permite crear receitas, engadir imaxes, clasificalas por categorías, buscalas por texto e marcalas como favoritas. Tamén inclúe opcións de interacción entre usuarios, como comentar, dar “likes” e reportar contido inapropiado. Ademais, cada usuario pode personalizar o seu perfil con foto, descrición e ligazóns externas.

A aplicación está deseñada con distintos niveis de acceso: visitantes anónimos, usuarios rexistrados e administradores. Isto permite ofrecer unha experiencia cómoda para quen só quere consultar receitas, ao tempo que se manteñen ferramentas de control e moderación para garantir unha comunidade ordenada e segura. O sistema incorpora tamén medidas como a validación de formularios, a protección fronte a accesos non autorizados e o control de “strikes” para actuar ante comportamentos incorrectos. En conxunto, trátase dunha plataforma útil, visual e pensada para facilitar o intercambio de receitas entre persoas con intereses comúns.

## Instalación/Posta en marcha

Para usar a web de maneira local, basta con baixar o repositorio, colocarse na carpeta `src/` e executar o comando `docker compose up --build`. A continuacion, pode executar manualmente o seguinte comando: `docker compose run web python manage.py loaddata initia_data.json `. Con estos dous simples pasos contarás con unha web totalmente funcional e con datos reais para o seu uso.

## Uso

| Ambiente       | URL                                                                    |
| -------------- | ---------------------------------------------------------------------- |
| **Local**      | [`https://localhost:5173`](https://localhost:5173)                     |
| **Producción** | [`https://frontolea.up.railway.app`](https://frontolea.up.railway.app) |

---

#### 🔹 Endpoints da API

A base da API é: **`https://backolea.up.railway.app/api/`**

### 👤 Autenticación

| Método     | Endpoint    | Descripción           |
| ---------- | ----------- | --------------------- |
| `GET/POST` | `api/auth/` | Listar/crear usuarios |

---

### 📖 Recetas

| Método | Endpoint                                    | Descripción                          |
| ------ | ------------------------------------------- | ------------------------------------ |
| `GET`  | `api/recetas/recetas/`                      | Listar todas as recetas              |
| `POST` | `api/recetas/recetas/`                      | Crear nova receita                   |
| `GET`  | `api/recetas/recetas/<id>/`                 | Ver unha receita en detalle          |
| `POST` | `api/recetas/recetas/<id>/like/`            | Dar/quitar like a unha receita       |
| `GET`  | `api/recetas/recetas/<id>/comentarios/`     | Ver comentarios dunha receita        |
| `POST` | `api/recetas/comentarios/crear-comentario/` | Crear un comentario                  |
| `GET`  | `api/recetas/comentarios/recetas/<id>/`     | Comentarios dunha receita específica |
| `GET`  | `api/recetas/top-recetas/`                  | Top de receitas máis populares       |
| `GET`  | `api/recetas/buscar-usuario/`               | Buscar usuarios                      |

---

### 🏷️ Categorias

| Método | Endpoint                               | Descripción                  |
| ------ | -------------------------------------- | ---------------------------- |
| `GET`  | `api/recetas/categorias/`              | Listar todas as categorías   |
| `POST` | `api/recetas/categorias/`              | Crear nova categoría         |
| `GET`  | `api/recetas/categorias/<id>/recetas/` | Ver receitas dunha categoría |

---

### ⭐ Favoritos

| Método | Endpoint                     | Descripción                  |
| ------ | ---------------------------- | ---------------------------- |
| `POST` | `api/favoritos/<receta_id>/` | Engadir/quitar dos favoritos |

---

### 👤 Perfil de Usuario

| Método | Endpoint                         | Descripción            |
| ------ | -------------------------------- | ---------------------- |
| `GET`  | `api/recetas/perfil/<username>/` | Ver perfil dun usuario |

---

### 🔐 Panel de Administración

| Método       | Endpoint                           | Descripción                 |
| ------------ | ---------------------------------- | --------------------------- |
| `GET`        | `api/recetas/admin/`               | Dashboard de administración |
| `GET`        | `api/recetas/admin/usuarios/`      | Listar todos os usuarios    |
| `GET/DELETE` | `api/recetas/admin/usuarios/<id>/` | Ver/eliminar un usuario     |
| `GET`        | `api/recetas/admin/recetas/`       | Listar todas as recetas     |
| `GET/DELETE` | `api/recetas/admin/recetas/<id>/`  | Ver/eliminar unha receita   |
| `GET`        | `api/recetas/admin/reportes/`      | Listar todos os reportes    |
| `GET/DELETE` | `api/recetas/admin/reportes/<id>/` | Ver/eliminar un reporte     |

---

### 📋 Reportes

| Método | Endpoint                | Descripción      |
| ------ | ----------------------- | ---------------- |
| `POST` | `api/recetas/reportes/` | Crear un reporte |

---

> ℹ️ **Nota:** Reemplaza `<id>`, `<username>`, `<receta_id>`, `<categoria_id>` e `<pk>` co valor correspondente ao acceder aos endpoints.

Poderá rexistrarse na web de forma libre ou usar as seguintes credenciais:

| Usuario  | Contrasinal |
| -------- | ----------- |
| **ALL**  | 123456789   |
| **ALL1 (ADMIN)** | 123456789   |

## Sobre a persoa autora

Son unha persoa con perfil técnico orientado ao desenvolvemento web full-stack, con experiencia en frontend, backend, integración de APIs e traballo con bases de datos. Destaco especialmente no desenvolvemento "backend", sempre prestando atención á estrutura do código, á funcionalidade e á optimización do mesmo. Escollín este proxecto porque me permitía unir funcionalidades reais e útiles nunha aplicación completa, traballando tanto a parte visual como a lóxica de negocio e a administración de contido. A forma máis fiable de contacto é o meu correo electrónico profesional: antonlopez2004@gmail.com.

## Licencia

[LICENSE](license)

## Memoria

1. [Estudo preliminar](doc/templates/1_estudo_preliminar.md)
2. [Análise](doc/templates/2_analise.md)
3. [Deseño](doc/templates/3_deseno.md)
4. [Planificación e Orzamento](doc/templates/a3_orzamento.md)
5. [Codificación e Probas](doc/templates/4_codificacion_probas.md)
6. [Futuro e comercialización](doc/templates/5_manuais.md)

