# Respaldo independiente de MitoMapa

El flujo prepara una copia operativa en GitHub Pages, separada del dominio principal y de Cloudflare. La dirección prevista es **https://crgarsan.github.io/mitomapa-canario/**. Este documento y el flujo no demuestran que la copia esté activada ni publicada: esa comprobación se realiza después del despliegue.

La copia lleva un aviso discreto «Copia de respaldo» con un enlace a la web principal. No redirige automáticamente. Mantiene las actividades y los archivos de ejecución, `VERSION.json`, `MEDIA_MANIFEST.json`, todos los medios aprobados y los tres paquetes vigentes identificados en `VERSION.json`: REA, paquete compartido y fuentes. Conserva además una lista explícita de tres materiales docentes actuales, con sus enlaces locales: `Cuaderno_de_ruta_MitoMapa.html` y `Pauta_de_revision_MitoMapa.html`, junto con su versión editable `Pauta_de_revision_MitoMapa.csv`. Los vídeos, audios y PDF binarios se copian sin modificarlos.

Los paquetes históricos permanecen en la infraestructura principal. Sus enlaces se convierten en direcciones absolutas del dominio principal; por tanto, un bloqueo de ese dominio también puede impedir su descarga. No forman parte de esta copia operativa. Esta selección permite cumplir el [límite oficial de 1 GB para una web publicada en Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

## Preparar y comprobar la copia local

Después de instalar los medios definitivos y regenerar la edición pública:

```sh
python3 tools/update_release.py --check
python3 -m unittest discover -s tests -p 'test_backup_stage.py'
python3 tools/prepare_backup.py
cd .backup
sha256sum --check SHA256SUMS.txt
```

En macOS puede utilizarse `shasum -a 256 -c SHA256SUMS.txt` para la última comprobación. El preparador sustituye `.backup` solo después de validar los archivos y el tamaño. Un fallo conserva la copia anterior. No se debe añadir `.backup` al historial del repositorio.

Si preparas el respaldo desde una exportación completa sin Git, indica su inventario revisado con `--inventory RUTA` y el identificador completo del commit de origen con `--source-commit ID`.

La selección parte del inventario público firmado por hashes, comprueba además los pines de `MEDIA_MANIFEST.json` y rechaza rutas inseguras y enlaces simbólicos. Excluye herramientas, pruebas, QA, secretos, directorios ocultos, archivos `.old` y la configuración específica del proveedor principal. Las referencias locales con una ruta nombrada que comienza por `/` se adaptan a `/mitomapa-canario/`; los medios continúan alojados en el propio respaldo. El literal `/` aislado no se modifica: se conserva, entre otros usos, el separador de `decoded.split('/')` con el que el código rechaza rutas `../` y sus variantes codificadas.

`BACKUP_MANIFEST.json` identifica el dominio principal, el commit de origen, las versiones, los tres paquetes seleccionados, los tres materiales docentes actuales, los históricos externos y cada archivo público con tamaño y SHA-256. Si la copia local procede de cambios sin confirmar, registra esa circunstancia. `SHA256SUMS.txt` se calcula sobre la copia final, incluido el manifiesto del respaldo. La comprobación de tamaño incluye un margen conservador para las cabeceras del archivo que subirá Pages.

## Activación inicial por la persona propietaria

1. En el repositorio público, abrir **Settings → Pages → Build and deployment** y elegir **GitHub Actions** como fuente.
2. Mantener la dirección `github.io` de proyecto. No asignar el dominio principal ni otro dominio que dependa de Cloudflare.
3. Revisar la protección del entorno `github-pages` para permitir únicamente la rama `main` y las aprobaciones que correspondan.
4. Tras integrar y verificar la edición, ejecutar manualmente **Validate and publish the independent backup**, marcando `deploy`. Las ejecuciones por una propuesta de cambios o por un envío a `main` validan y preparan el artefacto; no publican.

GitHub permite Pages en repositorios públicos con su plan gratuito. El despliegue de una Pages ya configurada usa los permisos `pages: write` e `id-token: write` del token automático. La [acción oficial de configuración](https://github.com/actions/configure-pages/blob/983d7736d9b0ae728b81ab479565c72886d7745b/action.yml) indica que activar Pages mediante `enablement` requiere otro tipo de credencial; el flujo mantiene **`enablement: false`**. No crea ni solicita un PAT. Si Pages no está configurada, debe completarse el paso anterior desde la cuenta propietaria. Véanse la [disponibilidad de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), el [flujo oficial de publicación](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) y sus [permisos de despliegue](https://github.com/actions/deploy-pages#security-considerations).

Todas las acciones utilizadas son oficiales y están fijadas a commits completos: checkout `v7.0.1`, setup-node `v7.1.0`, configure-pages `v5.0.0`, upload-pages-artifact `v5.0.0` y deploy-pages `v4.0.5`. Node 22 ejecuta también la prueba del control de rutas sobre el JavaScript realmente preparado. El flujo no contiene credenciales de Cloudflare ni cambios de configuración de esa infraestructura.

## Verificar la publicación y recuperar el servicio

La comprobación posterior usa HTTPS con validación normal de certificado y nombre del servidor. Compara el SHA del manifiesto remoto con el artefacto construido y verifica el commit y los hashes de la portada, `VERSION.json` y `MEDIA_MANIFEST.json`. Una página de bloqueo con HTTP 200 no satisface estas comprobaciones. El flujo reintenta brevemente por la propagación de Pages y falla si no obtiene la edición esperada.

La misma comprobación puede ejecutarse después desde una copia local de la edición:

```sh
BACKUP_SHA=$(python3 -c "from pathlib import Path;from hashlib import sha256;print(sha256(Path('.backup/BACKUP_MANIFEST.json').read_bytes()).hexdigest())")
python3 tools/prepare_backup.py --verify-url https://crgarsan.github.io/mitomapa-canario/ --source-commit "$(git rev-parse HEAD)" --expected-manifest-sha "$BACKUP_SHA"
```

Si el dominio principal queda inaccesible, puede difundirse la dirección de Pages ya verificada. Para restaurar otro alojamiento estático, verificar primero los hashes de `.backup` y copiar su contenido. Si el nuevo alojamiento sirve desde otra subcarpeta, regenerar con `--base-path`; si sirve desde la raíz, usar `--base-path /`. Conservar por separado una copia local completa de los originales y los históricos, que este artefacto reducido no sustituye.

La copia no reproduce las reglas de Cloudflare ni garantiza acceso frente a bloqueos de redes o plataformas. La web principal conserva su configuración. Pages aporta su propio HTTPS; las verificaciones de certificado y contenido deben seguir pasando antes de anunciar una recuperación.

## Registro de preparación

- Pruebas de selección, integridad, rutas de medios y fallos atómicos realizadas con una edición de prueba pequeña, sin consumir ni alterar medios reales.
- La prueba de una edición instalada debe ejecutarse después de que la coordinación termine sus medios e inventarios; el resumen del preparador indica el número de archivos y bytes reales.
- La activación, el envío de cambios y el despliegue pertenecen a la coordinación. Este trabajo de preparación no los ejecuta.
