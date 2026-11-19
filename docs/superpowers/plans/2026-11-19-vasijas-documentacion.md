# Vasijas y documentación: plan de corrección

> Ejecución autorizada: modificar una rama y preparar una PR, sin fusionar ni desplegar.

**Objetivo:** recuperar los visores tras un fallo transitorio y alinear las etiquetas vigentes con VERSION.json.

**Base:** main 2ba1bbaab5ae54b671a6fcbe530b414ac278f0e8. Web 4.10.0, REA 4.8.9 y adjunto Mediateca 4.8.8 se conservan.

**Enfoque:** carga por recurso pendiente en Vasijas ES/EN, sin duplicar peticiones en curso ni opciones del selector. Las guías generan únicamente los campos marcados de versión; la prosa histórica permanece intacta. La etiqueta del manifiesto inglés se corrige sin cambiar actividades, medios ni bibliotecas.

- Verificar main, crear rama aislada y comprobar referencia de pruebas limpia.
- Escribir y observar fallar regresiones de Vasijas en ambos idiomas: catálogo/Tenerife, reapertura, concurrencia y validación.
- Implementar recuperación al reabrir; comprobar que el recurso ya cargado no se solicita de nuevo.
- Añadir regresiones del generador de guías: versiones web/REA distintas, conservación de historia y --check sin escrituras.
- Sincronizar guías y etiqueta editorial inglesa; preservar todos los demás miembros del ELPX y la hoja de revisión del ZIP.
- Regenerar únicamente paquetes vigentes afectados y sus sumas. Conservar históricos y el ELPX ES.
- Ejecutar pruebas, verificadores --check y revisión independiente; publicar sólo rama y PR.
- Completar controles privados sólo mediante acceso autenticado de lectura, sin mostrar valores de secretos. Registrar límites pendientes.

**Verificación:** regresiones RED/GREEN; pruebas Python y JavaScript; pruebas de navegador; sync_current_elpx, update_release, harden_jspdf_exports, harden_drawing_archives, historical_releases y prepare_release en modo --check. Comparar contenido y metadatos ZIP antes/después de la edición inglesa.

**Límites:** no cambiar reglas, secretos, tokens, alertas o la ficha de Mediateca. No crear releases, fusionar ni desplegar. Los paquetes de la rama son candidatos; los hechos de publicación conservan su fecha y huella anterior.
