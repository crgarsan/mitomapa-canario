# mitomapa-canario
Recurso educativo abierto sobre mitos, leyendas y patrimonio canario para Primaria y Secundaria

## Narraciones de la web 4.4.0

Los ocho cuentos tienen grabación de Jesica Fortes Regalado y una alternativa
con entrada sonora suave, identificada como recreación. El registro público
es `narraciones.js`; la procedencia y las medidas están en
`AUDIO_ORIGENES.json`, y la atribución en `AUDIO_CREDITOS.html`.

Para preparar de nuevo los MP3 se necesitan los WAV originales, Python3,
NumPy y FFmpeg con libmp3lame. Usa `AUDIO_SELECCION.json` y ejecuta:

```sh
python3 tools/prepare_narrations.py --input-dir /ruta/a/los/WAV --selection AUDIO_SELECCION.json --output-dir assets/audio --report /tmp/informe-audio.json
python3 tools/update_release.py
python3 tools/prepare_deploy.py
```

El ELPX mantiene su edición 4.0.2; las grabaciones nuevas están en la web y
en el ZIP de fuentes 4.4.0. Los WAV originales no se incluyen en ese ZIP.
