# Expedición del alumnado — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Aplicar la propuesta aprobada de experiencia, accesibilidad y profundidad didáctica en la web, conservando el ELPX 4.8.7.

**Architecture:** Evolución de los módulos JavaScript/CSS existentes, sin servicios nuevos. Mapa, lectura y aprendizaje se separan por responsabilidad; la coordinación de navegación, estado y publicación permanece en el recurso estático. Se conservan las claves de progreso y sus validaciones.

**Tech Stack:** HTML, CSS y JavaScript sin dependencias de ejecución nuevas; Python unittest/Playwright y Chromium para verificación; pipeline estático de versiones, GitHub Actions y Cloudflare existentes.

**Spec:** Propuesta aprobada por «Aplica las propuestas»: `/workspace/mitomapa_propuesta_20261026/Propuesta_mejora_MitoMapa_web.md` y propuesta entregada en el chat el 26/10/2026.

## Global Constraints

- Solo web. ELPX actual y todos los audios, imágenes, mapas y descargas históricas conservan exactamente sus bytes.
- Ocho islas abiertas, sin comienzo obligatorio; multinivel y anclaje curricular decidido por el profesorado.
- Cerámicas en las tarjetas del juego solo con imagen. Pintaderas decorativas. La Graciosa: caracola contemporánea, no hallazgo arqueológico.
- Conservar narración de Jesica, ilustraciones aprobadas, CC BY-SA 4.0, créditos y cautelas históricas.
- Usar ustedes; sin nuevas calificaciones, competiciones, cuentas, telemetría o publicación automática de producciones.
- Mantener guardado local, importaciones antiguas, limpieza entre alumnos, validación de datos, CSP y barreras de despliegue.
- Registrar la actualización como web 4.9.0; REA editable 4.8.7. Rehacer fuentes y ZIP de compartir actuales; conservar las versiones anteriores públicas.
- La sincronización por párrafos de las grabaciones se identificó como ampliación posterior que requiere alineación y revisión humana: no fingir sincronía ni modificar las locuciones. Se implementa ahora acceso al cuento y al fragmento textual de las pistas.
- El pilotaje real y una evaluación con usuarios de tecnologías de apoyo siguen pendientes; se actualizará el protocolo web sin afirmar resultados.

## Review Focus

1. Cambio de etapa, ruta docente y usuario sin arrastrar tareas o borradores ajenos.
2. Inicio nuevo, URL directa, atrás/adelante y reanudación del apartado correcto.
3. Teclado, móvil 320/390 y texto ampliado sin controles ocultos ni pérdida de alternativas.
4. Pistas y consultas de fuentes sin falsear revisión docente ni conceder recompensas nuevas.
5. Exportación/importación, almacenamiento no disponible y entradas no confiables, manteniendo contratos de seguridad.

## Task 1: Elección visual de islas

**Files:** `explorador.js`, `explorador.css`, `tests/test_map_choice_browser.py`.

**Interfaces:** conservar `MitoMapaExplorer.init/refresh/reset`; añadir `attachList(detailsElement)` para integrar la lista que crea navegación. Contexto existente `{routes, assets, openRoute, isEarned}`.

- [x] Escribir y ejecutar pruebas inicialmente fallidas de Mapa/Lista, ocho opciones equivalentes, foco y elección móvil.
- [x] Implementar conmutador visible, lista inicial en móvil, mapa general y acercamiento controlado preservando geografía. Enriquecer las tarjetas con título/pregunta sin cambiar las piezas.
- [x] Probar elecciones, pistas, cambios de vista y anchuras estrechas.

## Task 2: Lectura y escucha contextuales

**Files:** nuevo `lectura.js`, `lectura.css`, partes de narración y preferencias en `scripts.js`, `tests/test_reading_support_browser.py`.

**Interfaces:** `MitoMapaReading.init({readJSON,writeJSON})`, `enhance(section,route)`. Puede mover los controles de narración existentes sin duplicar reproductores; preferencias visuales independientes de etapa. Otros agentes no editan `scripts.js` durante esta tarea.

- [x] Pruebas rojas de reproductor accesible desde inicio del cuento, ajustes persistentes y cambio de ambiente manteniendo posición.
- [x] Implementar lector y controles de tamaño/espaciado/ancho/restablecer, sin inyectar estilos inline incompatibles con CSP. Preferencia de sonido conservada.
- [x] Verificar pausa, velocidad, cambio de paso, rutas y controles de texto ampliado.

## Task 3: Comprender, contrastar y crear

**Files:** nuevo `aprendizaje.js`, `aprendizaje.css`, `tests/test_learning_support_browser.py`. Integraciones en `scripts.js`/navegación a cargo del coordinador tras Task 2.

**Interfaces:** `MitoMapaLearning.init({openStory})`, `enhance(section,route)`, `feedback(routeId,kind,index,correct,explanation,hint): string`, `buildClosure(): HTMLElement`; `kind` es `source` o `quiz`. Se utilizan los datos existentes de preguntas, no se alteran sus respuestas ni la concesión de piezas.

- [x] Pruebas rojas de pistas antes de explicación, vuelta al fragmento, pregunta oral justificada y cierre creativo disponible sin ocho piezas.
- [x] Implementar ayudas graduadas, vínculo entre feedback y pregunta, pauta de fuente en el campo de evidencia existente y práctica geográfica textual alternativa al puzle.
- [x] Reutilizar `.final-project` en una vista de cierre accesible para la ruta elegida; añadir ejemplo comentado, destinatario y revisión cualitativa sin nuevas puntuaciones.
- [x] El coordinador distinguirá preguntas de investigación comprobadas de contraste revisado; no exigir texto ni autovalorar calidad.

## Task 4: Alternativas de juegos y foco

**Files:** `nombres-islas.js/css`, `piezas-islas.js/css`, nuevo `accesibilidad.css`, `tests/test_game_access_browser.py`.

- [x] Pruebas rojas de acceso al modo sin arrastrar antes del mapa y continuidad de estado.
- [x] Hacer visibles las alternativas existentes, mantener tarjetas solo imagen, mejorar estados accesibles y foco de cabecera.
- [x] Comprobar teclado, cancelación del arrastre, restauración de foco y presentación estrecha sin ampliar el alcance a rediseñar juegos.

## Task 5: Orientación, sesión y cierre integrado

**Files:** `navegacion.js/css`, `recorrido.js/css`, `itinerario.js/css`, `index.html`, integración de hooks en `scripts.js`; `tests/test_expedition_browser.py` y ajustes semánticos de pruebas existentes.

- [x] Baseline focalizado de navegación y seguridad de despliegue; registrar resultado.
- [x] Inicio visual accionable también en móvil, CTA contextual y reanudación validada por isla/apartado.
- [x] Dar prioridad a ruta acordada frente a colección, consigna visible por isla y siguiente paso hacia taller/cierre.
- [x] Catálogo por propósito con actividades abiertas primero y gran reto opcional al final; acceso a cierre creativo desde cualquier isla.
- [x] Conectar módulos, corregir etiqueta de región de ajustes y mantener todas las pestañas libres.
- [x] Probar cambios de etapa, rutas cortas, tareas externas, back/forward, ausencia de almacenamiento y nueva visita.

## Task 6: Documentación, versión y entrega

**Files:** `GUIA_DOCENTE.html`, `PROTOCOLO_PILOTAJE.html` (solo la copia web), `CAMBIOS_WEB_4_9_0.md`, `VERSION.json/txt`, `version.js`, README y metadatos de versiones actuales, fuentes/ZIP/checksums; workflow para incluir pruebas nuevas.

- [x] Actualizar documentación web para describir comportamiento real, posibilidades y límites del pilotaje; no sincronizar ni reconstruir ELPX.
- [ ] Regenerar release 4.9.0 mediante pipeline, verificar SHA del ELPX y de todos los binarios históricos/media.
- [ ] Pruebas pertinentes y suite completa una vez integrados los cambios; revisión independiente de tareas y rama completa, corregir hallazgos.
- [ ] Verificación visual en escritorio/móvil, teclado, texto ampliado, CSP y flujos de progreso.
- [ ] PR con revisión y required validate, merge exacto sin saltar protección; despliegue y prueba pública de HTTPS, recursos y descargas.

## Decisiones

- Se conserva la identidad azul mar/barro/papel con las imágenes existentes.
- No se añade una nueva plataforma de creación ni campos de datos personales. Las reflexiones pueden realizarse oralmente o en cuaderno; se aprovechan las producciones y exportaciones ya existentes.
- Los detalles reversibles de composición y texto se resuelven según la propuesta aprobada, sin solicitar de nuevo autorización.
