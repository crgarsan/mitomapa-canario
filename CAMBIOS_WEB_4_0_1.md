# Web y REA 4.0.1 — 30/09/2026

Revisión de la entrega 4.0. Pendiente de publicación por la autoría.

## Correcciones
- ELPX: se elimina la carpeta resources duplicada de las referencias internas.
  Los datos editables y los datos de la exportación quedan sincronizados.
- Web: el historial de insignias permanece en el almacenamiento original.
  Cada pantalla calcula las insignias válidas con los requisitos de la etapa
  seleccionada. Una pintadera histórica sin verdadero/falso no completa una
  ruta de 2.º ciclo, 3.º ciclo o Secundaria. El reto final y el diploma aplican
  el mismo criterio. Se explica esta distinción en el pasaporte y en la guía.
- Investigación: respuestas correctas repartidas entre las tres posiciones.
- Verdadero/falso: se varía la secuencia y se revisan cinco afirmaciones,
  conservando su coherencia con los cuentos. Web y ELPX coinciden.
- Conservados: las ocho rutas, sus producciones, las adaptaciones por etapa,
  el pasaporte manual de eXeLearning, los créditos, la licencia y el estilo.

## Comprobaciones
- Sintaxis JavaScript, recorrido de los 48 ítems de comprensión y V/F,
  desbloqueo del reto final y diploma, 32 combinaciones de etapa e isla.
- Cambio de etapa con progreso antiguo, conservación del historial,
  bloqueo del diploma, impresión, recarga e importación/exportación.
- ELPX: 14 páginas y 94 iDevices; 829 referencias locales verificadas;
  coincidencia entre datos editables y exportados de los cuestionarios.
- No se afirma una prueba manual de apertura y reexportación en el editor
  eXeLearning ni una auditoría WCAG. Las pruebas anteriores se realizaron
  sobre el código y los archivos, con DOM simulado para el comportamiento web.
