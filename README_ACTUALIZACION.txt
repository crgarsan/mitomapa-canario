MITOMAPA WEB 4.4.4 / REA 4.4.0 — ADAPTACIÓN GOBCAN · 09/10/2026

DESCARGA PRINCIPAL
MitoMapa_canario_GobCan.elpx se abre en eXeLearning 4.0.5 o compatible.
Contiene 39 páginas y 118 iDevices. Se conservan 95 identidades de iDevices,
42 juegos y 16 MP3 de Jesica Fortes Regalado. El archivo es idéntico a la
entrega preparada con la plantilla Flux y las orientaciones de GobCan.
Se organizan Cuento, Retos y Taller por isla; se añaden Andika, contador,
guía didáctica y fundamento curricular. Las islas se eligen libremente.
La propuesta principal trabaja dos islas en cuatro sesiones de unos 50 minutos,
con 6.º como referencia del tercer ciclo de Primaria y adaptación a 5.º.
Las variantes Esencial e Intermedio y las descargas históricas permanecen
como ediciones anteriores; no son la adaptación GobCan.

CÓDIGO EN GITHUB
El apartado de adaptación web enlaza al repositorio
https://github.com/crgarsan/mitomapa-canario
El repositorio conserva su visibilidad privada: requiere acceso autorizado.
El ELPX y los paquetes de fuentes siguen disponibles como descargas públicas.
El ZIP de fuentes web 4.4.4 excluye todos los ELPX y otros ZIP anidados.

DESPLIEGUE AUTOMÁTICO
Cada push a main ejecuta GitHub Actions y publica el Worker existente.
Antes de subir archivos públicos, ejecutar python3 tools/update_release.py
y python3 tools/prepare_deploy.py. El despliegue verifica SHA256SUMS.txt.
No modificar directamente .deploy: se genera a partir de ese manifiesto.
VERSION.json identifica el archivo principal, su tamaño y su SHA-256.

EDICIÓN DEL PROYECTO
Para adaptar GobCan, abrir y guardar una copia del ELPX con eXeLearning.
tools/build_elpx.py corresponde a la edición histórica original 4.4.0,
con 15 páginas y 95 iDevices, y no regenera la adaptación GobCan.
El Explorador conserva su código local dentro del proyecto. La edición nativa
y el código de la aplicación son independientes; comprobar ambas al adaptarlas.

SEGUIMIENTO Y SONIDO
Las claves de almacenamiento, rutas y juegos web se conservan. El progreso
permanece en el navegador y el mismo origen. Docente permite guardar/cargar
seguimiento. El informe nativo y el Explorador tienen seguimiento independiente.
Los ocho cuentos incluyen voz humana de Jesica. El ambiente breve de percusión
y naturaleza es una recreación digital opcional, sin reproducción automática.

LICENCIA Y FUENTES
CC BY-NC-SA 4.0 para los materiales propios. Se mantiene autoría y créditos.
La versión del modelo ImageGen usado en las imágenes originales no quedó
registrada y así se indica en la adaptación. El mapa se sustituye por un mapa de relieve aportado; las 18 imágenes ilustrativas conservan sus archivos.
Consultar CAMBIOS_WEB_4_4_4.md, CAMBIOS_REA_GOBCAN.md y VALIDACION_WEB_4_4_4.txt.

REVISIÓN GOBCAN 09/10/2026
La descarga principal coincide byte por byte con la entrega GobCan revisada. Incluye mapa de relieve aportado con pintaderas seleccionables y pauta cualitativa sin puntuaciones ni pesos. La guía completa está en GUIA_DOCENTE_GOBCAN.html; la guía práctica añade la propuesta de cuatro sesiones como apartado desplegable. Los archivos CSV y HTML de revisión corresponden a esta edición.
