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
python3 -m forge.cli studio-proof --out artifacts/studio-proof.json
python3 -m forge.cli compose-scene --layers examples/layered-scene.json --out artifacts/composed-scene.json
python3 -m forge.cli blender-studio-witness --blend artifacts/studio-scene.blend --image artifacts/studio-scene.png --report artifacts/studio-scene.json
python3 -m forge.cli verify-bundle artifacts/prompt-25
python3 -m forge.cli character --pose T --out artifacts/generic-t
python3 -m forge.cli character --pose A --out artifacts/generic-a
python3 -m forge.benchmark --out artifacts/benchmark.json
# Requires Blender installed on this machine; otherwise reports unavailable:
python3 -m forge.cli blender-verify artifacts/prompt-25/world.glb --report artifacts/blender-report.json
```

Each world build currently creates **16 files**, including `world.glb`, `world.obj`, `world.mtl`, `world_lod1.glb`, `navigation.json`, `chunks.json`, `camera_tour.json`, `lighting.json`, `spatial_overview.json`, `scene_facts.json`, `interiors.glb`, `interiors.json`, `parks.glb`, `parks.json`, `preview.svg`, and `manifest.json`. The manifest holds SHA-256 receipts for the other 15 outputs. `character` separately creates a **generic** T/A mannequin, **20 detachable GLB parts** (including trouser legs and mixed-weight elbow sleeves), an editable pose track and `wardrobe.json`. None of this is Tevin's verified likeness or a production deforming rig. Windows Blender 5.2.2 now verifies the 20-part, 11-bone skin, 48 mixed-weight sleeve vertices, PBR material parameters and an actual 3-shot CPU Cycles rendered `.blend` scene. See `evidence/blender/windows-wave5-*.json`. Invented rooms are explicitly not observed reality. The road graph supports pathfinding and box collisions. Prompts remain **limited** count-based requests; art direction and geometry remain deliberately blocky prototypes.

### Larger-wave hands-on Blender commands

```bash
python3 -m forge.cli character --pose T --out artifacts/anonymous-model
python3 -m forge.cli blender-rig artifacts/anonymous-model --skin --blend artifacts/model.blend --report artifacts/rig.json
python3 -m forge.cli blender-pose-audit artifacts/model.blend --report artifacts/pose.json
python3 -m forge.cli blender-material-audit artifacts/prompt-25/world.glb --report artifacts/materials.json
python3 -m forge.cli blender-cinematic artifacts/prompt-25/world.glb --tour artifacts/prompt-25/camera_tour.json --mood golden-hour --blend artifacts/world-scene.blend --image artifacts/world-preview.png --report artifacts/cinematic.json
```

The Blender executable must be available on the system or supplied using `--binary`. All commands are actual external-tool operations, not mock proofs.

Code lives under `forge/`, tests under `tests/`; [implementation evidence](docs/IMPLEMENTATION-EVIDENCE.md) explains exact results and limitations.

| Read | Purpose |
|---|---|
| [WHAT-WE-HAVE.md](docs/WHAT-WE-HAVE.md) | Full plain-English inventory: what exists, what Forge will create and exactly what is missing |
| [PRODUCT-BIBLE.md](docs/PRODUCT-BIBLE.md) | Complete intended product, capabilities, MGR-native ideas, use cases and limits |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Owners, modules, data contracts, pipeline, integrations |
| [RESEARCH-REGISTER.md](research/RESEARCH-REGISTER.md) | Source-linked model/research comparisons and evidence disposition |
| [Open systems research queue](research/OPEN-SYSTEMS-RESEARCH-QUEUE.md) | 24 additional open engine, physics, world and AI research branches |
| [Open systems rights ledger](research/external-provenance/OPEN-SYSTEMS-SOURCES.md) | Official sources and rights separated from native product canon |
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

- **Current expanded local wave: 187/187 Python tests PASS on Linux; last published Windows wave: 175/175 PASS.** Blender 5.2.2 accepted the 20-piece mannequin with 48 two-bone elbow sleeve vertices, 11-bone pose audit and imported PBR materials. It saved an editable three-camera CPU Cycles scene with real cut markers and a second shot whose camera moved **7.21726m** between frames 49 and 96. Four frames proved moving-shot RGB MAE **5.98669**. Later Windows Cycles render proofs established native energy portal phase motion, Fog Glow, an illuminated witness, **uniform plus procedural-cloud volumetric scattering** and an independently executed MGR FX Judge with **22.37957/255** matched-image RGB MAE. Native tests now add oriented stereo triangulation, mesh-edge audit, sampled kinematics, camera-distance chunk planning, and **ten synthetic studio-quality CPU test contracts**. A new actual Blender studio witness script has code/CLI tests, but its Windows scene/render receipt is still pending. Earlier Windows spatial proof reconstructs `(0,1,4)` meters with zero reported reprojection errors in a controlled fixture. These remain controlled prototypes; photoreal full VFX, real-world Tevin visual approval and live game streaming remain open.

- MGR Forge owns a working CPU procedural GLB exporter, bounded planner, 20-part generic T/A mannequin, scene intelligence, environment/interior meshes, geometry QA, license/cost gates and artifact receipts.
- On Windows, **64/64 tests passed**, and **five GLB imports passed Blender 5.2.2 LTS**. Reproducible evidence is preserved under `evidence/blender/`.
- Native register now covers **86 capabilities**, including director/camera/motion F44–F50, fantasy/VFX F51–F67, reality-to-space F68–F71, ten studio-quality CPU contracts F72–F81 and layered-scene/independent runtime follow-ons F82–F86. All **20 cross-disciplinary research packets and 20 source ledgers** are under `research/chapters/` and `research/external-provenance/`; the owner's **24 industry/lab/engine source families** have 24 scoped chapters; **24 additional open-systems research branches** are also queued. None of these is a claim of exhaustive source mastery or production-complete parity.
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
