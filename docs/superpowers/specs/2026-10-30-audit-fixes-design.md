# Correcciones de la revisión del 30 de octubre

Autorización: preparar una PR para actualizar fflate y corregir los cuatro problemas persistentes con pruebas; sin fusionar ni desplegar. Base: `095d10ed63065b3c65326c17940f16bac30caef9`.

## Comportamiento solicitado

- Sustituir fflate 0.8.2 del ELPX vigente por la distribución oficial 0.8.3, fijada por integridad y SHA-256, conservando exportación y ZIP legítimos. No afirmar una entrada remota a unzipSync sin demostrarla.
- Editar un criterio cualitativo de una etapa invalida su revisión, conservando las de otras etapas. Editar una producción compartida sí invalida todas las revisiones que dependan de ella.
- Consultar un cuento y volver a Crear conserva las dos islas elegidas; una nueva selección explícita puede reemplazarlas y Reiniciar las limpia.
- Un clic sin trazo no marca un lienzo vacío como preparado ni modifica una revisión previa. Conservar trazos reales, deshacer, borrar, alternativas escritas e importación de dibujos.
- A 320 px y fuente raíz 200 %, Inicio/Puzle/ayudas y Pasaporte/Docente se ajustan sin ocultar texto, foco o cierre. Conservar desplazamiento horizontal local de la tabla docente cuando sea necesario.

## Enfoque y límites

Cambios acotados en los módulos actuales, sin rediseño ni migración del almacenamiento. La alternativa de modificar todas las descargas históricas se descarta: son ediciones inmutables y no forman parte de esta actualización. El nuevo ELPX y los dos ZIP vigentes se preparan reproduciblemente dentro de la PR, con versiones web 4.9.2 y ELPX 4.8.9 y manifiestos coherentes. Audios, escenas, juegos nativos, contenido didáctico y metadatos ajenos al cambio permanecen preservados.

Las pruebas adversarias usan únicamente procesos con tiempo límite y localhost aislado. No cambiar DNS, permisos, MFA, producción, WAF, rama main ni configuración de despliegue. La prueba de teclado debe medir una selección nativa realmente confirmada en cada plataforma, sin convertir un fallo de automatización en una afirmación falsa sobre la aplicación.

## Validación

Regresiones rojas antes de cada cambio, controles legítimos y límites, suite existente Python/Node/navegador, cuatro herramientas --check y revisión independiente de compatibilidad y de la dependencia nativa. Entregar la PR abierta con pruebas, límites y hashes de paquetes.
