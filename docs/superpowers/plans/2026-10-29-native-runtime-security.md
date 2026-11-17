# Native metadata rendering Implementation Plan

> Execute inline with superpowers:executing-plans; use the required independent investigation and one final bypass/regression review from codex-security:fix-finding.

**Goal:** Make metadata inert in the two affected native renderers while preserving legitimate formatting and activities.

**Architecture:** Hash-checked runtime transforms in the native build; a private pinned sanitizer instance and context-aware text/attribute/URL helpers; no global editor or web behavior change.

**Tech Stack:** Python/lxml/ZIP, native JavaScript/jQuery, DOMPurify 3.4.17, Playwright/Chromium.

**Spec:** docs/superpowers/specs/2026-10-29-native-runtime-security.md

## Global Constraints

- Web 4.9.1; ELPX 4.8.8; eXe 4.0.5 compatibility; own materials CC BY-SA 4.0 and dependency licenses retained.
- 34 pages, 118 native identities, 42 native games and 16 audio files preserved.
- Two exact runtime exceptions plus license; historical packages and all media byte-identical.
- Plain metadata must not create active DOM; intended checklist strong/link formatting remains.
- No accounts, telemetry, changes to learner data schemas or hosted editor administration.

## Review Focus

- Both XML and Yjs/search progress generators, including child pages, attribute breakouts, counters and empty-state messages.
- Checklist image URLs taken from hidden DOM rather than JSON.
- Encoded and malformed active HTML, SVG/MathML, dangerous protocols and style/ID clobbering in rich fields.
- Legitimate accents, literal angle brackets, strong/emphasis, footer links and interactive saved state.
- Rebuilt artifact and current ZIP copies must contain the exact hardened bytes; future unrecognized sources fail closed.

### Task 1: Reproduce and pin renderer behavior

Files: tests/test_native_runtime_security_browser.py; tests/test_native_runtime_security.py.

- [x] Use actual bundled pages/runtimes, isolated same-origin preview matching supported sandbox attributes, harmless sentinel and blocked external network.
- [x] Observe failing no-execution tests for metadata titles, both generators, checklist plain/rich fields and URL/attribute siblings.
- [x] Observe legitimate controls: 16 strong tokens, links, hierarchy, checklist interactions/storage and original media.

### Task 2: Harden current native build

Files: tools/native_runtime_security.py; tools/vendor/dompurify-3.4.17.min.js and license; tools/sync_current_elpx.py; tests/test_sync_current_elpx.py.

- [x] Verify package integrity and retain license. Implement exact source transforms and rendering helpers against the pinned sources.
- [x] Validate text at sinks, rich fields by allowlist, image URL CSS and DOM attributes; preserve raw state.
- [x] Permit only exact reproducible exceptions in preservation. Reject unrecognized source/runtime changes.
- [x] Run syntax, focused malicious/legitimate tests and nearest native/PDF regressions.

### Task 3: Review, package and publish

Files: VERSION.json/txt; version.js; current download metadata/headers/credits; release notes/README; workflow new checks; current ELPX/ZIP/checksums.

- [x] Update current native/web identities and disclosure scope; regenerate using existing pipeline, keeping historical files intact.
- [x] Run applicable full checks, one fresh bypass/regression review, address confirmed issues in scope and verify final diff.
- [ ] PR, required exact-head validation, protected merge, automatic deployment and public artifact/HTTPS checks. Preserve explicit limits about hosted editor and historical copies.
