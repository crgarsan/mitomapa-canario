# Learner retention implementation plan

> **For agentic workers:** Execute this bounded change inline with test-driven development, then request an independent branch review.

**Goal:** Caducar el trabajo local a los 15 días sin perder los ajustes generales.

**Architecture:** Un guardián compartido de almacenamiento comprueba el plazo antes de las lecturas y rota la generación existente. Los controladores ES/EN lo consultan antes de guardar, exportar o imprimir y al volver a la pestaña.

**Tech Stack:** JavaScript sin dependencias nuevas; node:test y Playwright/unittest.

**Spec:** `docs/superpowers/specs/2026-11-20-learner-retention-design.md`

## Global Constraints

- 15 * 24 * 60 * 60 * 1000 milisegundos; no renovación por visita.
- Ambas lenguas comparten datos y plazo. Importaciones sin cambio de esquema.
- Conservar lectura/accesibilidad, idioma y preferencias no identificativas.
- Sin modificación de ELPX, descargas históricas, alojamiento o credenciales.
- Sin fusión ni despliegue.

## Review Focus

- El primer arranque no debe mostrar nombre ni trabajo caducado.
- Una pestaña antigua no puede resucitar datos al escribir, exportar o imprimir.
- Un cambio concurrente de generación no debe borrarse como si fuera antiguo.
- Una cuota agotada o acceso bloqueado no debe producir bucles ni promesas de borrado.
- Las copias importadas comienzan un plazo local nuevo; una importación rechazada conserva el anterior.

## Task 1: Caducidad y aislamiento

**Files:** `learner-retention.js`, `scripts.js`, `scripts-en.js`, `index.html`, `index-en.html`, `tests/learner-retention.test.js`, `tests/test_learner_session_browser.py`.

- [x] Añadir y ejecutar regresiones que fallen con el código actual.
- [x] Implementar el guardián compartido y la integración con generaciones, reinicio e importación.
- [x] Comprobar frontera exacta, migración, fallos de almacenamiento y concurrencia en ambas lenguas.

## Task 2: Avisos, documentación y entrega

**Files:** avisos ES/EN, `SEGURIDAD_Y_PRIVACIDAD.txt`, guías vigentes, ZIP de fuentes y manifiesto.

- [x] Sincronizar los avisos con el comportamiento comprobado.
- [x] Regenerar sólo los paquetes vigentes exigidos por el repositorio y ejecutar sus modos `--check`.
- [x] Ejecutar pruebas JS/Python/navegador, revisar el diff de forma independiente y preparar la PR sin fusionar ni desplegar.

## Resultado de verificación

47 pruebas JS correctas; 370 pruebas Python sin fallos (3 controles opcionales de audio omitidos por falta de NumPy/FFmpeg); 68 métodos de navegador correctos: 36 de persistencia/sesión y 32 de dibujo, experiencia, ruta y texto ampliado. Seis herramientas `--check` correctas. Revisión independiente sin hallazgos materiales pendientes. ELPX español e inglés idénticos al commit base.
