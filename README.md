# MGR 3D FORGE

**Owner:** Money Grind Religion (MGR) / Timebeunus Boyd  
**Canonical repository:** https://github.com/tdmboyd-dev/MGR-3D-FORGE  
**Project status:** Research and architecture specification; implementation has **not** begun.  
**Last researched:** 2026-10-25

## Mission

Build an MGR-owned, prompt-driven 3D creation platform for **characters, editable parts, props, environments, persistent worlds, animation-ready assets, scene reconstruction, and automated quality repair**. Favor native procedural creation, verified open-weight models, and reusable assets. A paid 3D API is optional, never the core dependency.

**North star:** Describe a character or world in ordinary language; Forge plans it, creates/reuses the pieces, assembles them in a real 3D scene, checks them, repairs known defects, and exports owned, editable assets.

## Start here

| Read | Purpose |
|---|---|
| [PRODUCT-BIBLE.md](docs/PRODUCT-BIBLE.md) | Complete intended product, capabilities, MGR-native ideas, use cases and limits |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Owners, modules, data contracts, pipeline, integrations |
| [RESEARCH-REGISTER.md](research/RESEARCH-REGISTER.md) | Source-linked model/research comparisons and evidence disposition |
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
- This commit records the vision, candidate research, decisions, scope, risks, and executable acceptance plan.
- No 3D engine, Blender bridge, generated model, production integration, hardware benchmark or 10× improvement is claimed complete.
- The external Creation OS / Create Loco / MGR-ONE source-of-truth mapping must be verified before integration.

## Intended future structure

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
