# MGR 3D FORGE

**Owner:** Money Grind Religion (MGR) / Timebeunus Boyd  
**Canonical repository:** https://github.com/tdmboyd-dev/MGR-3D-FORGE  
**Project status:** Active build. First GPU-free world-generation vertical slice implemented and tested; full production platform remains unfinished.  
**Last researched:** 2026-10-25

## Mission

Build an MGR-owned, prompt-driven 3D creation platform for **characters, editable parts, props, environments, persistent worlds, animation-ready assets, scene reconstruction, and automated quality repair**. Favor native procedural creation, verified open-weight models, and reusable assets. A paid 3D API is optional, never the core dependency.

**North star:** Describe a character or world in ordinary language; Forge plans it, creates/reuses the pieces, assembles them in a real 3D scene, checks them, repairs known defects, and exports owned, editable assets.

## Start here

**MGR-NATIVE OWNERSHIP:** `docs/MGR-NATIVE-CANON.md` governs all product naming, documentation and capabilities. Third-party source citations are separated from MGR's original creation specification.

**OWNER-LOCKED AUTONOMY:** Build, test, repair and rerun hands-off inside an approved Forge worktree; keep personal files, secrets, destructive changes and external spend behind separate authorization. See the canon for exact boundaries. The full enforcement runner remains queued as F36.

### Run the working native prototype

Requires Python 3.10+ only; no GPU, packages, account, key or paid API.

```bash
python3 -m unittest discover -v
python3 -m forge.cli build --spec examples/neighborhood.json --out artifacts/example
python3 -m forge.cli build --prompt "Create 25 buildings and streets" --out artifacts/prompt-25
python3 -m forge.cli inspect artifacts/prompt-25/world.glb
python3 -m forge.cli verify-bundle artifacts/prompt-25
python3 -m forge.cli character --pose T --out artifacts/generic-t
python3 -m forge.cli character --pose A --out artifacts/generic-a
python3 -m forge.benchmark --out artifacts/benchmark.json
# Requires Blender installed on this machine; otherwise reports unavailable:
python3 -m forge.cli blender-verify artifacts/prompt-25/world.glb --report artifacts/blender-report.json
```

Each world build creates fourteen files: `world.glb`, `world.obj`, `world.mtl`, `world_lod1.glb`, `navigation.json`, `chunks.json`, `camera_tour.json`, `spatial_overview.json`, `interiors.glb`, `interiors.json`, `parks.glb`, `parks.json`, `preview.svg`, and `manifest.json`. The manifest has SHA-256 receipts for the other 13 outputs. `character` separately creates a **generic** T/A-pose mannequin, 16 detachable GLB parts and an editable bone-length-checked pose track. None of this is Tevin's verified likeness or a production deforming rig. Worlds include static chunks, a building-only LOD1, editable camera keyframes, simple parks and invented two-room interior hypotheses. **Five GLB imports actually passed Blender 5.2.2 on Time's Windows PC**; this does **not** yet prove rendered appearance, animation deformation or game-engine acceptance. Invented rooms are explicitly not observed reality. The SVG previews scene-plan projection, not the imported GLB. The road graph supports pathfinding and box collisions. Prompts are **limited** count-based requests; architecture remains blocky rather than cinematic final-quality.

Code lives under `forge/`, tests under `tests/`; [implementation evidence](docs/IMPLEMENTATION-EVIDENCE.md) explains exact results and limitations.

| Read | Purpose |
|---|---|
| [WHAT-WE-HAVE.md](docs/WHAT-WE-HAVE.md) | Full plain-English inventory: what exists, what Forge will create and exactly what is missing |
| [PRODUCT-BIBLE.md](docs/PRODUCT-BIBLE.md) | Complete intended product, capabilities, MGR-native ideas, use cases and limits |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Owners, modules, data contracts, pipeline, integrations |
| [RESEARCH-REGISTER.md](research/RESEARCH-REGISTER.md) | Source-linked model/research comparisons and evidence disposition |
| [MGR-NATIVE-CANON.md](docs/MGR-NATIVE-CANON.md) | Ownership, feature identity, creative sovereignty and source-of-truth precedence |
| [External provenance ledger](research/external-provenance/) | Isolated licensing and audit references only; not product definitions |
| [DEEP-DIVE-NATIVE-CPU.md](research/DEEP-DIVE-NATIVE-CPU.md) | 16-field native procedural research packet |
| [DEEP-DIVE-IMAGE-TO-3D.md](research/DEEP-DIVE-IMAGE-TO-3D.md) | 16-field TripoSR, TripoSG and TRELLIS.2 packets |
| [DEEP-DIVE-WORLDS-PARTS.md](research/DEEP-DIVE-WORLDS-PARTS.md) | 16-field world/parts/rig research packets |
| [HARDWARE-COST.md](research/HARDWARE-COST.md) | CPU versus GPU feasibility and total-cost framework |
| [LICENSE-RISK.md](research/LICENSE-RISK.md) | License gates, derivative rights, commercial-use caution |
| [ACCEPTANCE-PLAN.md](docs/ACCEPTANCE-PLAN.md) | Build phases, tests, benchmark protocol and definition of done |
| [BUILD-REGISTER.md](docs/BUILD-REGISTER.md) | Owned capabilities, current status, dependencies, next actions |
| [DECISIONS.md](docs/DECISIONS.md) | Locked and pending architectural decisions |
| [PROGRESS-LOG.md](docs/PROGRESS-LOG.md) | Audit trail, research updates, open issues |
| [Blender Windows verification](evidence/blender/windows-2026-10-25.json) | Actual Windows 5.2.2 GLB import receipts and artifact hashes |

## Rules

1. **Own the creation contracts, not the vendor.** All providers and models sit behind replaceable adapters.
2. **Separate evidence levels.** A paper, code repository, downloaded weights, smoke test, benchmark and production result are different proof levels.
3. **Generate the minimum new geometry.** Reuse owned assets or procedural methods wherever they satisfy the brief.
4. **No false GPU-free claim.** CPU creation is real; frontier neural inference may still require a GPU or rented compute.
5. **No false 10× claim.** Benchmark approved-asset cost, repair rate, geometry quality, consistency, time and editability against explicit baselines.
6. **Commercial license review before integration or distribution.** GitHub-public does not mean permissively licensed.
7. **Do not run expensive inference, download model weights, or incur API charges automatically.** Present a concrete plan and costs before spending.
8. **No secrets or user-owned reference assets in public commits.** This repository is public.
9. **No unnecessary GitHub Actions.** Prefer local verification and manual evidence.
10. **Tevin is a locked identity.** Character DNA, proportions and detachable outfits must be measured and verified.

## Current truth

- MGR Forge owns a working CPU procedural GLB exporter, bounded planner, 16-part generic T/A mannequin, scene intelligence, environment/interior meshes, geometry QA, license/cost gates and artifact receipts.
- On Windows, **64/64 tests passed**, and **five GLB imports passed Blender 5.2.2 LTS**. Reproducible evidence is preserved under `evidence/blender/`.
- Native register covers **43 capabilities**; the implementation plan is `research/MGR-CREATION-INTELLIGENCE-HOWTO.md`.
- Prior verified development wave: **85/85 tests passed on both Linux and Time's Windows PC**. F34 generated-world facts, F35 measurable PNG comparison, F36 recoverable workspace edits, F42 integrity-checked creation memory and F43 bounded repair coordination have partial implementations. The full visual intelligence, isolated code runner, advanced rig and interactive world remain open.
- Earlier wave: **94/94 tests passed on both platforms**, with cross-view identity rules, a Windows-verified build→Blender→render pipeline, and a real modular armature `.blend`. Provenance can confirm the same underlying template across poses; a silhouette by itself cannot prove character identity.
- Latest extension: **97/97 tests pass on Linux and Time's Windows PC**; modular armature verified on Windows, editable `.blend` preserved under `evidence/blender/`, and F40 offline collision-checked road traversal verified with a 120m route. Interactive game-world runtime remains open.
- Next rigging slice: **99/99 tests passing on Linux and Time's Windows PC**. The published CLI built a 16-part/11-bone weighted rig with 16 modifiers, actual keyed arm motion and two transparent pose renders (RGB MAE 0.671411); smooth production weight blending and full animation remain open. Source project and screenshots are in `evidence/blender/` with real QA receipts.
- Latest wave total: **103/103 tests on Linux and Windows**, including hardware-aware model admission so large GPU-dependent models aren't treated as runnable locally without evidence. Professional smooth weights, complete locomotion, game-engine playback and semantic vision remain open acceptance work.
- The engine remains a prototype: Blender import works for tested assets, but there is no neural text/image-to-3D model, photorealistic production scene, approved Tevin likeness, complete runtime integration or measured 10× competitor improvement yet.
- The external Creation OS / Create Loco / MGR-ONE source-of-truth mapping must be verified before integration.

## Intended future structure (long-term; current working code lives in `forge/`)

```text
apps/                 # user-facing Forge studio / job inspector (future)
packages/contracts/   # asset, scene, provider, quality, provenance types
packages/planner/     # prompt -> scene specification, resource and cost plan
packages/assets/      # owned asset registry, semantic retrieval, dedupe
packages/geometry/    # deterministic CPU procedural systems
packages/character/   # DNA locks, part separation, rig/pose validation
packages/world/       # region graph, roads, terrain, scene assembly
packages/blender/     # version-aware Blender runtime bridge
packages/models/      # isolated model adapters (licensed independently)
packages/quality/     # geometry and visual QA, repair, export validation
workers/              # optional local / rented compute runners
tests/                # deterministic contracts + golden scene tests
research/             # current source evidence and unresolved investigations
docs/                 # the source of truth
```

**This tree is a proposed layout, not files that currently exist.**
