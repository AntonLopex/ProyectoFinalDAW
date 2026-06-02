## 1. Descrición do proxecto

O proxecto consiste no desenvolvemento dunha aplicación web de tipo **recetario colaborativo**, onde os usuarios poden crear, compartir e descubrir receitas de cociña. A idea principal é construír unha plataforma dinámica na que os usuarios non só publiquen contido, senón que tamén interactúen entre eles mediante comentarios, valoracións e rankings.

O obxectivo principal da aplicación é ofrecer un espazo centralizado onde calquera persoa poida gardar as súas receitas, aprender novas ideas culinarias e descubrir cales son as máis populares dentro da comunidade. Ademais, preténdese fomentar a participación dos usuarios mediante un sistema de interacción e valoración que permita destacar o contido máis interesante.

---

## 2. Funcionalidades do proxecto

A aplicación contará coas seguintes funcionalidades principais:

- Rexistro e inicio de sesión de usuarios.
- Xestión de perfil de usuario.
- Creación, edición e eliminación de receitas.
- Visualización de receitas doutros usuarios.
- Clasificación de receitas por categorías (postres, pratos principais, etc.).
- Sistema de valoración das receitas (mediante "likes").
- Comentarios nas receitas para fomentar a interacción.
- Buscador e filtros (por categoría, popularidade, etc.).
- Ranking de receitas máis valoradas.
- Posibilidade de gardar receitas favoritas.

Como funcionalidade adicional, poderíase incluír un pequeno sistema de gamificación, no que os usuarios gañen puntos por participar (subir receitas, comentar, recibir valoracións), aínda que isto non sería o núcleo principal da aplicación.

---

## 3. Estudo de necesidades

A idea do proxecto xorde da necesidade de ter un lugar sinxelo e organizado onde gardar receitas e, ao mesmo tempo, poder descubrir novas ideas doutros usuarios. Hoxe en día moita xente busca receitas en internet, pero normalmente están dispersas en diferentes páxinas, blogs ou redes sociais.

O obxectivo da aplicación é centralizar este contido e facilitar a interacción entre os usuarios, permitindo non só consultar receitas senón tamén valoralas e compartilas. Deste xeito, a aplicación resolve o problema da dispersión da información e mellora a experiencia do usuario.

En canto ao mercado, existen aplicacións e plataformas similares como Cookpad ou Tasty, que permiten compartir receitas e descubrir contido novo. Estas aplicacións teñen unha gran presenza e éxito, xa que ofrecen contido atractivo e interacción social. Non obstante, o proxecto proposto busca unha solución máis sinxela, cun sistema propio de organización e ranking.

A proposta de valor deste proxecto baséase en:
- Unha interface clara e sinxela.
- Un sistema de filtrado e busca eficiente.
- Un ranking dinámico que destaque as mellores receitas.
- Posibilidade de adaptación e ampliación futura.

En canto ao público obxectivo, a aplicación está dirixida principalmente a:
- Persoas interesadas na cociña (afeccionados ou principiantes).
- Usuarios que queiran gardar e organizar as súas propias receitas.
- Comunidades ou grupos que compartan interese pola gastronomía.

Non está enfocada a empresas de forma directa, senón a usuarios individuais e comunidades.

---

## 4. Requirimentos

Para o desenvolvemento do proxecto empregaranse os seguintes medios e tecnoloxías:

### Infraestrutura
- Servidor web para despregar a aplicación.
- Servidor de base de datos.
- Contedores Docker para xestionar os distintos servizos.
- Almacenamento para imaxes das receitas.

---

### Backend
- Linguaxe: Python  
- Framework: Django  
- Xestión da base de datos mediante ORM de Django  
- API REST con Django REST Framework  
- Sistema de autenticación de usuarios integrado  

---

### Frontend
- Linguaxes: HTML, CSS e JavaScript  
- Framework: Vue.js  
- Librería de estilos: Bootstrap  
- Uso de compoñentes dinámicos para filtros, buscas e interacción  

---

### Base de datos
- Sistema: MySQL  
- Almacenamento de usuarios, receitas, comentarios e valoracións  

---

### Outros
- Control de versións con Git (repositorio en GitLab)  
- Uso de Docker para facilitar o despregamento  