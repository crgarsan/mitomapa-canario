# Correcciones de auditoría de MitoMapa

**Objetivo:** resolver los fallos confirmados y la terminología solicitada, publicando web 4.8.12 y ELPX 4.8.7.
**Base aprobada:** informe de auditoría del chat sobre 9780a24, con evidencias en /workspace/mitomapa_auditoria_integral_20261025.
**Arquitectura:** cambios acotados en la aplicación estática y transformaciones verificadas del proyecto nativo fijado; sin cambiar escenas ni audios ni reglas de obtención del pasaporte.

## Restricciones
- Conservar escenas, narraciones y archivos históricos; guardar la edición ELPX 4.8.6 antes de actualizar el descargable actual.
- Conservar identidades, tipos y reglas de los juegos salvo correcciones expresamente autorizadas de vocabulario.
- Mantener CC BY-SA 4.0, autorías, enfoque multinivel y condiciones separadas de terceros.
- Sustituir terminología propia indígena/indígenas por aborigen/aborígenes; no falsificar títulos bibliográficos ni URLs.
- Mantener CSP, separación de secretos y protecciones de main.

## Tareas
- [x] Web: importación validada antes de modificar estado; recuperación de preferencias inválidas; respuestas y consignas de vocabulario coherentes.
- [x] ELPX: limpiar bancos Completa, normalizar referencias de recursos y enlaces docentes, traducir salto al contenido; guardas explícitas para los cambios permitidos.
- [x] Documentación y términos: dominio principal, créditos sincronizados y retirada de residuos técnicos.
- [x] Accesibilidad y compatibilidad: cabecera con letra ampliada y redirección de valoración compatible con CSP.
- [x] Mantenimiento: comandos de verificación aplicables al inventario actual y documentación coherente.
- [ ] Edición: archivar ELPX anterior, actualizar versiones, regenerar ELPX/miniatura si procede y paquetes/huellas.
- [ ] Verificación: reproducciones rojas/verde de fallos, batería completa, recursos y archivos históricos, revisión independiente.
- [ ] Publicación: PR con validate obligatorio, integración autorizada, despliegue y comprobación pública de contenidos y descargas.

## Casos que deben cubrir las regresiones
Importar nombre no válido preserva todas las respuestas; preferencias null recuperan valores; texto literal del cuento se acepta según consigna; selectores no muestran biología ni faltas ortográficas; enlaces docentes alcanzan el documento anunciado; recursos funcionan en raíz y subcarpeta; menú usable a 320 px con letra al 200 %.
