# Audit fixes implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans with the bounded file assignments below. Steps use checkbox syntax.

**Goal:** Prepare a reviewable PR upgrading fflate and fixing the four reproduced defects, without merge or deployment.

**Architecture:** Keep the current web modules and versioned storage. Add a hash-pinned native-library transformation to the deterministic ELPX builder; integrate release files only after component fixes are verified.

**Tech Stack:** Vanilla JavaScript/CSS, Python 3.12 unittest/lxml/Pillow, Node 22+, Playwright Chromium.

**Spec:** `docs/superpowers/specs/2026-10-30-audit-fixes-design.md`.

## Global Constraints

- Base main `095d10ed63065b3c65326c17940f16bac30caef9`; feature branch only; no merge/deploy.
- Web 4.9.2, ELPX 4.8.9; preserve historical package bytes and media.
- Explicit pin fflate 0.8.3 from npm official package with SHA-512 integrity, member SHA-256 and license.
- Keep active-stage criteria separate from shared primary/secondary creative content.
- Keep legitimate drawing/import/undo and two-island creative workflows; no blanket clearing of unrelated stages.
- No weakening preservation, ZIP limits, metadata sanitization, CSP, import validation or test assertions.

## Review Focus

- A no-op pointer event on an existing drawing must preserve its prepared/reviewed state.
- A real shared-primary content change must invalidate all affected primary stages, but not secondary.
- Explicit new creative choices and reset must still work after navigation preserves an existing pair.
- Enlarged text must leave modal close controls and keyboard focus visible; table-local scrolling must remain available.
- Vendor drift, malformed ZIP64 and ordinary ZIP round trips must be checked with bounded execution.

### Task 1: Creative state correctness

**Files:** Modify `scripts.js`, `aprendizaje.js`; create `tests/test_persistent_state_browser.py`.

**Interfaces:** Preserve existing storage schema and window.MitoMapaLearning APIs. Criteria handler may pass an explicit stage restriction to invalidation; shared-content callers retain broad invalidation.

- [ ] Add regressions for cross-stage criterion edits, preserved second creative island and empty/no-op drawings, including legitimate controls from Review Focus.
- [ ] Run the new tests against base and record expected failures.
- [ ] Apply minimal changes to invalidation scope, closure initialization/navigation, and actual-drawing mutation detection.
- [ ] Run the new file and existing journey/drawing/learning suites; report red and green commands.
- [ ] Review focused diff and commit only assigned files after root integration.

### Task 2: Native fflate upgrade

**Files:** Create `tools/native_fflate.py`, pinned files in `tools/vendor/`, regression tests; modify `tools/sync_current_elpx.py` and the validation workflow as needed.

**Interfaces:** `apply_fflate_upgrade(files, baseline, root)` applies only the pinned member; `verify_fflate_upgrade(files, baseline, root)` independently verifies it. Builder applies the transform and preservation exempts only the verified member/license.

- [ ] Reconcile independent source-to-sink investigation with the builder and all embedded current copies.
- [ ] Add a bounded malformed ZIP64 regression, another invalid archive class, ordinary zip/unzip and downgrade/vendor drift/preservation tests; watch old version fail.
- [ ] Verify npm tarball integrity, vendor the official 0.8.3 UMD and license, and integrate exact source/replacement hash validation.
- [ ] Confirm all other runtime/media/activity invariants and legitimate native download/export remain intact.
- [ ] Review the candidate for bypasses/regressions with a fresh read-only reviewer.

### Task 3: Enlarged text and dialogs

**Files:** Modify only relevant CSS (`styles.css`, `aprendizaje.css`, `navegacion.css`, `recorrido.css`, `itinerario.css` as needed); add `tests/test_text_resize_browser.py`.

**Interfaces:** Keep DOM identities, navigation and public controls. No global overflow hiding; constrain intrinsic sizes and wrap labels/modal headers as needed.

- [ ] Add dialog content/close/tab/focus regressions at 320x800 with font-size root 200%; use existing four reflow failures as base evidence.
- [ ] Run red tests before CSS changes.
- [ ] Implement bounded wrapping/sizing and verify desktop/390/320 and reduced motion.
- [ ] Run new and existing navigation/learning/expedition tests; inspect screenshots.

### Task 4: Release candidate and PR

**Files:** VERSION.json, new change notes, current announced labels, current ELPX and ZIPs, SHA256SUMS.txt, generated version.js; no historical binary changes.

- [ ] Set web 4.9.2 and ELPX 4.8.9; document the exact five changes and remaining scope.
- [ ] Run deterministic current ELPX/release builders locally; inspect changed members, sizes, hashes and package versions.
- [ ] Run full Python/Node/browser suite and all four --check commands; investigate any failing platform-specific keyboard test with native-select controls, preserving real keyboard coverage.
- [ ] Review the whole patch independently, resolve confirmed regressions, and confirm diff scope and latest main.
- [ ] Commit, push only the feature branch, create and attach the PR; inspect CI validation status without merging or deploying.
