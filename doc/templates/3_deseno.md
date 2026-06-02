# Deseño

## Esquema (boceto ou wireframe).

A continuación mostranse varias das pantallas principáis do proxecto, tendo en conta que é un boceto e pode sufrir algunha pequena modificación á hora de programar a aplicación:

![alt text](../img/Pantalla_de_inicio_móvil.png)

![alt text](../img/Pantalla_de_inicio_ordenador.png)

## Identidade visual

O fondo principal da páxina empregarase nun ton crema suave, que achega sensación de limpeza, amplitude e facilita que os elementos principais destaquen sen cansar a vista. Para as áreas de contido, como receitas e seccións, utilizarase un branco roto que crea unha lixeira diferenciación visual e evita unha aparencia plana.

O color primario será o verde oliva, empregado no logotipo, títulos e elementos destacados. Esta elección está directamente vinculada coa marca, OLEA, nome que fai referencia á familia arbórea das oliveiras, reforzando así a identidade do proxecto e a súa relación co aceite de oliva, un dos ingredientes máis representativos da cociña.

Como cor de acento usarase un ton laranxa terra, reservado para botóns e accións importantes, xa que atrae a atención e guía a interacción do usuario. Por último, o texto principal presentarase nun verde escuro, garantindo boa lectura e mantendo a coherencia cromática do conxunto.

En canto á tipografía, escóllese unha combinación equilibrada entre Lora para títulos e Hind para o corpo de texto. Lora, de estilo serif, achega personalidade, elegancia e un carácter máis editorial aos encabezados, reforzando a identidade visual do proxecto. Pola súa parte, Hind, garante unha lectura clara e fluída nos contidos máis extensos. Esta combinación permite establecer unha xerarquía visual efectiva, mantendo ao mesmo tempo unha experiencia de lectura cómoda e moderna.

A continuación podes ver as devanditas cores e tipografías como se usarán no ficheiro de estilos da aplicación:

```css
:root {
  /* Paleta de Colores */
  --fondo-crema: #fefae0;
  --fondo-bloque: #f8f9fa;
  --color-olea: #606c38;
  --color-acento: #dda15e;
  --color-texto: #283618;
  --color-alerta: #bc6c25;

  /* Tipografías */
  --fuente-titulos: "Lora", serif;
  --fuente-cuerpo: "Hind", sans-serif;
}
```

## Diagrama de Bases de Datos

A continuación móstrase o diagrama da organización da base de datos empregada na nosa app:

```mermaid
---
config:
  layout: dagre
  theme: default
  look: handDrawn
---
erDiagram
	USUARIO {
		int id PK ""
		string nombre_usuario  "OBLIGATORIO"
		string email  "OBLIGATORIO"
		string password_hash  "OBLIGATORIO"
		string foto_perfil  "NULL (Opcional)"
		text biografia_y_enlaces  "NULL (Opcional)"
		enum rol  "registrado, admin"
		int strikes_count  "Default 0"
	}

	RECETA {
		int id PK ""
		int usuario_id FK ""
		string titulo  "OBLIGATORIO"
		text descripcion  "OBLIGATORIO"
		text duracion  "OBLIGATORIO"
		text dificultad  "fácil, media,  difícil"
		string imagen_url  "OBLIGATORIO"
		boolean visible  "Default true"
	}

	COMENTARIO {
		int id PK ""
		int receta_id FK ""
		int usuario_id FK ""
		text contenido  ""
		boolean visible  "Default true"
		datetime created_at  ""
	}

	LIKE {
		int usuario_id PK,FK ""
		int receta_id PK,FK ""
	}

	FAVORITO {
		int usuario_id PK,FK ""
		int receta_id PK,FK ""
	}

	REPORTE {
		int id PK ""
		int informador_id FK ""
		int receta_id FK "Opcional"
		int comentario_id FK "Opcional"
		string motivo  ""
		enum estado  "pendiente, revisado"
		datetime created_at  ""
	}

	STRIKE_LOG {
		int id PK ""
		int usuario_sancionado_id FK ""
		int admin_responsable_id FK ""
		string motivo  ""
		datetime fecha  ""
	}

	RECETA_CATEGORIA {
		int receta_id PK,FK ""
		int categoria_id PK,FK ""
	}

	CATEGORIA {
		int id PK ""
		string nombre  ""
	}

	USUARIO||--o{RECETA:"autor_de"
	USUARIO||--o{COMENTARIO:"autor_de"
	USUARIO||--o{LIKE:"realizado_por"
	USUARIO||--o{FAVORITO:"marcado_por"
	USUARIO||--o{REPORTE:"informado_por"
	USUARIO||--o{STRIKE_LOG:"recibe_sancion"
	USUARIO||--o{STRIKE_LOG:"admin_que_sanciona"
	RECETA||--o{RECETA_CATEGORIA:"tiene"
	CATEGORIA||--o{RECETA_CATEGORIA:"pertenece"
	RECETA||--o{COMENTARIO:"tiene"
	RECETA||--o{LIKE:"recibe"
	RECETA||--o{FAVORITO:"es_guardada"
	RECETA||--o{REPORTE:"es_reportada"
	COMENTARIO||--o{REPORTE:"es_reportado"
```
