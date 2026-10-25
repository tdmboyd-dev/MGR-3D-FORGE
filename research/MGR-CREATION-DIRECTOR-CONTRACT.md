# MGR Creation Director — original native instruction-to-geometry contract

Date: 2026-10-25. Status: specified and limited implementation; no open-ended text-to-3D foundation model.

## User intent and architecture

**Text/voice/image must feed the SAME persistent editable scene**. The initial deterministic command compiler translates bounded natural phrases into typed building operations. Browser speech can transcribe into the text field; it **does not run arbitrary Python**, and its transcription must be reviewed before execution. The Python `apply-world-edits` path converts the resulting typed JSON into actual GLB/OBJ/SVG geometry. Uploaded pictures remain **local references**; extracting geometry from their pixels is a separate researched and unverified capability.

Canonical flow: typed instruction → allowlisted parse → proposed typed geometry edit → bounds, identity and material validation → undo checkpoint → WebGL render → saved JSON → verified Python GLB export. Optional microphone → browser speech recognition → editable instruction. Optional image → local object URL/preview → bounded pixel-average → closest MGR building material; this transfers color, **not** image-derived mesh geometry.

## Research-to-build packet (16 fields)

1. **Definition:** MGR Creation Director compiles a small set of natural-language building instructions to deterministic scene edits.
2. **Production use:** quick iteration and accessibility alongside precision object controls; voice must not silently commit mutations.
3. **Standards:** Web Speech API draft for optional browser speech, W3C File API for preview file object URLs, binary glTF 2.0 export through existing audited MGR code.
4. **Research:** Browser recognition and local file object behavior; research must not be confused with a usable image-to-mesh algorithm.
5. **Implementations:** MGR `viewer/runtime.js`, `viewer/template.html`, `forge/world_editor.py`; no external runtime dependency for text commands.
6. **Models:** none installed or required for typed commands; future optional vision/ASR workers need separate benchmark and license decisions.
7. **Datasets:** test phrase corpus and adversarial commands maintained through browser regression; user photos are not collected as training data.
8. **Licensing:** original MGR code, generated geometry in owner workspace; third-party recognition services follow their browser/provider policies.
9. **Providers:** optional user-selected browser speech engine; no paid model API integration in this wave.
10. **Native alternative:** deterministic command parser and CPU geometry/material compiler, with undo and export receipts.
11. **Hardware:** text/geometry works without discrete GPU or Python runtime inside browser; real-time visualization requires WebGL2. Voice requires supported microphone/browser/service.
12. **Cost:** zero MGR API calls for typed edits; browser voice provider costs/data handling must be disclosed by the browser and cannot be assumed zero/fully local.
13. **Failures:** ambiguous phrases, invalid dimensions, occupied/colliding lots, adversarial code instructions, unsupported speech implementation, microphone denial, invalid image format, export SHA mismatch.
14. **Evaluation:** actual Chrome command execution, negative input and undo/reimport, independent GLB/OBJ validation with artifact receipts.
15. **Placement:** browser `director` sidecar writes the existing canonical world-edit JSON; the Python exporter is the geometry authority. Image references are not persisted into the 3D asset by implication.
16. **Acceptance:** prove bounded text changes, create/delete/duplicate/resize, browser persistence, downloaded JSON and Python GLB materialization. For image input, verify an actual decoded image selects a bounded material. Browser speech-engine recognition and image-to-mesh reconstruction require their own actual evidence and remain open.

## Locked safety and truth boundaries

- Text instructions are **data**, never arbitrary Python, shell, browser script, network fetch or model invocation.
- Browser audio transcription requires a deliberate click and browser permission; it may be processed remotely by the browser service. Always show a reviewable transcript before geometry changes.
- Image files are format/size gated and presented locally; no claim of semantic recognition or geometry conversion.
- New object IDs are scoped, bounded and validated. The original source world is immutable; exporting edited files requires a new destination and matching original SHA receipt.
- Scope of accepted phrases is intentionally narrow and testable. More complex prompts should be handed to a future pluggable planning worker only after exact evaluation and authorization.

## Build follow-ons

- F90: Native text command parser + browser geometry editing + Python materialization.
- F91: Collapsible sidecar, privacy-safe local reference and optional speech transcription. Audio hardware proof outstanding.
- F92: Future **true** image-conditioned reconstruct/segment/generate workflow with explicit GPU/CPU, accuracy, provenance, topology and multi-view tests. Not built.
- F93: Future spoken Python scripting needs isolated code executor, scoped permissions and consent; never equate speech recognition with unsandboxed code execution. Not built.
