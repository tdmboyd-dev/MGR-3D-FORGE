# MGR 3D FORGE

**Owner:** Money Grind Religion (MGR) / Timebeunus Boyd  
**Canonical repository:** https://github.com/tdmboyd-dev/MGR-3D-FORGE  
**Project status:** Active build. First GPU-free world-generation vertical slice implemented and tested; full production platform remains unfinished.  
**Last researched:** 2026-10-25

## Mission

Build an MGR-owned, prompt-driven 3D creation platform for **characters, editable parts, props, environments, persistent worlds, animation-ready assets, scene reconstruction, and automated quality repair**. Favor native procedural creation, verified open-weight models, and reusable assets. A paid 3D API is optional, never the core dependency.

**North star:** Describe a character or world in ordinary language; Forge plans it, creates/reuses the pieces, assembles them in a real 3D scene, checks them, repairs known defects, and exports owned, editable assets.

## Start here

### Run the working native prototype

Requires Python 3.10+ only; no GPU, packages, account, key or paid API.

```bash
python3 -m unittest discover -v
python3 -m forge.cli build --spec examples/neighborhood.json --out artifacts/example
python3 -m forge.cli build --prompt "Create 25 buildings and streets" --out artifacts/prompt-25
python3 -m forge.cli inspect artifacts/prompt-25/world.glb
```

Each build creates a real binary `world.glb` mesh and a `manifest.json` with seed, building positions, file hash, geometry counts, and quality results. This prototype can plan a **limited** count-based neighborhood prompt; it is not a general text-to-3D model. Current materials are simple PBR colors and buildings are basic massing blocks, not detailed interiors. The GLB is internally validated but has **not** been imported and rendered in Blender or a game engine here.

Code lives under `forge/`, tests under `tests/`; [implementation evidence](docs/IMPLEMENTATION-EVIDENCE.md) explains exact results and limitations.

| Read | Purpose |
|---|---|
| [WHAT-WE-HAVE.md](docs/WHAT-WE-HAVE.md) | Full plain-English inventory: what exists, what Forge will create and exactly what is missing |
| [PRODUCT-BIBLE.md](docs/PRODUCT-BIBLE.md) | Complete intended product, capabilities, MGR-native ideas, use cases and limits |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Owners, modules, data contracts, pipeline, integrations |
| [RESEARCH-REGISTER.md](research/RESEARCH-REGISTER.md) | Source-linked model/research comparisons and evidence disposition |
| [DEEP-DIVE-NATIVE-CPU.md](research/DEEP-DIVE-NATIVE-CPU.md) | 16-field native procedural research packet |
| [DEEP-DIVE-IMAGE-TO-3D.md](research/DEEP-DIVE-IMAGE-TO-3D.md) | 16-field TripoSR, TripoSG and TRELLIS.2 packets |
| [DEEP-DIVE-WORLDS-PARTS.md](research/DEEP-DIVE-WORLDS-PARTS.md) | 16-field world/parts/rig research packets |
| [HARDWARE-COST.md](research/HARDWARE-COST.md) | CPU versus GPU feasibility and total-cost framework |
| [LICENSE-RISK.md](research/LICENSE-RISK.md) | License gates, derivative rights, commercial-use caution |
| [ACCEPTANCE-PLAN.md](docs/ACCEPTANCE-PLAN.md) | Build phases, tests, benchmark protocol and definition of done |
| [BUILD-REGISTER.md](docs/BUILD-REGISTER.md) | Owned capabilities, current status, dependencies, next actions |
| [DECISIONS.md](docs/DECISIONS.md) | Locked and pending architectural decisions |
| [PROGRESS-LOG.md](docs/PROGRESS-LOG.md) | Audit trail, research updates, open issues |

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

- GitHub repository exists and was empty when this research baseline was added.
- Research baseline is preserved and a functioning CPU procedural GLB exporter, bounded prompt planner, quality checks, character-landmark validation and hashed asset registry now exist.
- The world generator is a prototype, not a full 3D engine. There is no Blender bridge, neural text/image-to-3D model, production integration, cross-engine proof or measured 10× improvement yet.
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
