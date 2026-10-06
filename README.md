# MitoMapa canario

Recurso educativo abierto sobre mitos, leyendas y patrimonio canario para
Primaria y Secundaria, con lectura acompañada para Infantil. Autoría: Jesica
Fortes Regalado, Gloria Elsa González Martín y Cristian García Santana.

## Descargas y edición

La distribución web 4.4.1 actualiza las descargas del REA y conserva la aplicación
interactiva 4.4.0. El proyecto eXeLearning 4.4.0 reúne 15 páginas y 95 iDevices:
los 94 originales editables y un iDevice de texto que integra el nuevo
«Explorador interactivo». La aplicación portable incluida permite utilizar las
vistas Inicio, Islas, Juegos y Recursos, las pintaderas interactivas, las pistas,
los pasos Cuento/Retos/Taller y las demás interacciones de la web.

Los tres proyectos conservan las actividades nativas; la selección del informe
determina qué juegos figuran en él:

- [REA completo: 42 juegos en el informe](downloads/MitoMapa_canario_REA_eXeLearning_v4_4_0.elpx).
- [Esencial: 9 juegos en el informe](downloads/MitoMapa_REA_v4_4_0_Esencial.elpx).
- [Intermedio: 33 juegos en el informe](downloads/MitoMapa_REA_v4_4_0_Intermedio.elpx).
- [Fuentes de la web 4.4.1](downloads/MitoMapa_fuentes_web_v4_4_1.zip).

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

Desde este repositorio, que conserva los tres ELPX de partida 4.0.2, usa
Python 3 con `lxml` y ejecuta `python3 tools/build_elpx.py`. El generador actualiza
el modelo ODE, los iDevices Texto, la exportación HTML, los recursos locales,
el buscador y el manifiesto de descarga del proyecto. El ZIP de fuentes web
no incluye los ELPX de partida; se ofrecen como descargas históricas separadas.
Antes de distribuir un cambio, abre, guarda y exporta el resultado con
eXeLearning 4.0.5 y verifica las rutas afectadas.

Las notas de preparación están en [CAMBIOS_REA_4_4_0.md](CAMBIOS_REA_4_4_0.md) y
[CAMBIOS_WEB_4_4_1.md](CAMBIOS_WEB_4_4_1.md). Las comprobaciones de estructura, apertura, guardado, edición y exportación
con eXeLearning 4.0.5 se recogen en [VALIDACION_4_4_0.txt](VALIDACION_4_4_0.txt).
