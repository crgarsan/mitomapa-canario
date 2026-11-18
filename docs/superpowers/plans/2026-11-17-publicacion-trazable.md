# Publicación trazable de MitoMapa Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Preparar metadatos coherentes, una entrega trazable y el catálogo previo a la migración histórica.

**Architecture:** La selección de archivos conserva el índice Git revisado y los lectores acotados de #64. Un módulo deriva documentos de VERSION.json; otro prepara una entrega externa a los ZIP; el catálogo histórico registra destinos todavía no publicados.

**Tech Stack:** Python 3.12, unittest, Node 22, GitHub Actions con acciones fijadas por SHA.

**Spec:** `docs/superpowers/specs/2026-11-17-publicacion-trazable.md`.

## Global Constraints

- Base: main b4014344450e1862bf1d441df59d824ec2714c22 y PR64 06a83fcda01c72f20b1fecd3339b3c4095c7ea77.
- Sin fusión, despliegue, modificación de secretos ni retirada de históricos.
- Web 4.10.0, ELPX 4.8.9, runtime 4.0.5; los productos no comparten necesariamente versión.
- ELPX ES/EN e históricos conservan bytes; únicamente se regeneran los ZIP actuales afectados y sus sumas.
- Ningún documento contenido en un ZIP puede incluir la huella de ese mismo ZIP.

## Review Focus

- VERSION.txt, README o version.js atrasados deben hacer fallar --check sin escribir.
- Dos preparaciones con el mismo contenido deben dar la misma entrega.
- Un commit sucio, un archivo no aprobado o una ruta insegura no puede convertirse en entrega formal.
- Los metadatos externos distinguen título anunciado, versión del adjunto e identidad descargada.
- La propuesta de archivo no cambia enlaces, secretos ni binarios existentes.

### Task 1: Metadatos y documentos

**Files:** tools/release_metadata.py, tools/update_release.py, VERSION.json, VERSION.txt, version.js, README.md, EDICIONES.md y pruebas correspondientes.

**Interfaces:** document_outputs(root, version) -> dict[str, bytes]; product_rows(root, version) -> list[dict].

- [ ] Añadir regresiones de versiones distintas, desajuste documental, idempotencia y uso con inventario sin Git.
- [ ] Confirmar fallos antes del cambio.
- [ ] Derivar documentos y comprobarlos desde update_release --check, preservando la prosa ajena al bloque generado.
- [ ] Incorporar evidencia pública de ES/EN y Mediateca, sin confundir disponibilidad con estado interno.
- [ ] Ejecutar pruebas y confirmar el cambio.

### Task 2: Catálogo histórico

**Files:** HISTORICAL_RELEASES.json, tools/historical_releases.py, tests/test_historical_releases.py, docs/ARCHIVO_HISTORICO.md.

**Interfaces:** current_archive_paths(root, version), build_catalog(...), check_catalog(...).

- [ ] Probar inventario, mutación de hash, duplicados, CRC, nombres y destinos.
- [ ] Catalogar los históricos y sus consumidores; mantener destinos como planned.
- [ ] Comprobar --check sin escrituras y confirmar el cambio.

### Task 3: Preparador de entrega y colaboración

**Files:** tools/prepare_release.py, tests/test_prepare_release.py, .github/workflows/prepare-release.yml, docs/PUBLICACIONES.md, CONTRIBUTING.md y plantillas de colaboración.

- [ ] Probar rechazo de commit sucio o incorrecto, de archivos no revisados y de entregas alteradas.
- [ ] Crear catálogo externo con commit, versiones, bytes, SHA-256 y notas; verificar la copia antes de terminar.
- [ ] Crear workflow de preparación con contents:read y sin publicación/despliegue.
- [ ] Documentar el procedimiento y preparar el texto de rectificación de Mediateca.
- [ ] Ejecutar pruebas y confirmar el cambio.

### Task 4: Integración y revisión

- [ ] Integrar sólo los archivos asignados a cada tarea y ampliar el inventario de fuentes para los documentos nuevos revisados.
- [ ] Regenerar los ZIP actuales y sumas; verificar ELPX e históricos intactos.
- [ ] Ejecutar pruebas apropiadas, cuatro --check, catálogo histórico y preparador.
- [ ] Revisar el diff de forma independiente y abrir la PR sin fusionar ni desplegar.
- [ ] Informar resultados e intervenciones externas pendientes.
