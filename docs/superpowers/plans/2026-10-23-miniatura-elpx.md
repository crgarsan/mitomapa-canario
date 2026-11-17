# Miniatura actual del ELPX

Objetivo: corregir la vista previa guardada del proyecto, conservando la portada,
las actividades, los audios, las escenas y la licencia actual CC BY-SA 4.0.

1. Reproducir el defecto con una prueba: ambos PNG del proyecto y el campo
   pp_screenshot deben coincidir con la captura actual, distinta de la anterior.
2. Capturar la portada actual mediante el navegador. Guardar el PNG y su SHA y
   dimensiones en VERSION.json; la construcción y su comprobación no deben
   necesitar un navegador ni la red.
3. Actualizar exclusivamente screenshot.png, content/resources/screenshot.png y
   pp_screenshot. Mantener theme/screenshot.png y proteger todos los demás medios.
4. Publicar REA 4.8.5 y actualizar su identificación de descarga en web 4.8.9.
   Conservar un snapshot nativo 4.8.4 y todos los paquetes históricos existentes.
5. Construir y comprobar el ELPX, los paquetes y el despliegue; comparar medios y
   juegos con la edición anterior. Obtener revisión independiente y pruebas de
   GitHub antes de integrar. Verificar la descarga pública por su huella.

La ficha ya subida a Mediateca no se modifica: su miniatura deberá renovarse al
reemplazar el archivo allí. La miniatura social azul de la web sigue como está.
