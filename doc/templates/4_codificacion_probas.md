# URL da páxina web

# Deseño dos prototipos

## Prototipo 1

### Data de entrega:

05/05/2026

### Funcionalidades implementadas:

- Modelos, estructuración de carpetas, login, register e logout.

### Observacións:

- Tiven moitos problemas en canto á creación dos dockers e das dependencias. Tamén tiven que modificar bastante o settings.py xa que tiven varios problemas de CORS.
- Todavía non uso a paleta de cores nin tipografía que usarei no proxecto final, prioricei familiarizarme con esta forma de traballar e usar os estilos básicos de bootstrap, no seguinte prototipo xa se aplicará a paleta de cores axeitada.

### Innovación:

- Uso de sistema de usuarios personalizado, non uso o sistema de usuarios extendido de DJANGO para unha maior personalizacion e flexibilidade.

## Prototipo 2

### Data de entrega:

19/05/2026

### Funcionalidades implementadas:

Sistema de likes e comentarios, restricción de accesos a non logueados e vista detalle receitas.

### Observacións:

- Moitos problemas de enrutamento, nas peticions entre back e front.
- Cometín un erro na escolla do usuario creado por min en vez de extendelo de DJANGO, xa que hai moitas funcions de autenticacion que teño que facer a man por ser un usuario personalizado.

### Innovación:

## Prototipo Final

### Data de entrega:

02/06/2026

### Funcionalidades implementadas:

Sistema de baneos/strikes, formularios para engadir recetas e categorías e edición de perfil.

### Observacións:

- Tiven moitos problemas ca autenticación e edición dos usuarios, xa que me facían conflicto o super user de DJANGO cos usuarios creados para a web.

### Innovación:

- Uso de compoñentes para modais, listados para un uso de SPA.
- Cambio no sistema de baneos,cando un usuario chega a 3 strikes, notifícaselle tanto a el como ao usuario Admin para proceder ao seu borrado.
