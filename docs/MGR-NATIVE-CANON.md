# MGR 3D Forge — Native Creation Canon

**Owner rule (2026-10-25): Every product capability, specification, headline, status, module and documentation entry must have an MGR-native identity and purpose.** Other projects may inform private research, but they do not define our features or product limits. MGR Forge owns original source code created here, its design contracts and generated outputs, subject to third-party dependencies and user-provided asset rights.

## Locked owner execution policy — hands-off Forge workspace

**Approved operating mode:** autonomous, continuous research → design → code → build → test → visual-check → fix → re-test → document **inside an explicitly designated MGR Forge worktree and its disposable job directories**. Routine in-scope file edits, temporary generated assets, local Blender executions, repeat tests and bounded retries do not require a separate prompt at each checkpoint. The runner must preserve checkpoints, changesets, failure evidence and the ability to revert an individual job; pass/fail claims require actual receipts. Do not treat this policy as an authorization to ignore platform/tool permissions.

**Hard boundaries:** no access to secrets beyond task-scoped approved credentials; no personal files or unrelated repo changes outside authorized roots; no destructive actions to existing user assets or broad filesystem trees; no permission/authentication changes; no exposing credentials; no paid or unapproved network services; no executing unreviewed remote install scripts. Each of these requires its own appropriate authorization. Refusal/permission errors must be reported, never bypassed.

**Implementation contract:** task manifest declares workspace roots, exact action scope, tool allowlist, network policy, time/cost ceiling, expected files and rollback strategy. Generated code runs as a scoped subprocess rather than an unrestricted machine-wide agent. Within that scope, the system should proceed without recurring confirmation dialogs. Current code only implements pieces of this policy; F36 tracks the full runner.

## MGR's creation method

Every technology investigation returns to this native system:

1. **Identify universal technical principles** — continuous camera control, spatial awareness, optional local model execution, persistent world relationships.
2. **Define MGR's own creative problem** — immersive navigation, reality/invention boundaries, creation control, character continuity, resource sovereignty.
3. **Build MGR-specific capabilities** — actual editable scene geometry, MGR Spatial Eyes, MGR Model Dock, MGR World Flight, MGR world/character asset memory.
4. **Separate factual input from hypothetical output** — observed, estimated, procedural, approved, license-restricted. A generated unseen back wall is an editable proposal, not a measured truth.
5. **Preserve external origins only where necessary** for third-party rights, code/weight/dataset licensing, reproducibility and legal attribution, in `research/external-provenance/`, not in MGR product feature names.
6. **Implement an original prototype**, test contracts and negative cases, benchmark local paths, then seek external Blender/engine and owner acceptance.
7. **Track honest status** in BUILD-REGISTER and PROGRESS-LOG. No feature receives a completed label because a third-party demo looks impressive.

## MGR-owned capability language

| MGR capability | Native creative purpose | Working proof | Open acceptance |
|---|---|---|---|
| MGR World Flight | Editable, continuous world-space camera routes | `forge/cinematic.py` | Browser scrubbing and engine replay |
| MGR Spatial Eyes | Know where authored geometry is, and what occludes it | `forge/perception.py` | Detailed scene intelligence and user-facing HUD |
| MGR Beyond Imagery | Create possible structures and label invented geometry honestly | `forge/interiors.py` | Multi-reference reconstruction and owner review |
| MGR Model Dock | Choose local/commercially cleared creation engines without vendor lock-in | `forge/recipes.py`, `forge/adapters.py` | Isolated installation and actual neural models |
| MGR Character Fabric | Detachable character assets, proportions and pose continuity | `forge/character.py`, `forge/animation.py` | Owner-approved Tevin source, skinning and final rig |

## Canonical hierarchy and conflict rule

1. `docs/MGR-NATIVE-CANON.md` governs naming, ownership and interpretation.
2. `docs/PRODUCT-BIBLE.md` and `docs/ARCHITECTURE.md` govern the target design.
3. `docs/BUILD-REGISTER.md` and `docs/IMPLEMENTATION-EVIDENCE.md` govern **measured reality**. Running code and passing tests outrank optimistic prose.
4. `docs/WHAT-WE-HAVE.md` is a current snapshot; `docs/PROGRESS-LOG.md` is historical chronology, not today's status.
5. `research/` is evidence, not product ownership. `research/external-provenance/` is an isolated ledger of legally/reproducibly relevant external source references.

When two documents conflict, fix them in the same change. Never silently erase research evidence needed for licensing, nor let a reference project appear to own an MGR feature.
