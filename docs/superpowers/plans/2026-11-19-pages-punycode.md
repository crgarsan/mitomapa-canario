# Pages punycode implementation plan

> Agentic execution: implement and independently review in this chat. Prepare a PR; do not merge or deploy.

**Goal:** remove DEP0040 from the pinned deploy-pages process by replacing its deprecated builtin import, without suppressing warnings.

**Architecture:** keep official deploy-pages v5.0.1 at 368f82528645a54fb793d4d04e342629a3f51346. Preload a synchronous Node module resolution hook only for that workflow step, resolving exactly punycode and node:punycode through a CommonJS facade preserving named ESM exports to the unmodified MIT userland punycode 2.3.1. No installation at deployment time; retain provenance and hashes beside the vendored file.

**Spec:** user request: prepare a PR correcting the punycode warning with tests, without merging or deploying. Base main 8f1d4eec065abe5e4c987de6dc8211671ab89944.

**Alternatives:** an official fixed release would be preferred, but latest release and upstream main still point to v5.0.1. An unreleased fork/rebuilt 5.8 MB action would require maintaining the entire action dependency graph. Warning suppression would hide the symptom. The scoped import replacement preserves the reviewed action and all warnings.

## Constraints and review focus

- Keep manual deploy=true, main/repository gates, permissions, host guard, artifact reuse, TLS and content verification.
- Both require/import and both builtin spellings must resolve; all other modules and warnings must remain unchanged.
- Quote paths containing spaces in the actual workflow NODE_OPTIONS; do not inherit it into other steps.
- Check the exact upstream bundle with a clean environment and explicit network denial. Never use real credentials or call deployment APIs in tests.
- Preserve VERSION.json product versions, ELPX, media and historical packages. Refresh only the current source ZIP and related checksums as candidate outputs.
- An actual publishing job remains unverified until separately authorized after merge; a successful isolated startup is not a publication.

## Task: scoped runtime compatibility and regression proof

- [x] Write offline behavioral tests reading and executing the workflow Node options. Observe DEP0040 failures before the fix.
- [x] Add tools/pages-punycode.mjs, tools/vendor/punycode-2.3.1.js, MIT license and provenance; scope NODE_OPTIONS to deploy-pages only.
- [x] Add an integrity-checked, network-denied startup check of the immutable upstream bundle; run it under Node 24 before the artifact build in validate.
- [x] Verify RED/GREEN, unrelated warnings, Unicode cases, clean context failure and zero network attempts. Run backup, full Python/JavaScript suites and release --check tools.
- [x] Obtain independent review, refresh the candidate source archive, verify unchanged other packages, and commit.
- [ ] Publish branch and PR; inspect CI and CodeQL. No manual dispatch, merge or deployment.

## Review decisions and evidence

- Root cause: @actions/artifact 2.x includes tr46 -> external require(punycode) in the immutable upstream bundle. Official v5.0.1 is still latest; upstream main has the same pin.
- RED: default Node core emits DEP0040; the workflow preload regression failed before the change. The isolated exact-bundle control also reproduces it with zero network attempts.
- Independent review P2: direct CJS vendor mapping removed named ESM exports. Added a facade and a static named-import RED/GREEN regression for both module spellings; vendor bytes remain unchanged.
- Independent review P3: corrected the removal procedure: a future fixed control requires reviewing and updating the checker expectation in the same PR.
- Test harness correction: delimit action with inputs, so step env values are not misclassified as unknown inputs.
- A Node executable missing from the initial shell PATH was an environment limitation, resolved by using the existing Node24 runtime; the unchanged baseline then passed 21/21.
- Source package closure: a roundtrip inspection found that Pages YAML metadata and its MIT licence were omitted by the existing source selector. A synthetic source-package RED/GREEN regression now requires that reviewed fixture directory without allowing unrelated YAML.
- Final local verification before commit: 367 Python cases (364 passed, 3 optional NumPy/FFmpeg skips), 37 JavaScript cases, 28 backup cases, six release validators in --check mode, and 28 backup cases plus exact-bundle startup from the CRC-verified source ZIP extracted into a path with spaces.
