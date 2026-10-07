# MitoMapa canario

Recurso educativo abierto sobre mitos, leyendas y patrimonio canario para
Primaria y Secundaria, con lectura acompañada para Infantil. Autoría: Jesica
Fortes Regalado, Gloria Elsa González Martín y Cristian García Santana.

## Descargas y edición

La distribución web 4.4.2 ofrece como descarga principal la adaptación GobCan
del REA 4.4.0. Contiene 39 páginas y 118 iDevices, conservando las 95 identidades
de la edición base, sus 42 juegos y los 16 MP3. Utiliza la plantilla Flux,
Andika, contador de páginas, guía didáctica práctica y fundamentación curricular.
Propone cuatro sesiones para dos islas de libre elección, con 6.º como referencia
del tercer ciclo de Primaria y adaptación a 5.º. Las ocho islas siguen disponibles.

La aplicación portable incluida conserva las vistas Inicio, Islas, Juegos y
Recursos, las pintaderas, las pistas, los pasos Cuento/Retos/Taller, la comparación
y las narraciones. El archivo publicado es idéntico al de la entrega GobCan.

- [REA adaptado a GobCan](downloads/MitoMapa_canario_GobCan.elpx).
- [Código en GitHub](https://github.com/crgarsan/mitomapa-canario); el repositorio
  mantiene su visibilidad privada y requiere acceso autorizado.
- [Fuentes de la web 4.4.2](downloads/MitoMapa_fuentes_web_v4_4_2.zip).

Las ediciones anteriores 4.4.0 conservan 15 páginas y 95 iDevices. La selección
del informe determina qué juegos figuran en él:

- [Edición original: 42 juegos en el informe](downloads/MitoMapa_canario_REA_eXeLearning_v4_4_0.elpx).
- [Esencial anterior: 9 juegos en el informe](downloads/MitoMapa_REA_v4_4_0_Esencial.elpx).
- [Intermedio anterior: 33 juegos en el informe](downloads/MitoMapa_REA_v4_4_0_Intermedio.elpx).

El ZIP de fuentes contiene la aplicación web, sus guías y los 16 MP3. Los
proyectos ELPX se descargan por separado: no se incluyen en ese ZIP, para
evitar duplicar los proyectos que ya contienen la aplicación portable. Se
conservan las ediciones y los paquetes históricos.

Para adaptar el REA, abre una copia del ELPX con una instalación de eXeLearning
compatible con su formato 4.0.5. Las actividades nativas se editan desde
eXeLearning; el componente portable se adapta editando sus fuentes HTML, CSS y
JavaScript. Antes de distribuir una adaptación, comprueba su apertura y
exportación en tu instalación.

## Trabajar en el aula

Se puede empezar por cualquier isla y elegir otra cuando convenga. La guía
práctica aparece primero en Docente y ofrece preparación, una sesión flexible,
apoyos de lectura y creación y juegos opcionales. Ajustes y seguimiento reúne
las herramientas locales para acordar tareas y guardar el trabajo. También
está disponible [la guía docente imprimible](GUIA_DOCENTE.html).

## Narraciones

La web y la aplicación portable del REA contienen 16 MP3: ocho grabaciones de
Jesica Fortes Regalado y ocho alternativas con una entrada sonora suave,
identificada como recreación. El registro público
es `narraciones.js`; la procedencia y las medidas están en
`AUDIO_ORIGENES.json`, y la atribución en `AUDIO_CREDITOS.html`.

Para preparar de nuevo los MP3 se necesitan los WAV originales, Python3,
NumPy y FFmpeg con libmp3lame. Usa `AUDIO_SELECCION.json` y ejecuta:

```sh
python3 tools/prepare_narrations.py --input-dir /ruta/a/los/WAV --selection AUDIO_SELECCION.json --output-dir assets/audio --report /tmp/informe-audio.json
python3 tools/update_release.py
python3 tools/prepare_deploy.py
```

Los WAV originales no se incluyen en el ZIP de fuentes ni en el ELPX. El ambiente
opcional recrea percusión y naturaleza; no se presenta como una grabación
documental de instrumentos o paisajes canarios. Las grabaciones no se reproducen
automáticamente.

## Regenerar el proyecto editable

Para adaptar la edición GobCan, abre una copia de
`downloads/MitoMapa_canario_GobCan.elpx` en eXeLearning. El generador siguiente
corresponde a la edición original 4.4.0 y no reproduce la adaptación GobCan.

Para regenerar esa edición histórica desde este repositorio, que conserva los
tres ELPX de partida 4.0.2, usa Python 3 con `lxml` y ejecuta
`python3 tools/build_elpx.py`. El generador actualiza
el modelo ODE, los iDevices Texto, la exportación HTML, los recursos locales,
el buscador y el manifiesto de descarga del proyecto. El ZIP de fuentes web
no incluye los ELPX de partida; se ofrecen como descargas históricas separadas.
Antes de distribuir un cambio, abre, guarda y exporta el resultado con
eXeLearning 4.0.5 y verifica las rutas afectadas.

Las notas actuales están en [CAMBIOS_REA_GOBCAN.md](CAMBIOS_REA_GOBCAN.md) y
[CAMBIOS_WEB_4_4_2.md](CAMBIOS_WEB_4_4_2.md). Las comprobaciones de la descarga
y la publicación se recogen en [VALIDACION_WEB_4_4_2.txt](VALIDACION_WEB_4_4_2.txt).
La validación de la edición histórica permanece en
[VALIDACION_4_4_0.txt](VALIDACION_4_4_0.txt).
