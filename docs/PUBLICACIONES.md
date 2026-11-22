# Preparar una publicación trazable

`VERSION.json` es la fuente de las versiones. Consulte [EDICIONES.md](../EDICIONES.md) para distinguir web ES/EN, ELPX, paquetes y la publicación externa de Mediateca. Una versión web no atribuye esa misma versión al REA.

## Antes de preparar la entrega

1. Integre los cambios aprobados siguiendo sus dependencias y compruebe el `main` remoto.
2. Revise los metadatos y regenere únicamente los documentos y ZIP vigentes afectados con `python3 tools/update_release.py`.
3. Ejecute las pruebas correspondientes y los cuatro verificadores `--check` indicados en CONTRIBUTING.md.
4. Confirme los archivos de publicación. La entrega formal debe corresponder a un commit limpio, no a cambios locales sin confirmar.

Las observaciones públicas guardan su fecha y el commit con el que se compararon. No prueban que un despliegue posterior siga sirviendo esos mismos bytes. La etiqueta editorial del ELPX inglés identifica su base REA 4.8.9. La corrección de la etiqueta no cambia actividades, medios ni bibliotecas. La matriz distingue los bytes de esta entrega de las observaciones públicas anteriores; preparar estos paquetes no acredita su publicación. El preparador de releases no reconstruye el ELPX.

## Preparación local o mediante Actions

El workflow **Prepare a traceable MitoMapa release** recibe el SHA completo de un commit y prepara un artefacto revisable. Sólo tiene permisos de lectura. No crea tags, releases ni despliegues y no necesita credenciales de Cloudflare.

El preparador valida la edición y los paquetes y copia sus mismos bytes a un directorio nuevo. El catálogo externo identifica el commit, cada producto, idioma, versión, tamaño y SHA-256. Las sumas se guardan fuera de los ZIP para evitar que un archivo contenga su propia huella.

La interfaz local y la verificación de una copia se consultan con:

```sh
python3 tools/prepare_release.py --help
python3 tools/prepare_release.py --source-commit SHA_COMPLETO_DEL_COMMIT --check
```

Para crear y verificar una copia local, utilice ese mismo SHA y un directorio nuevo fuera del checkout:

```sh
python3 tools/prepare_release.py --source-commit SHA_COMPLETO_DEL_COMMIT --output /ruta/nueva/entrega
python3 tools/prepare_release.py --source-commit SHA_COMPLETO_DEL_COMMIT --verify-output /ruta/nueva/entrega
```

Si cambia la relación de paquetes vigentes, revise también el catálogo histórico. El parámetro `--source-commit` de `tools/historical_releases.py` identifica el commit que conserva los bytes que pasarán a ser históricos. Añada a Git los nuevos ZIP ya generados, reconstruya el catálogo y vuelva a empaquetar las fuentes para incluirlo. Su comprobador rechaza una procedencia ausente o distinta; en un checkout superficial se debe recuperar previamente ese commit siguiendo ARCHIVO_HISTORICO.md.

La salida preparada incluye las notas y los argumentos de identificación necesarios para una publicación posterior. No sustituya un archivo por otro diferente conservando una misma identidad de entrega. El nombre de la entrega incorpora el commit para distinguir revisiones de paquetes con la misma versión de producto.

## Publicación posterior

Una persona con permisos de publicación debe revisar el artefacto, las notas, los resultados de CI y todas sus sumas antes de autorizar una release. La publicación debe utilizar esos mismos bytes. Después hay que descargar los archivos publicados y verificar SHA-256, tamaño y CRC; una ejecución de Actions correcta no demuestra por sí sola que una URL pública entregue la copia prevista.

La estrategia histórica está en [ARCHIVO_HISTORICO.md](ARCHIVO_HISTORICO.md). Los destinos del catálogo son propuestas hasta que se hayan copiado y comprobado los archivos. Las redirecciones y la retirada del árbol Git forman una fase posterior; los archivos actuales y sus direcciones se conservan durante esta preparación.

GitHub permite hasta 1000 assets por release y exige que cada uno sea menor de 2 GiB. El lote histórico catalogado cabe en esos límites. La release antigua `v4.0.1` se conserva: un archivo con el mismo nombre en Git no tiene necesariamente sus mismos bytes. [Límites oficiales de releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

## Mediateca

Se mantiene anunciada la edición **4.8.8**, correspondiente al archivo adjunto actual de Mediateca, conforme a la decisión de la autoría del 18/11/2026. La comprobación del 17/11/2026 encontró una ficha que todavía anuncia 4.8.4; el descargable directo del proyecto es una edición distinta, 4.8.9. La [propuesta de rectificación](MEDIATECA_RECTIFICACION.md) permite corregir únicamente el texto y los campos de versión con una cuenta autorizada de Mediateca, conservando el adjunto 4.8.8.
