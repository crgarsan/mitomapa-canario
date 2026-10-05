ACTUALIZAR MITOMAPA WEB Y REA 4.0.2 — 04/10/2026

CLOUDFLARE (Worker existente: mitomapa-canario)
1. Antes de actualizar, descarga el seguimiento desde el recurso publicado si
   necesitas una copia de seguridad del trabajo local.
2. Descomprime MitoMapa_Web_v4_0_2_Cloudflare.zip. index.html debe estar en la raíz.
3. En tu Worker actual, utiliza New deployment y carga este ZIP o todos los archivos
   descomprimidos, según la opción que ofrezca el panel. No crees otro Worker.
4. Conserva Assets directory /, HTML handling auto-trailing-slash y Not found
   handling none si aparecen estos ajustes.
5. Si el panel no ofrece carga de recursos, desde la carpeta usa:
   npx wrangler login
   npx wrangler deploy --assets . --name mitomapa-canario
6. Verifica «Versión web 4.0.2», una descarga «REA 4.0.2», el selector docente
   de tareas, la restauración de un borrador y el pasaporte anterior.
7. Si ves la versión anterior, recarga con Ctrl+F5 o Cmd+Mayús+R.

Se han conservado las claves locales y los identificadores de ruta. Mantener
la misma dirección permite conservar el progreso guardado; no traslada datos
entre navegadores o dominios. No se ha desplegado automáticamente.

DESPLIEGUE DESDE GITHUB
El repositorio incluye un flujo de GitHub Actions para desplegar el Worker desde
main. Permanece desactivado hasta configurar los secretos de Cloudflare y la
variable de activación. La configuración se explica en
DESPLIEGUE_AUTOMATICO.md del repositorio GitHub; no forma parte del ZIP web.
La carga manual anterior sigue disponible mientras tanto.

GITHUB PRIVADO
La web 4.0.2 publicada se ha incorporado a este repositorio junto con la revisión
editorial posterior. El repositorio es la fuente para futuros despliegues.
Al modificar los archivos públicos, ejecuta python3 tools/update_release.py para
actualizar el ZIP editable y SHA256SUMS.txt antes del commit. El flujo de GitHub
verifica ambos y se detiene si falta algún archivo o huella no coincide.
Conserva las etiquetas anteriores y no cambies la visibilidad del repositorio.
Las descargas públicas del REA y del código editable permanecen en Cloudflare;
el repositorio puede seguir privado.

REA NATIVO
Principal: MitoMapa_canario_REA_eXeLearning_v4_0_2.elpx, informe de 42 juegos.
Esencial: 9 juegos en el informe; Intermedio: 33 juegos. Todas las copias conservan
las 14 páginas y 94 iDevices nativos; las tareas excluidas del informe son opcionales.
El pasaporte y las producciones requieren revisión manual. La selección del informe
no cambia la finalización SCORM: adapta y prueba las páginas para utilizar Moodle.
Los enlaces antiguos del ELPX 4.0 y 4.0.1 entregan también la corrección 4.0.2.
Los ZIP anteriores del código se conservan como archivos históricos.

FORMULARIO WEB
Se incluye una valoración voluntaria local. Para activar Google Forms para todo el
alumnado, pega la URL pública de respuesta en configuracion.js y vuelve a desplegar.
No pegues el enlace de edición. No se conoce una URL pública verificable del
formulario web existente; no se ha inventado. El campo del modo docente guarda
un enlace solo en ese navegador. Comprueba que el formulario está publicado.

LICENCIA Y VALIDACIÓN
CC BY-NC-SA 4.0 para los materiales propios; se conservan créditos y fuentes.
Lee CAMBIOS_WEB_4_0_2.md y VALIDACION_4_0_2.txt para ver alcance y límites.
No se han añadido falsas locuciones humanas: el audio sigue dependiendo de las
voces del dispositivo. Los MP3 propios se pueden incorporar posteriormente.

Documentación oficial consultada:
https://developers.cloudflare.com/changelog/post/2025-09-09-interactive-wrangler-assets/
https://descargas.intef.es/cedec/exe_learning/Manuales/manual_exe405/html/informe-de-progreso.html
