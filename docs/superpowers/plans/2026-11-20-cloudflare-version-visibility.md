# Cloudflare version visibility recurrence implementation plan

> Agentic execution in this chat with isolated branch, RED/GREEN and independent review. Prepare a PR; do not merge or deploy.

**Goal:** tolerate the observed recurrence of exact-version 100146 beyond the old short retry sequence, while bounding attempts and wall-clock time and never repeating ambiguous writes.

**Spec:** user request in this chat: correct recurrence in automatic Cloudflare publication, with tests and bounded retries for the exact version, without merge or deployment. Base main 4afb1a0e3175bab125dc6d00bcd64129a9990bfe.

**Evidence:** run219 uploaded version bb66dcbf-0a22-4c4d-b36d-34e44bacf649, then exhausted five lookup failures about20s later. Old pauses1/2/4/8 total15s; the60s deadline was only a ceiling, not a useful visibility window. A later manual activation succeeded. This does not measure the provider's maximum propagation delay.

**Architecture:** keep Wrangler4.152.0 and the existing strict recognition of an unambiguous stderr100146 on GET of the original account/Worker/UUID, before deploymentPOST. Re-run only the identical UUID@100% command. At most9 attempts (8 retries), pauses2/4/8/16/30/30/30/30 seconds and a shared180s activation deadline including process time and sleeps. A separate successful visibilityGET would not remove Wrangler's subsequent read race. Keep upload single-use; no latest version, new upload, additional permission or fallback promotion.

## Scope and review focus

- `tools/deploy_cloudflare.py`: retry timing and sanitized budget diagnostics only; exact-path classifier, process-group termination and credentials boundaries unchanged.
- `tests/test_deploy_cloudflare.py`: real subprocess fake CLI and controlled clock; demonstrate success after90s virtual time and on final attempt, persistent failure cap, budget consumed by CLI work, timeout killing descendants, and no replay of a later ambiguousPOST.
- `DESPLIEGUE_AUTOMATICO.md`: actual bounds and failure/uncertainty semantics. Scope is activation phase, not total workflow duration.
- Current source ZIP and its sum must include the new tool/tests/docs. Keep VERSION.json versions, ELPX, other ZIPs, all media and historical packages unchanged.
- Unknown/auth/other-UUID/other-account/other-Worker failures, malformed or multiple diagnostics, POST errors and timeouts must fail without retry. Never log raw captured CLI output or credentials.
- The180s limit does not promise that Cloudflare will always make a version readable in time; exhaustion remains a visible failure. No real provider calls or deployment in regression tests.

## Steps

- [x] Verify clean main baseline and upstream pre-POST call graph.
- [x] Write failing recurrence/budget/safety tests using independent literal expectations and virtual time.
- [x] Extend the bounded policy and dynamic diagnostics; verify focused GREEN.
- [x] Independent review; fix actionable findings through regression tests.
- [x] Full Python/JavaScript suites and release checks, regenerate only candidate source ZIP, verify integrity and preserved other bytes.
- [ ] Publish branch and PR; inspect validation and CodeQL. No merge, workflow dispatch or Cloudflare activation.

**Review result:** a diagnostic issue corrected with two RED/GREEN regressions: report insufficient time for the next pause separately from an exhausted deadline. Follow-up review identified possible timing flakiness: virtual budget cases now exclude real CLI elapsed time, while the process-tree timeout case still uses the real clock. Full suite before this diagnostic correction: 370 Python tests (3 optional skips) and 37 JavaScript tests passed; rerun and release validation follow below.

**Local verification:** 370 Python tests passed (3 optional skips), 37 JavaScript tests passed, final wrapper regression suite 16/16 after deterministic-clock correction, extracted-source roundtrip 16/16. Six release validators passed in --check mode. Candidate ZIP CRC and all 440 manifest entries verified; all other packages/media and version declarations are unchanged. Independent review has no remaining finding. Clean-commit preparation check and remote CI are the final gates.
