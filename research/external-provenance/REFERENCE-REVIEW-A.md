# External code/license reference ledger A — 2026-10-25

These are optional architecture inspirations. Do **not** copy vendor code into Forge without per-file license checks, preserve required notices if copying, and do **not** execute unreviewed third-party install scripts.

## Scroll-World — verified upstream

- Canonical inspected repository: https://github.com/oso95/scroll-world
- Reviewed primary README: https://raw.githubusercontent.com/oso95/scroll-world/main/README.md
- License: MIT at https://raw.githubusercontent.com/oso95/scroll-world/main/LICENSE (copyright 2026 cyw; notice retention needed if incorporating code).
- What it does: builds cinematic landing-page experiences using AI-created still images, transition videos and a JavaScript scroll-to-video-timeline controller. Its source README describes optional Codex image output and provider/credit-dependent video generation. It does **not** inherently create editable navigable 3D meshes. Do not mistake a prerecorded camera video for 3D world geometry.
- MGR native decision: **F31 Native World Flight**. Derive editable camera waypoints from actual Forge 3D world coordinates; permit future wheel/scroll/controller scrubbing and target-engine export with no image/video API expense for the camera plan.
- Implemented in `forge/cinematic.py`: deterministic subject camera keyframes, positions, look-at and interpolation; output `camera_tour.json`; basic tests. **Not** a working browser scroll player or cinematic editor.
- Expected gain: editable world continuity and reusable camera path, rather than rebuilding a priced chain of unrelated videos. No measured 10x speed/quality claim.

## Pinokio — verified upstream

- Canonical inspected repository: https://github.com/pinokiocomputer/pinokio
- Read primary README: https://raw.githubusercontent.com/pinokiocomputer/pinokio/main/README.md
- License: permissive grant at https://raw.githubusercontent.com/pinokiocomputer/pinokio/main/LICENSE (notice retention needed if code is copied); individual hosted apps/models have their own licenses.
- What it does: launch/manage local AI apps through inspectable scripts, scoped environments and package managers. It is **not** itself a model that sees hidden 3D behind an image. To infer unseen geometry requires separately chosen reconstruction methods, assumptions, multiple views, depth models or neural priors.
- Risk: third-party recipes can execute arbitrary commands. Auto-installing unknown packages is unsafe. The upstream README emphasizes recipe vetting and path/venv isolation.
- MGR native decision: **F32 Forge Model Dock**. Make approved local model/provider recipes inspectable; record exact version, SHA, license, RAM/VRAM, runtime and secure source; eventually isolate installers, sandbox execution and provide human approval.
- Implemented in `forge/recipes.py`: strict recipe contract and fail-closed inspection for licenses and insufficient GPU VRAM. **No downloading, installation, sandbox, execution or model inference has been implemented.**
- Expected gain: replace paid-API hard binding with swappable locally available engines, while making safety and ownership explicit.

## Synapse — repository identity unresolved

- User supplied the word **Synapse** without owner or URL. GitHub has many unrelated repositories named Synapse, including Matrix server software, SynapseML and other products. Search did not identify a uniquely relevant 3D-world source.
- Status: **HOLD for exact upstream URL.** Do not invent functionality or reverse-engineer the wrong project. This does not block other Forge work and is not yet counted as a new native build capability.
- Candidate native opportunity if the intended repository is an AI agent-memory system: persistent world/character scene graph, object identity and learned spatial relationships (potential extension of F20). This is speculative until upstream is identified.

## Source-vs-build boundaries

1. Researching source, implementing an original inspired design, importing licensed code and verifying functionality are different statuses.
2. Model launchers and cinematic video scrubbing do not prove GPU-free photorealistic mesh reconstruction.
3. New source inspiration must pass ownership, provenance, resource budgeting, security, QA and owner-approval gates before any dynamic installation.
4. F31/F32 extend the original 30 areas to **32**; keep progress counts based on real code and tests rather than research claims.
