# Caducidad local del trabajo a los 15 días

## Alcance acordado

La web elimina el nombre opcional, las respuestas, los dibujos, el progreso y las revisiones locales al cumplirse 15 períodos de 24 horas. Conserva idioma, etapa, ajustes de lectura y narración y configuración del formulario. No afecta a las copias descargadas, al ELPX, a Moodle ni a los registros del alojamiento. Esta rama no se fusiona ni despliega.

## Decisiones de implementación

- Plazo fijo desde el primer guardado local; abrir la web no lo prorroga. El trabajo anterior sin fecha recibe sus primeros 15 días al abrir la nueva versión. Importar o reiniciar comienza un período nuevo.
- Comprobar antes de cargar datos, al vencer el temporizador y al volver a la pestaña. Con el navegador cerrado, la limpieza queda para la siguiente apertura.
- Preparar el guardado con el mismo bloqueo de las importaciones antes de cargar el núcleo clásico de la aplicación. Rotar la generación antes de retirar sus claves: una pestaña antigua no puede volver a guardar trabajo caducado. Conservar sólo campos expresamente no identificativos de las preferencias mixtas.
- Informar del plazo y de la posibilidad de guardar seguimiento en ES/EN. Si el navegador impide comprobar o borrar datos, no mostrar el trabajo caducado ni afirmar que se ha eliminado; avisar del problema de almacenamiento. Las claves pendientes de eliminación se conservan como metadatos de limpieza para reintentarlas al recuperar el acceso.

## Alternativas consideradas

Se adopta la comprobación síncrona antes de leer el trabajo, integrada con la generación existente. Un borrado después del renderizado mostraría datos caducados y exigiría bloquear también las escrituras iniciales. Un plazo renovable por visita permitiría conservar trabajo indefinidamente y no satisface el reinicio periódico solicitado.

## Verificación

Pruebas de límite exacto, migración, plazo no renovable, preferencias conservadas, importación/reinicio, pestañas ES/EN y fallos de almacenamiento. Las pruebas usan datos ficticios en un servidor local.
