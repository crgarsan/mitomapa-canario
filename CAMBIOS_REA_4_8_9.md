# MitoMapa canario Objeto de Aprendizaje 4.8.9

30/10/2026. Actualización de fflate incorporado a la edición nativa vigente.

`libs/fflate/fflate.umd.js` se sustituye por la distribución UMD oficial de fflate 0.8.3, bajo licencia MIT incluida en `libs/fflate/LICENSE.txt`. El tarball npm se verifica por SHA-512; el miembro UMD, la licencia y la fuente histórica se fijan por SHA-256. El constructor rechaza cambios de esas entradas, degradaciones de versión y diferencias no autorizadas del resto de bibliotecas.

El cambio atiende GHSA-px8p-9vwx-vf98 / CVE-2026-45820: la biblioteca anterior podía no terminar al recorrer un campo ZIP64 malformado. Las pruebas aisladas y con tiempo límite reproducen ese bloqueo y comprueban su rechazo tras actualizar, además de ZIP64 legítimo y exportaciones con texto, nombres Unicode, binarios y entradas sin compresión. Una prueba de navegador usa el exportador HTTP nativo real para descargar un ELPX y comprobar su contenido.

En el recurso inspeccionado, el consumidor de fflate comprime mediante `fflate.zip`; no se ha establecido una vía ordinaria de entrada de ZIP no confiables a `unzipSync`. Esta actualización elimina la biblioteca afectada de los paquetes vigentes, sin atribuir una explotación remota demostrada a MitoMapa.

Se conservan las 34 páginas, 118 identidades de iDevice, 42 juegos, 16 MP3 y medios. La corrección de metadatos de 4.8.8 permanece. Las ediciones históricas conservan sus bytes y la biblioteca con la que se publicaron; no se presentan como actualizadas. Tampoco se modifica un editor o LMS externo.

Fuentes: [aviso](https://github.com/advisories/GHSA-px8p-9vwx-vf98) y [versión oficial 0.8.3](https://github.com/101arrowz/fflate/releases/tag/v0.8.3). Preparación en PR, sin fusión ni despliegue.
