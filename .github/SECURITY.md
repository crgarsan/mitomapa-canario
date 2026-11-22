# Comunicar una posible vulnerabilidad

## Canal privado de seguridad

En la [pestaña de seguridad del repositorio](https://github.com/crgarsan/mitomapa-canario/security), seleccionen **Report a vulnerability** para abrir el formulario de informe privado. Tras revisar y completar el informe, utilicen **Submit report**. La opción **Private vulnerability reporting** se observó habilitada el 22/11/2026 en la configuración del repositorio; su disponibilidad puede cambiar.

Las cuentas con permisos de administración o seguridad pueden crear directamente un borrador de aviso. Ese flujo de mantenimiento es distinto del informe de una tercera persona; consulten la [guía oficial de GitHub](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately) para identificar el procedimiento de su perfil.

Si no aparece la opción de presentar un informe privado o no permite enviarlo, no publiquen los detalles del problema. Utilicen un medio privado que ya hayan acordado con las personas responsables del repositorio. Si no disponen de uno, pueden abrir una incidencia que solicite únicamente un contacto privado, sin describir la vulnerabilidad, su alcance ni sus pasos de reproducción. Esperen a que se confirme ese canal antes de compartir el informe. Esta política no publica un correo alternativo de seguridad.

## Información para revisar el problema

Incluyan, si es posible:

- El producto, idioma, versión y dirección o archivo afectado; añadan el commit o SHA-256 cuando lo conozcan.
- Los pasos mínimos para reproducirlo, el resultado observado y su posible impacto.
- Una demostración con datos ficticios y el navegador o entorno utilizado.

No publiquen detalles de explotación en incidencias, PR o comentarios públicos. No adjunten contraseñas, tokens, datos personales del alumnado ni archivos de seguimiento reales. Antes de aportar registros o capturas, retiren esos datos y comprueben también los nombres de archivo y los metadatos.

## Identificar la edición afectada

La web, el REA editable y la publicación de Mediateca son entregas diferenciadas. Como referencia del 22/11/2026, la web se identifica como **4.10.0**, el REA descargable del proyecto como **4.8.9** y el ELPX conservado en Mediateca como **4.8.8**. La ficha de Mediateca todavía anuncia **4.8.4**; esa etiqueta no identifica los bytes de su adjunto.

Consulten [VERSION.json](../VERSION.json) y la [matriz de ediciones](../EDICIONES.md). Indiquen también si el problema afecta a una descarga histórica o a una adaptación propia. Estas referencias identifican productos; no establecen una garantía de mantenimiento de todas las ediciones.

Un informe y una propuesta de corrección deben revisarse. La existencia de un cambio en una rama o una PR no demuestra que la web o las descargas publicadas ya incluyan la corrección.

Los errores de funcionamiento sin implicaciones de seguridad pueden comunicarse mediante las [incidencias del repositorio](https://github.com/crgarsan/mitomapa-canario/issues/new/choose). Para manejar exportaciones de seguimiento, consulten las [pautas de custodia](../docs/CUSTODIA_SEGUIMIENTO.md).
