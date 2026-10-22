# Seguridad y juego de piezas: plan de implementación

> **For agentic workers:** usar subagentes con archivos asignados y revisión independiente. Las integraciones, comprobaciones y publicación corresponden al agente principal.

**Objetivo:** mejorar la seguridad del mantenimiento y añadir una práctica del mapa con las piezas del pasaporte, exclusivamente en la web.

**Arquitectura:** juego JavaScript aislado con interfaz mount/reset, ruta propia dentro de Juegos y alternativas al arrastre. El ELPX nativo y la entrega documental 4.8.4 se mantienen sin cambios. La publicación web 4.8.5 identifica separadamente la edición nativa 4.8.4.

**Tecnologías:** HTML, CSS y JavaScript sin dependencias nuevas de navegador; Python y Playwright para verificación; Wrangler fijado por lockfile para Cloudflare.

**Especificación:** petición del usuario del 22/10/2026: revisar avisos GitHub/Cloudflare sin comprometer funcionamiento; ampliar ligeramente cerámicas del mapa; añadir juego de asociación de piezas a islas, como el de nombres y solo en web.

## Restricciones

- Mantener geografía, ocho imágenes aprobadas, progreso y almacenamiento del pasaporte.
- Siete vasijas y caracola contemporánea de La Graciosa, sin atribuirles autenticidad arqueológica.
- No cambiar el ELPX d9969e284f1d473f1df8cf780f9551d539121e966b1ed75a5e2bd63fc3e4be49 ni descargas históricas.
- No añadir CAPTCHA sin un envío de servidor que lo justifique ni modificar MFA sin intervención del titular y su dispositivo.
- No mezclar un PR antiguo conflictivo y sin verificaciones del head con producción.

## Focos de revisión

- Los nombres de archivo y textos alternativos no deben revelar respuestas antes de practicar.
- La referencia y los reintentos no modifican el pasaporte ni almacenan datos personales.
- Navegar, importar y reiniciar cancelan arrastres y evitan estados residuales.
- La Graciosa y Lanzarote permanecen seleccionables sin solapamientos a 320–1280 px.
- Los cambios de mantenimiento conservan aislamiento de secretos, permisos mínimos y despliegue exclusivo desde main.

## Trabajo

- [x] Juego: prueba inicial de pantalla ausente; implementar piezas-islas.js/.css, integración index/navegación/scripts y pruebas de arrastre, toque, teclado, referencia y reinicio.
- [x] Mapa: medir imágenes y objetivos antes/después; ampliar solo explorador.js/.css y comprobar islas próximas y bordes a 320, 375, 768 y 1280 px.
- [x] Seguridad: fijar diff y head de PR 1 y contrastar sus propuestas con main y ajustes accesibles; revisar avisos de cuenta y límites de acceso.
- [x] Dependencias: conservar auditoría previa; actualizar Wrangler y lockfile si corrige avisos verificados, comprobar instalación, auditoría y dry-run sin credenciales.
- [x] Mantenimiento: configurar propuestas mensuales de Dependabot sin fusión automática; documentar secretos en production y MFA, sin afirmar cambios de cuenta no verificados.
- [x] Versionado: probar publicación web 4.8.5 con nativo 4.8.4; preparar nuevos ZIP de fuentes/documentación sin reemplazar anteriores.
- [x] Verificación: suites relevantes y navegadores; revisar diff independiente, hashes del ELPX e históricos, inventario y tamaño de archivos públicos.
- [ ] Publicación: PR propio con checks correctos, integración y comprobación de la web pública, cabeceras y descarga nativa sin cambios.
