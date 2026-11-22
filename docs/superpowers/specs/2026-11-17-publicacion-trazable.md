# Publicación trazable de MitoMapa

Fuente: informe de auditoría del 17/11/2026, propuestas 02, 03 y 08; continuación autorizada por la autoría. Se prepara una PR sobre la corrección #64, sin fusionar ni desplegar.

- `VERSION.json` identifica productos distintos: web ES/EN, ELPX ES/EN, paquetes y referencia externa de Mediateca. Se conservan las claves públicas existentes y los esquemas de progreso.
- La documentación vigente y `version.js` se derivan de esos metadatos. Los hashes de ZIP no se incluyen dentro de sus propios contenidos; el catálogo externo de cada entrega contiene todas las huellas.
- El estado declarado por un archivo y su disponibilidad pública son hechos distintos. No se modifican los ELPX por corregir la documentación de la web.
- Un preparador crea una entrega reproducible, fijada a un commit limpio, con catálogo, notas y sumas. El workflow sólo prepara un artefacto revisable y tiene permisos de lectura; no publica releases ni despliega.
- El catálogo histórico conserva las 82 identidades candidatas y sus enlaces originales. Los destinos son propuestas hasta comprobar sus copias y redirecciones. No se retiran binarios ni se reescribe el historial.
- Se documentan contribuciones, pruebas y custodia del seguimiento. La política privada de seguridad sigue en la PR #47.

Intervención externa pendiente: rectificar la ficha y el adjunto de Mediateca y autorizar posteriormente la publicación de la release y la migración histórica. La configuración de credenciales de #1 sigue pendiente.
