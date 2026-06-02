# Forum

## DIAGRAMA BASE DE DATOS

```mermaid
erDiagram

  %% ─────────────────────────────
  %% USUARIOS Y RELACIONES BASE
  %% ─────────────────────────────

  USUARIOS {
    int id PK
    string nombre
    string email
    string password_hash
    string rol "ENUM: Admin, cliente, control, comercial, proveedor, invitado"
    string nombreEmpresa
    string cifEmpresa
    string codigo
    string direccionEmpresa
    ENUM tipo_vc " V, C "
    int comercial_id FK
    Datetime fecha_llegada
    string qr_token "UNIQUE"
    bool estado
    datetime fecha_alta
  }

  USUARIOS ||--o{ USUARIOS : "comercial asignado"
  USUARIOS ||--o{ CONTROL_ES : "registra"
  USUARIOS ||--o{ PEDIDOS : "realiza"
  USUARIOS ||--o{ PRODUCTOS : "provee"
  USUARIOS ||--o{ ACOMPAÑANTE : "tiene"
  USUARIOS ||--o{ PRESENTACION_USUARIO : hace
  PRESENTACION ||--o{ PRESENTACION_USUARIO : incluye
  USUARIOS ||--o{ SOLICITUD : "realiza"
  USUARIOS ||--o{ PRESENTACION : "se apunta a"

  %% ─────────────────────────────
  %% ACCESOS / CONTROL
  %% ─────────────────────────────

  CONTROL_ES {
    int id PK
    int usuario_id FK
    datetime hora_entrada
    datetime hora_salida
    string observaciones
    string tipoAcceso "ENUM:QR o Manual"
  }

  %% ─────────────────────────────
  %% PEDIDOS / PRODUCTOS
  %% ─────────────────────────────

  PEDIDOS {
    int id PK
    int cliente_id FK
    datetime fecha_pedido
    string estado
    decimal total "Calc: suma de los subtotales"
    string observaciones
    datetime fecha_actualizacion
  }

  DETALLE_PEDIDO {
    int id PK
    int pedido_id FK
    int producto_id FK
    int cantidad
    decimal precio_unitario
    decimal subtotal "Calc: cantidad × precio_unitario "
  }

  PRODUCTOS {
    int id PK
    string nombre
    string descripcion
    decimal precio
    string imagen_url
    string qr_token "UNIQUE"
    int proveedor_id FK
  }

  PEDIDOS ||--o{ DETALLE_PEDIDO : "contiene"
  PRODUCTOS ||--o{ DETALLE_PEDIDO : "incluye"

  %% ─────────────────────────────
  %% SOLICITUDES / STANDS / MOBILIARIO
  %% ─────────────────────────────

  SOLICITUD {
    int id PK
    int usuario_id FK
    string observaciones
    datetime fecha_solicitud
    string estado
  }

  DETALLE_SOLICITUD_MOBILIARIO {
    int id PK
    int solicitud_id FK
    int mobiliario_id FK
    int cantidad
    decimal precio_total
  }

  DETALLE_SOLICITUD_STAND {
    int id PK
    int solicitud_id FK
    int stand_id FK
    int cantidad
    decimal precio_total
  }

  STAND {
    int id PK
    int solicitud_id FK
    int numeroStand
    decimal precio
    decimal dimensiones
    Enum estado "ENUM: Disponible, Pre-Reservado, Ocupado"
  }

  MOBILIARIO {
    int id PK
    int solicitud_id FK
    string referencia
    string descripcion
    int stock
    decimal precio
  }

  SOLICITUD ||--o{ DETALLE_SOLICITUD_MOBILIARIO : "tiene"
  SOLICITUD ||--o{ DETALLE_SOLICITUD_STAND : "tiene"
  STAND ||--o{ DETALLE_SOLICITUD_STAND : "se solicita"
  MOBILIARIO ||--o{ DETALLE_SOLICITUD_MOBILIARIO : "se solicita"

  SOLICITUD ||--o{ MOBILIARIO : "se solicita "
  SOLICITUD ||--o{ STAND : "se solicita"

  %% ─────────────────────────────
  %% ACOMPAÑANTES / CONFIG / PRESENTACIÓN
  %% ─────────────────────────────

  ACOMPAÑANTE {
    int id PK
    int usuario_id FK
    string nombre
    string apellido
    string qr_token "UNIQUE"
  }

  CONFIG {
    string tipo
    int valor
    string valorStr
    DateTime fecha_forum
  }

  PRESENTACION {
    int id PK
    int usuario_id FK
    Datetime fecha_hora
    string tema
    string descripcion
    int aforo
  }

  PRESENTACION_USUARIO{
    int id PK
    int presentacion_id FK
    int usuario_id FK
  }

  EXTRA{
    int id PK
    int solicitud_id FK
    string descripcion
    int cantidad
    Decimal precio
  }

  HISTORIAL_STANDS {
    int id PK
    int stand_id FK
    int solicitud_origen_id FK
    int solicitud_destino_id FK
    int usuario_origen_id FK
    int usuario_destino_id FK
    string estado_anterior
    string estado_nuevo
    string accion
    text observacion
    datetime fecha
  }


  INCIDENCIAS {
    int id PK
    string titulo
    text descripcion
    int usuario_id FK
    datetime fecha_creacion
    string estado
  }

      %% Relaciones Incidencias
    USUARIOS ||--o{ INCIDENCIAS : "crea"

    %% Relaciones HistorialStands
    STAND ||--o{ HISTORIAL_STANDS : "afecta"
    SOLICITUD ||--o{ HISTORIAL_STANDS : "origen"
    SOLICITUD ||--o{ HISTORIAL_STANDS : "destino"
    USUARIOS ||--o{ HISTORIAL_STANDS : "origen"
    USUARIOS ||--o{ HISTORIAL_STANDS : "destino"

    %% Relaciones Extras
    SOLICITUD ||--o{ EXTRA : "contiene"
```

## JUSTIFICACIÓN TABLAS

- **Usuario**: Almacena a todas las personas que interactúan con la aplicación, independientemente del rol. Rol controla el acceso a cada sección, comercial_id auto-referencia a la misma tabla, un usuario con rol comercial se asigna a un usuario con rol cliente. Evitamos tabla intermedia innecesaria.

- **Control_es**: Registra los accesos mediante QR. El diseño de una única fila por visita (hora_entrada y hora_salida) mejor que dos filas separadas para entrada y salida. (Facilita calculo duración visita, permite detectar el doble escaneo). Almacenamos el tipo de acceso para diferenciarlo de un acceso manual o por escaneo de QR.

- **Presentacion**: Registra las "charlas" que se harán el dia del evento.

- **Presentacion_usuario**: Almacena el historial de personas que se "anotan" a la presentación.

- **Proveedores**: Tabla independiente para los proveedores del catálogo de productos. Permite filtrar el catálogo por proveedor de forma eficiente.

- **Productos** : El catálogo. Referencia a proveedores mediante proveedor_id.

- **Pedidos**: Cabecera del pedido. Contiene el total calculadoo, el estado (pendiente -> confirmado -> cancelado ) y la referencia al usuario que lo hizo.

- **Detalle_pedido**: Líneas del pedido. Guarda precio_unitario. Si el precio de un producto cambia mañana, los pedidos de ayer deben mantener el precio original.

- **Mobiliario**: Almacena el mobiliario existente.

- **Stand**: Almacena los stands existentes.

- **Detalle_solicitud_stand**: Almacena solicitudes de stands.

- **Detalle_solicitud_mobiliario**: Almacena solicitudes de mobiliario.

- **Solicitud**: Almacena las solicitudes de mobiliario y stands.

- **Acompañante**: Esta tabla es creada para registar las personas que vayan acompañando a los clientes. Se relaciona con usuarios ya que varios de sus tipos pueden llevar acompañantes. Estes no tienen rol en la aplicación, si tendrán un codigo qr para el acceso al recinto.

- **Config**: Esta tabla será usada simplemente para conteo.

- **Incidencias**: Tabla destinada a registrar problemas, errores o solicitudes de soporte dentro del sistema. Incluye usuario creador, estado de la incidencia y fecha de creación, permitiendo su seguimiento y resolución.

- **Historial_Stands**:Registra el historial de movimientos y cambios de estado de los stands. Incluye origen, destino, usuarios implicados y estados anteriores y nuevos.  
  Permite trazabilidad completa de asignaciones, cambios y transferencias de stands.

- **Extra**: Permite añadir elementos adicionales a una solicitud, con descripción, cantidad y precio. Se utiliza para servicios o productos no contemplados en tablas principales.