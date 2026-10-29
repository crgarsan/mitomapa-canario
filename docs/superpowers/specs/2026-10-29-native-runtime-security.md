# Native metadata rendering — authorized correction

User authorization: «Procede», after triage of report (5).md, finding 1. Base f5d9864dafb351cd18e1d9dc8287352c3eec5317.

The current ELPX contains one progress-report and ten checklist components. Their XML/Yjs names and checklist configuration reach HTML interpolation. Native eXe 4.0.5 uses a same-origin author preview; upstream intentionally permits author content. This change closes the two renderers' metadata interpretation paths, not the broader question of trusting arbitrary executable projects or a hosted editor's security.

Plain page/block/type names, checklist title/subtitle, messages, points and metadata attributes must remain inert through both progress generators and interface/table construction. Checklist items and footer intentionally support HTML: preserve strong/emphasis, paragraphs/lists, links and other passive documented formatting with a pinned DOMPurify HTML allowlist; disallow executable nodes, handlers, styling and DOM-clobbering identifiers. Image URLs originating from hidden DOM links also require validation and safe CSS/attribute construction.

Use an isolated sanitizer instance without replacing a host DOMPurify global. Keep raw options/state intact; encode at the rendering sink so later .text() updates and saved state do not display escaped entities. Preserve hierarchy, order, links, evaluation, storage and PDF/PNG paths.

Apply deterministic, hash-checked transforms during the existing current-native build. Only the two named runtime members and one dependency-license member may differ beyond existing editorial changes. Do not weaken preservation of other libraries, game data, identities, scenes, map, icons or 16 recordings. Historical public archives remain unchanged.

Publish new native 4.8.8 and web/package 4.9.1 with matching attachment/header/link/version metadata. This scope does not include the twelve unrelated UX findings. Live hosted eXe configuration and unrelated native components remain outside the claim.
