MITOMAPA WEB 4.0.1 — CARGA DIRECTA EN CLOUDFLARE
Preparado el 30/09/2026. Este ZIP no implica que la web ya esté actualizada.

1. Antes de actualizar, guarda una copia del seguimiento desde Docente.
2. En Cloudflare, abre el Worker existente: mitomapa-canario.
3. En la opción New deployment para cargar archivos estáticos, selecciona
   MitoMapa_Web_v4_0_1_Cloudflare.zip. Si el panel solicita una carpeta,
   descomprime el ZIP y selecciona su contenido completo.
4. index.html debe quedar en la raíz pública, junto a styles.css, scripts.js,
   assets/ y downloads/. No crees una carpeta exterior site/.
5. Si aparecen los ajustes: Assets directory /; HTML handling
   auto-trailing-slash; Not found handling none. Publica con Deploy.
6. Mantén la dirección https://mitomapa-canario.cgarcias.workers.dev/.
7. Comprueba el pie «Versión web 4.0.1», una ruta y la ventana Docente.
   Prueba la descarga «REA 4.0.1» y ábrela en eXeLearning.
8. Si ves la versión antigua, haz una recarga completa. No borres los datos
   del sitio: el progreso se guarda en el navegador.

No subas únicamente el ELPX. Este paquete es la web completa.
No contiene configuración de cuenta, credenciales ni respuestas del alumnado.
No es necesario modificar WordPress si la dirección se mantiene.

GITHUB Y TRAZABILIDAD
Sustituye el contenido de la carpeta que ya sirve la web, conservando la
configuración de despliegue del repositorio. No cambies su privacidad.
Commit sugerido: «Publica web 4.0.1 con REA 4.0.1 y materiales de aula».
Etiqueta sugerida: web-v4.0.1. Guarda el identificador real del despliegue
y su fecha junto al commit. Si no hay integración automática, GitHub
y Cloudflare se actualizan por separado.
VERSION.json identifica las versiones; SHA256SUMS.txt permite comprobar
la integridad de los archivos. Los ZIP anteriores se conservan para no
romper enlaces existentes; los botones visibles apuntan a la versión 4.0.1.

CORRECCIONES DE ESTA REVISIÓN
- Se conserva el historial de pintaderas. El pasaporte, la revisión docente,
  la impresión y el desbloqueo del diploma cuentan solo las que cumplen
  los requisitos de la etapa seleccionada. No se borran respuestas anteriores.
- Opciones de investigación y verdadero/falso variados y coherentes entre
  web y eXeLearning. Se mantienen las preguntas de comprensión originales.
- Referencias internas de imágenes reparadas en el ELPX editable y exportado.
- El enlace antiguo al ELPX 4.0 entrega también el archivo corregido 4.0.1.
- Los ZIP de fuentes de versiones anteriores son archivos históricos;
  utiliza la descarga 4.0.1 para nuevas adaptaciones.

No se ha publicado automáticamente ni se ha modificado tu repositorio GitHub.
En GitHub, actualiza la carpeta web existente y el ELPX con estos archivos.
Crea las etiquetas web-v4.0.1 y rea-exe-v4.0.1 para conservar la trazabilidad.
