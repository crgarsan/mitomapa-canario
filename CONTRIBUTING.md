# Contribuir a MitoMapa

Las propuestas deben conservar el contenido educativo, las fuentes y las condiciones de reutilización. Describa el problema, el comportamiento esperado y una forma breve de comprobarlo.

## Preparar el entorno

Trabaje en una rama a partir del `main` remoto vigente. El proyecto requiere Python 3.12 y Node.js 22 o posterior. Para las pruebas de navegador:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-browser-tests.txt
.venv/bin/python -m playwright install chromium chrome
npm ci --ignore-scripts --no-audit --no-fund
```

Las pruebas de impresión utilizan Poppler y las de vídeo, FFmpeg. Consulte el workflow de validación para las dependencias del sistema.

## Elegir el producto que se modifica

- La web, el ELPX nativo y los ZIP son entregas distintas. Cambiar JavaScript no actualiza por sí solo el ELPX ni el seguimiento de Moodle.
- Las variantes ES y EN comparten el progreso del navegador. Una corrección de comportamiento debe comprobar ambas y conservar los esquemas de exportación e importación.
- `VERSION.json` identifica las ediciones. `VERSION.txt`, `version.js`, `README_ACTUALIZACION.txt`, el bloque vigente del README y `EDICIONES.md` se generan a partir de sus datos.
- Un cambio de la web no requiere regenerar el ELPX. Las revisiones nativas utilizan `tools/sync_current_elpx.py` y sus propias pruebas.

## Preparar y comprobar el cambio

Primero añada una regresión que muestre el problema. Compruebe después la corrección y un caso de uso válido. Use datos ficticios; un archivo de seguimiento puede contener nombres y respuestas del alumnado.

Añada al índice de Git sólo los archivos nuevos ya revisados. El empaquetador utiliza ese inventario para evitar incluir borradores locales.

```sh
python3 tools/update_release.py
python3 tools/sync_current_elpx.py --check
python3 tools/update_release.py --check
python3 tools/harden_jspdf_exports.py --check
python3 tools/harden_drawing_archives.py --check
node --test tests/*.test.js
```

Ejecute también las pruebas Python y de navegador correspondientes al cambio. La validación completa está descrita en `.github/workflows/deploy-cloudflare.yml`. No se deben regenerar ni sustituir los descargables históricos para hacer pasar una prueba.

## Entregar la propuesta

La PR debe explicar el cambio, sus pruebas y cualquier comprobación pendiente. Identifique las versiones y los paquetes afectados. Indique si una prueba se hizo en un dispositivo físico o mediante emulación.

El procedimiento de [preparación de publicaciones](docs/PUBLICACIONES.md) produce una entrega fijada a un commit. La preparación, la creación de una release y el despliegue son acciones distintas.

La propuesta de política de divulgación privada de seguridad se mantiene en la [PR #47](https://github.com/crgarsan/mitomapa-canario/pull/47). Esa referencia no acredita que un canal privado esté habilitado.
