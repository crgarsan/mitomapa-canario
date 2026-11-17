# REA editable 4.8.9 · 02/11/2026

Se actualiza la biblioteca incorporada fflate de 0.8.2 a 0.8.3, con versión, integridad npm, SHA-256 y licencia MIT fijadas. Atiende GHSA-px8p-9vwx-vf98, relacionado con la lectura de ZIP64 malformados en unzipSync.

El consumidor del proyecto usa fflate.zip para exportar el editable. No se ha establecido una entrada ordinaria de ZIP no confiables a unzipSync en este recurso. La actualización de la dependencia no implica que se haya demostrado explotación de la web.

Se reconstruye desde la fuente nativa fijada, conservando actividades, seguimiento, cuentos, grabaciones e ilustraciones. Cambian la dependencia, su licencia/inventario y los metadatos de la edición vigente. Las entregas históricas y los aliases históricos conservan sus bytes; no se presentan como actualizados. Un editor o LMS externo conserva su propia versión y configuración.

Fuentes primarias: [aviso GHSA](https://github.com/advisories/GHSA-px8p-9vwx-vf98), [corrección upstream](https://github.com/101arrowz/fflate/commit/e6d5e6e1076892f72770ac732d83c81da9f3316e).
