# MitoMapa canario · web 4.8.7 · REA 4.8.4

Recurso educativo abierto multinivel sobre relatos, leyendas y patrimonio
canario. Cada docente elige las tareas, los apoyos y el anclaje curricular para
su grupo. Las ocho islas se pueden explorar en cualquier orden.

Autoría: Jesica Fortes Regalado, Gloria Elsa González Martín y Cristian García
Santana. Narración: Jesica Fortes Regalado.

## Edición vigente

La web se publica como **4.8.7**. El REA editable conserva la versión
**4.8.4**, revisada el 22/10/2026, con el mismo archivo y la misma huella.
Son dos recursos diferenciados. La adaptación GobCan tiene
**34 páginas, 118 iDevices, 42 juegos nativos y 16 MP3**. Utiliza el formato
de eXeLearning **4.0.5**, la plantilla Flux y Andika. El ELPX conserva los ocho
cuentos, las escenas, las actividades editables, sus apoyos y la narración local;
no incorpora la aplicación web ni la muestra en un marco incrustado. Su última
página ofrece únicamente un enlace opcional a la web como recurso extra.

- [Web publicada](https://mitomapa-canario.cgarcias.workers.dev/).
- [REA editable vigente · 4.8.4](downloads/MitoMapa_canario_GobCan.elpx).
- [Paquete de la publicación 4.8.7 · incluye el REA 4.8.4](downloads/MitoMapa_REA_v4_8_7.zip).
- [Fuentes web 4.8.7](downloads/MitoMapa_fuentes_web_v4_8_7.zip).

La revisión web del 23/10/2026 actualiza la miniatura compartida a «Ocho piezas»
y utiliza una dirección versionada para solicitar su renovación. Los mensajes
ya compartidos en WhatsApp pueden conservar la vista previa almacenada.

`VERSION.json` identifica la edición y las huellas de las descargas.
`SHA256SUMS.txt` determina los archivos públicos. El repositorio GitHub y las descargas son públicos; el archivo editable
se puede descargar directamente desde la web. Las ediciones y los paquetes anteriores siguen disponibles públicamente
en sus direcciones originales, con las condiciones que tenían al publicarse.

## Trabajar en el aula

La [guía docente práctica](GUIA_DOCENTE.html) ofrece tres posibilidades:

- **Una sesión de unos 45 minutos:** una isla y una tarea acordada.
- **Itinerario corto de cuatro sesiones de unos 50 minutos:** dos islas, una
  comparación, contraste de fuentes y una creación compartida.
- **Banco completo opcional:** ocho a diez sesiones de 35–50 minutos, ajustadas
  a las tareas y a los apoyos. No hay obligación de recorrer las ocho islas.

La web incorpora [Las piezas y sus islas](index.html#piezas-islas), una práctica
opcional para asociar las siete vasijas y la caracola contemporánea de La Graciosa
con las islas que representan en el recurso. Admite arrastre y selección con
toque, clic o teclado. No genera puntuaciones ni premios y no cambia el pasaporte
ni los requisitos del diploma. Las imágenes son recreaciones contemporáneas;
acertar no acredita su presencia arqueológica en cada isla. Las piezas también
se muestran más grandes en el mapa principal para facilitar su reconocimiento. En el
banco de tarjetas se ven solo las imágenes; los nombres y estados permanecen
accesibles para lectores de pantalla y se mantienen los controles con toque,
clic o teclado, sin exigir arrastrar.

En la web, el juego opcional [Nombres de las islas](index.html#nombres-islas) propone
asociar siete denominaciones y la ficha «Sin nombre documentado» con el mapa.
Admite arrastre y selección con toque, clic o teclado. No concede piezas,
no genera calificaciones ni condiciona la ruta. Su apariencia de carta antigua
es una recreación contemporánea que conserva la geografía del mapa, no un
documento de la conquista. La [nota de procedencia y cautelas](FUENTES_CUENTOS.html#nombres-islas)
distingue la selección aportada por la autoría, que informa de consultas con
personas expertas, de la documentación bibliográfica. Las formas, grafías y
cronologías siguen abiertas a contraste; «Sin nombre documentado» no supone
ausencia absoluta de presencia humana en La Graciosa.

La [guía de aplicación GobCan](GUIA_DOCENTE_GOBCAN.html) desarrolla el itinerario
corto y un **ejemplo** curricular del tercer ciclo de Primaria, con 6.º como
referencia y adaptable a 5.º. Ese ejemplo no fija el nivel destinatario del
recurso. Cada docente concreta competencias, criterios, tareas y evidencias
según su programación y la normativa aplicable.

En la web, Docente → Ajustes y seguimiento permite acordar las islas y las tareas. La ruta
se cierra tras revisar las evidencias pactadas: «2/2» puede representar una
ruta de dos islas terminada. La colección de ocho piezas es independiente.
Las listas cualitativas ayudan a mejorar las producciones; no suman puntos ni
generan calificaciones. En el ELPX, la ruta y el pasaporte se acuerdan y revisan
con el profesorado; las orientaciones docentes se organizan en cajas
desplegables. La práctica de los juegos no sustituye la revisión de la lectura,
la investigación o la creación.

**El recurso aún no se ha pilotado con alumnado.** El
[protocolo de pilotaje imprimible](PROTOCOLO_PILOTAJE.html) permite registrar
tiempos, apoyos, dificultades, accesibilidad y propuestas de mejora sin recoger
identificadores del alumnado. La valoración voluntaria admite comentarios
escritos aunque no se hayan respondido las escalas y se descarga localmente
en la web independiente.

## Editar y publicar

Para adaptar el REA, abre una copia del ELPX vigente con eXeLearning 4.0.5 o una
instalación compatible. Sus actividades nativas se editan en eXeLearning.
La web se adapta por separado desde sus fuentes HTML, CSS y JavaScript:
editar el ELPX no modifica la web, ni sus resultados se incorporan al informe
nativo o a SCORM. El enlace final es un complemento externo y no una actividad
incrustada ni un requisito del recorrido. Comprueba la apertura, la navegación
y la exportación antes de distribuir una adaptación.

Para publicar cambios exclusivos de la web, prepara y comprueba sus paquetes
sin regenerar el ELPX:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-browser-tests.txt
python3 tools/update_release.py
python3 tools/update_release.py --check
python3 tools/prepare_deploy.py
```

Si se prepara una revisión del proyecto nativo, utiliza por separado
`tools/sync_current_elpx.py` y comprueba el resultado con `--check` antes de
empaquetar. La publicación 4.8.7 conserva el ELPX 4.8.4 sin cambios.

LXML permite comprobar el modelo nativo y su DTD. Playwright y Pillow se usan
en las pruebas de navegador, no durante la lectura del recurso por el alumnado.

Revisa el resultado antes de publicar. `tools/build_elpx.py` corresponde a la
edición histórica 4.4.0 y **no reconstruye la adaptación GobCan vigente**.
Las políticas de despliegue y de dependencias se comprueban con las pruebas
del repositorio. El despliegue de `main` mediante GitHub Actions publica el
Worker; las descargas históricas deben conservarse en el manifiesto público.
La publicación usa Wrangler **4.152.0**, fijado en el manifiesto y el bloqueo de
dependencias. El flujo instala con `npm ci` y Dependabot propone actualizaciones
de las herramientas y las acciones de GitHub.

Las fuentes web no incluyen proyectos ELPX, archivos ZIP anidados ni los WAV
originales. El paquete del REA incluye el editable y su documentación.

## Narraciones, imágenes y fuentes

Las 16 pistas locales son ocho grabaciones de Jesica Fortes Regalado y ocho
alternativas con una entrada sonora tenue de percusión y naturaleza recreadas.
No se presentan como grabaciones documentales y no se reproducen
automáticamente. La web las registra en `narraciones.js`; el ELPX las conserva
en sus reproductores nativos. La procedencia y la atribución están en
`AUDIO_ORIGENES.json` y `AUDIO_CREDITOS.html`.

Para preparar de nuevo el audio se necesitan los WAV originales, Python 3,
NumPy y FFmpeg con libmp3lame. Las selecciones están en `AUDIO_SELECCION.json`;
después de modificar los MP3, ejecuta la sincronización y las comprobaciones
de publicación anteriores.

Las escenas, las piezas del pasaporte y las pintaderas decorativas son
recreaciones contemporáneas. Las piezas son siete vasijas y una caracola
simbólica de La Graciosa; no reproducen piezas arqueológicas concretas ni
demuestran cómo fue el pasado. [Las fichas de fuentes](FUENTES_CUENTOS.html) distinguen
testimonios, tradición, contexto y decisiones de adaptación. La consulta
crítica de esas fuentes forma parte de la propuesta cuando se acuerda una
tarea de investigación.

## Licencia

[![CC BY-SA 4.0](assets/images/cc-by-sa-4.0.svg)](https://creativecommons.org/licenses/by-sa/4.0/deed.es)

Los materiales propios se ofrecen bajo **Creative Commons
Reconocimiento-CompartirIgual 4.0 Internacional (CC BY-SA 4.0)**. Se permite
copiar, compartir y adaptar, también con fines comerciales, con atribución,
enlace a la licencia, indicación de cambios y la misma licencia para las
adaptaciones. Consulta el [texto legal](LICENSE) y los
[créditos y condiciones específicas](LICENCIA_Y_CREDITOS.txt).

El mapa de relieve procede de TongApp del Gobierno de Canarias y conserva
el aviso facilitado por la autoría sobre su titularidad y libre uso por la
comunidad educativa. No se le atribuye la licencia de los materiales propios.
Las dependencias y las fuentes externas conservan sus condiciones originales.

Sugerencias: [sugerencias.mitomapacanario@gmail.com](mailto:sugerencias.mitomapacanario@gmail.com).
