# Política de seguridad

## Comunicar una posible vulnerabilidad

Utiliza el [canal privado de seguridad del repositorio](https://github.com/crgarsan/mitomapa-canario/security/advisories/new) para comunicar una posible vulnerabilidad de MitoMapa canario.

Incluye, si es posible:

- La versión de la web o del REA editable y la dirección o el archivo afectado.
- Los pasos para reproducir el problema, el resultado observado y su posible impacto.
- Una demostración mínima con datos ficticios.

No publiques detalles de explotación en una incidencia pública. No adjuntes contraseñas, tokens, datos personales del alumnado ni archivos de seguimiento reales. Si necesitas aportar registros o capturas, elimina antes esos datos.

## Identificar la edición afectada

La web y el REA editable tienen versiones diferentes. La edición vigente se identifica en `VERSION.json` y en la documentación de descarga. Indica también si el problema afecta a una descarga histórica o a una adaptación propia.

Las propuestas de corrección se revisan antes de publicarse. La existencia de un cambio en una rama o en una solicitud de incorporación no significa que la web o las descargas publicadas ya incluyan esa corrección.

Los errores de funcionamiento que no tengan implicaciones de seguridad pueden comunicarse mediante las incidencias del repositorio.
