# Análise: Requirimentos do sistema

## Descrición xeral

O proxecto consiste no desenvolvemento dunha aplicación web de tipo **recetario colaborativo**, onde os usuarios poden crear, compartir e descubrir receitas de cociña. A idea principal é construír unha plataforma dinámica na que os usuarios non só publiquen contido, senón que tamén interactúen entre eles mediante comentarios, valoracións e rankings.

## Requirimentos

A continuación descríbense as funcionalidades principais da aplicación:

### Funcionais:

1. O sistema permitirá o rexistro de novos usuarios mediante formulario.
2. O sistema permitirá o inicio e peche de sesión.
3. O usuario poderá crear novas receitas.
4. O usuario poderá editar e eliminar as súas propias receitas.
5. O sistema permitirá visualizar receitas doutros usuarios.
6. O sistema permitirá clasificar receitas por categorías.
7. O sistema permitirá buscar receitas mediante texto.
8. O sistema permitirá filtrar receitas por categoría ou popularidade.
9. O sistema permitirá paxinación ou carga progresiva nas listas de receitas e comentarios longos.
10. O usuario poderá subir imaxes asociadas ás receitas mediante "drag & drop".
11. O sistema validará o tamaño e formato das imaxes subidas.
12. O usuario poderá comentar receitas.
13. O usuario poderá valorar receitas mediante "likes".
14. O usuario poderá reportar receitas ou comentarios inapropiados.
    - Cada contido pode ser reportado unha única vez.
    - Ao ser reportado, o contido deixa de mostrarse ao público e pasa á páxina de reportes do administrador.
    - O administrador revisa o reporte:
      - Se o contido é inapropiado → asigna un "strike" ao usuario e elimina o contido.
      - Se o contido non é inapropiado → elimina o reporte e o contido volve mostrarse no perfil do usuario correspondente.

15. O sistema calculará un "ranking" de receitas baseado nos "likes".
16. O usuario poderá gardar receitas como favoritas.
17. O usuario poderá ver o seu perfil con receitas propias e favoritas.
18. O usuario poderá editar o seu perfil (foto, descrición e enlaces externos).
19. O sistema permitirá a visualización de perfís doutros usuarios.
20. O sistema mostrará unha ventá modal aos usuarios non autenticados ao intentar interactuar coa aplicación.
21. O administrador poderá eliminar contido inapropiado (comentarios ou receitas).
22. O administrador asignará un "strike" a un usuario tras revisar o reporte feito por outro usuario.
23. O sistema levará un control do número de "strikes" por usuario.
24. O sistema eliminará automaticamente a conta dun usuario ao alcanzar o 3 "strikes".
25. O administrador poderá visualizar un listado de usuarios con información relevante (rol, "strikes", estado).
26. O administrador poderá eliminar usuarios manualmente.
27. O sistema mostrará mensaxes de erro e validación nos formularios.

### Non funcionais:

#### Seguridade

- Os contrasinais almacenaranse cifrados.
- Control de acceso segundo tipo de usuario.
- Protección fronte a ataques comúns como p.e. CSRF.
- Validación de datos tanto no frontend como no backend.
- Control de accións de usuarios non autenticados.

#### Usabilidade

- Interface sinxela e intuitiva.
- Navegación clara entre seccións.
- Feedback visual nas accións do usuario (mensaxes, alertas, modais).
- Sistema de interacción intuitivo para usuarios rexistrados e anónimos.

#### Compatibilidade

- A aplicación será accesible desde navegadores modernos.
- Deseño responsive para móbiles, tablets e ordenadores.

#### Escalabilidade

- Posibilidade de migrar o almacenamento de imaxes a servizos externos.
- Posibilidade de implementar unha lóxica máis profesional de suspensión temporal de usuarios (1º strike → 4h, 2º → 1 día, 3º → eliminación) con notificacións en tempo real.

#### Accesibilidade

- Uso correcto de etiquetas HTML.
- Contrastes de cores axeitados.
- Navegación básica posible mediante teclado.
- Descrición alternativa para imaxes (alt text) nas receitas e fotos de perfil.

## Tipos de usuarios:

Na aplicación existirán varios tipos de usuarios, definidos en función das accións que poden realizar dentro da plataforma:

### Usuario anónimo

- Pode acceder á web sen rexistrarse.
- Pode ver as receitas publicadas.
- Pode usar o buscador e filtros.
- Non pode comentar, valorar nin gardar receitas.
- Ao intentar realizar calquera acción interactiva ("like", comentario, favoritos), mostrarase unha ventá modal solicitando o inicio de sesión.

### Usuario rexistrado

- Debe ter a sesión iniciada na aplicación.
- Pode crear, editar e eliminar as súas propias receitas.
- Pode comentar receitas doutros usuarios.
- Pode valorar receitas mediante "likes".
- Pode gardar receitas como favoritas.
- Pode reportar receitas ou comentarios inapropiados.
- Pode personalizar o seu perfil (foto, descrición, enlaces a redes sociais...).
- Ten acceso ao seu perfil persoal no que poderá comprobar se ten "strikes".
- Ao chegar a 3 "strikes", o usuario será eliminado automaticamente xunto con todas as súas receitas.

### Usuario administrador

- Ten acceso ao panel de administración.
- Pode eliminar receitas ou comentarios inapropiados.
- Pode xestionar usuarios (ver listado, roles, "strikes").
- Pode eliminar usuarios manualmente.
- Pode asignar "strikes" aos usuarios ao moderar contido.
