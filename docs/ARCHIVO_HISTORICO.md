# Preparación del archivo histórico

`HISTORICAL_RELEASES.json` prepara una migración de los paquetes históricos a GitHub Releases. Su estado es `planned`: no acredita una subida, no activa destinos y no autoriza retirar archivos. Los binarios locales y las URL públicas originales se conservan. Este cambio no reescribe el historial Git.

La revisión de procedencia toma como referencia `b4014344450e1862bf1d441df59d824ec2714c22`. En el índice de la propuesta hay 90 ZIP/ELPX: 8 vigentes y 82 candidatos históricos, con 1.585.777.276 bytes históricos en total. El catálogo verifica los bytes históricos contra ese commit; no deduce fechas, versiones internas, compatibilidad ni seguridad del contenido a partir del nombre del archivo.

## Archivos vigentes y consumidores

Las rutas ES vigentes proceden de `download.path`, `sharing_archive.path` y `source_archive.path` de `VERSION.json`. Se conservan esos campos como fuente de verdad. Para la edición inglesa y las colecciones 3D se reutilizan las constantes de `tools/release_support.py`. Así quedan excluidos del archivo histórico:

- Los tres paquetes ES indicados en `VERSION.json`.
- `en/downloads/MitoMapa_Canary_Islands_EN.elpx` y su ZIP.
- `downloads/pintaderas-3d/recreaciones.zip`, `downloads/pintaderas-3d/sellos.zip` y `downloads/vasijas/coleccion.zip`.

El catálogo conserva las referencias exactas a rutas encontradas en `VERSION.json`. Hay cinco candidatos con consumidores conocidos: los dos `presets`, los dos `compatibility_aliases` y `elpx_source.path`. Se marcan con `requiresConsumerAdaptation: true`; mantienen su función y necesitan adaptación antes de cualquier retirada. Estar catalogado como histórico no hace prescindible un archivo ni elimina sus consumidores.

La búsqueda de consumidores cubre `VERSION.json`; no constituye una auditoría completa de enlaces de páginas, materiales descargados, marcadores o sitios externos. Es necesario revisar esos usos y mantener la compatibilidad de las URL originales.

## Destino propuesto e identidad

Se propone una sola release de archivo, con el tag estable `archive-b4014344450e`. Cada entrada registra ruta y URL originales, commit de procedencia, tamaño, SHA-256, comprobación CRC del ZIP/ELPX, consumidores y destino propuesto inactivo. Las URL bajo `https://github.com/crgarsan/mitomapa-canario/releases/download/archive-b4014344450e/` son propuestas, sin disponibilidad comprobada.

Los nombres de assets conservan el basename cuando es único y seguro. Si dos rutas tienen el mismo basename, ambas usan `path-<ruta UTF-8 en hexadecimal><extensión original>`: una transformación reversible que distingue también barras y guiones bajos. El checker rechaza nombres inseguros, nombres de más de 255 caracteres o colisiones residuales. En el inventario actual no hay colisiones de basename.

No se reutiliza una release de producto por una semejanza del nombre. En particular, el ELPX del repositorio llamado `MitoMapa_canario_REA_eXeLearning_v4_0_1.elpx` no debe sobrescribir un asset existente de `v4.0.1`: la comparación previa comunicada identifica bytes distintos. La nueva release de archivo evita esa sustitución; cada comparación futura debe hacerse con tamaño y SHA-256 completos, además del CRC, nunca solo con nombres o etiquetas.

## Generación y verificación local

Desde un checkout Git que contenga el commit de procedencia:

```sh
python3 tools/historical_releases.py --source-commit b4014344450e1862bf1d441df59d824ec2714c22
python3 tools/historical_releases.py --check
python3 -m unittest discover -s tests -p 'test_historical_releases.py'
```

La generación escribe únicamente `HISTORICAL_RELEASES.json`. No modifica binarios, sumas, paquetes de distribución ni servicios remotos. El resultado es determinista: no incorpora la hora de ejecución.

`--check` solo lee. Comprueba el inventario exacto aprobado por el índice Git, la exclusión e identidad de los vigentes, los hashes y tamaños históricos, su igualdad con los objetos del commit de procedencia, el CRC de todos los paquetes y la unicidad y seguridad de los destinos. Los hashes y tamaños declarados en los campos vigentes de `VERSION.json` deben coincidir con sus archivos. Cada cambio de rutas vigentes o de consumidores requiere revisar y regenerar el catálogo.

La comprobación de procedencia requiere el checkout y el commit completo disponible localmente. Si CI usa un checkout superficial de profundidad 1 y no contiene `b4014344450e1862bf1d441df59d824ec2714c22`, el checker termina con `Cannot verify source commit provenance from this Git checkout`; no sustituye ese control por una presunción basada en nombres. El flujo manual de publicación deberá preparar un fetch controlado del commit de referencia antes de ejecutar el checker, por ejemplo `git fetch --no-tags origin b4014344450e1862bf1d441df59d824ec2714c22`, y comprobar que el commit esperado está disponible. El checker no hace ese fetch automáticamente. No se puede acreditar esa procedencia desde un ZIP de fuentes que no contiene Git ni los paquetes históricos. Los helpers públicos son `current_archive_paths(root, version)`, `build_catalog(root, source_commit=..., version=None, inventory=None)` y `check_catalog(root, catalog=None, version=None, inventory=None)`; estos dos últimos devuelven el catálogo y lanzan `ValueError` cuando no se puede verificar. El parámetro opcional `inventory` sigue el contrato de inventarios de `release_support`, sin sustituir la exigencia de procedencia Git.

## Transición pendiente

Una migración posterior necesita aprobación externa explícita y un cambio revisado. Antes de retirar un solo archivo, debe completar estas comprobaciones:

1. Crear la release de archivo sin sustituir otras releases ni sus assets.
2. Subir cada candidato conservando exactamente sus bytes.
3. Descargar de nuevo los 82 destinos y cotejar tamaño, SHA-256 y CRC contra este catálogo; conservar evidencia de las comprobaciones.
4. Revisar todos los consumidores, adaptar los cinco usos conocidos en `VERSION.json` y validar las redirecciones de todas las URL originales, sin perder su acceso público.
5. Obtener la aprobación de la transición concreta antes de eliminar binarios del árbol de publicación o cambiar los enlaces activos.

El campo `planned` se conserva hasta que otra propuesta documente y verifique la transición. Este checker no cambia un destino a activo ni realiza solicitudes de red; un resultado local correcto no prueba que una release o una redirección exista.

## Reversión

En esta fase, la reversión consiste en revertir el commit preparatorio: los binarios y sus URL no han cambiado. No hay que borrar ni editar releases existentes.

Si una migración futura ya hubiera retirado archivos, su plan de reversión debe restaurar las mismas rutas y los mismos bytes del commit de procedencia, revertir la adaptación de consumidores y redirecciones, y volver a comprobar SHA-256, tamaño y CRC y la descarga pública. Se utilizarán commits nuevos de reversión, sin forzar ni reescribir el historial. Las copias de archivo verificadas se conservarán hasta comprobar la restauración.
