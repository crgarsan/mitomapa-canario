# MitoMapa canario web 4.9.2

30/10/2026. Correcciones de la revisión de funcionamiento y seguridad.

- Cambiar un criterio cualitativo invalida la revisión de su propia etapa. Las ediciones de una producción compartida conservan la invalidación de todas las etapas que dependen de ella.
- Consultar un cuento y volver a Crear conserva las dos islas elegidas. Abrir Crear directamente o recargar recupera primero la pareja acordada. Las selecciones explícitas y el reinicio siguen disponibles.
- Un clic sin trazo no convierte un lienzo vacío en una creación preparada ni invalida un dibujo revisado. Se conservan trazos, deshacer, borrado, descripción alternativa e importación de dibujos.
- Los títulos, controles, Pasaporte y Docente se ajustan a ventanas de 320 px con fuente raíz al 200 %. Se conserva el foco y el desplazamiento local de la tabla docente.

La publicación identifica el ELPX 4.8.9 y sus dos ZIP vigentes. Las fuentes incluyen los archivos fijados y las plantillas JavaScript que necesita el constructor nativo; el editable base se identifica por hash en VERSION.json y se obtiene por separado. Ver CAMBIOS_REA_4_8_9.md para fflate.

Las nuevas regresiones reproducen los fallos y verifican los controles legítimos. La selección nativa por teclado usa búsqueda por letra, compatible con los entornos ensayados; no depende de que Home/ArrowDown confirme opciones de la misma forma en cada sistema operativo. No se certifica conformidad WCAG global ni eficacia educativa. El pilotaje con alumnado sigue pendiente.

Los cuentos, mapas, imágenes, narraciones y contenido didáctico se conservan. Esta preparación pertenece a una PR: no implica fusión ni despliegue.
