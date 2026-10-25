# External evidence ledger — MGR Motion Truth & Reality Dynamics (S06)

**Date inspected:** 2026-10-25. This ledger records external factual provenance separately from the MGR-native source of truth. **Inspection depth:** public official documentation, upstream repository README and published license file overviews; no dependency checked out, installed, executed, source-audited end-to-end or benchmarked in this packet. Claims about integrations are proposed until separately tested.

| Primary source | URL | Inspected evidence / adopted engineering lesson | Rights and verification status |
|---|---|---|---|
| Blender manual — rigid bodies | https://docs.blender.org/manual/en/latest/physics/rigid_body/introduction.html | Standard rigid body behavior and scene workflow; use as reference for Blender adapter | Manual inspected; solver code/executable not inspected here |
| Blender manual — collision margin | https://docs.blender.org/manual/en/latest/physics/rigid_body/properties/collisions.html | Collision shape/margin settings influence contacts and stability | Manual only; chosen scene setup needs replay tests |
| Blender manual — rigid body world | https://docs.blender.org/manual/en/latest/physics/rigid_body/world.html | Solver/world options influence stack stability/contact quality | Manual only |
| Blender manual — cloth caching | https://docs.blender.org/manual/en/latest/physics/cloth/settings/cache.html | Bake/rebake and edited geometry can invalidate cached simulation | Manual only; direct cache mutation test pending |
| Blender manual — fluid introduction | https://docs.blender.org/manual/en/latest/physics/fluid/introduction.html | Domain/flow/caching design needed for liquid and gas | Manual only; precise solver implementation not source-audited |
| Blender manual — fluid domains | https://docs.blender.org/manual/en/latest/physics/fluid/type/domain/settings.html | Liquid vs gas distinction; respect domain/boundary | Manual only |
| Blender manual — adaptive gas domain | https://docs.blender.org/manual/en/latest/physics/fluid/type/domain/gas/adaptive_domain.html | Domain optimization can avoid empty voxels | Manual only; runtime effect requires benchmark |
| Blender manual — liquid mesh | https://docs.blender.org/manual/en/latest/physics/fluid/type/domain/liquid/mesh.html | Simulation data and rendered liquid surface are distinct | Manual only |
| Blender developer cache design | https://developer.blender.org/docs/features/nodes/proposals/caching/ | Sequential dependencies, limitations of simulation caching/geometry changes | **Proposal**, not implemented feature contract; do not claim shipped |
| Bullet Physics SDK | https://github.com/bulletphysics/bullet3 | Rigid body/collision and multibody SDK; compare game/VR adapter | README inspection, no runtime benchmark |
| Bullet license | https://github.com/bulletphysics/bullet3/blob/master/LICENSE.txt | zlib-style core, exceptions for Extras and third-party material | Verify target commit and all included folders before vendoring |
| Jolt Physics SDK | https://github.com/jrouwe/JoltPhysics | Multicore C++ rigid body engine, MIT license | README/license claims; pinned revision/build and notices pending |
| Jolt JS bridge | https://github.com/jrouwe/JoltPhysics.js | WASM/JS wrapper candidate for previews and browser scene physics | MIT per upstream README; binary provenance/version/perf must be tested |
| NVIDIA PhysX repository | https://github.com/NVIDIA-Omniverse/PhysX | Real-time CPU/GPU physics and interfaces | Root license metadata BSD-3-Clause; nested component terms vary—do not assume one license across tree |
| PhysX root license | https://github.com/NVIDIA-Omniverse/PhysX/blob/main/LICENSE.md | BSD-3-Clause notice text | Distinguish from nested SDK notices, driver/GPU binaries and dependencies |
| PhysX official documentation | https://nvidia-omniverse.github.io/PhysX/physx/5.6.0/index.html | PhysX use as real-time reference and USD Physics connection | Version-specific docs; exact current source/binaries unverified |
| Taichi project | https://github.com/taichi-dev/taichi | Python-friendly numerical kernels for custom solvers, not turnkey physics studio | Apache-2.0 per upstream project; compiled dependency/build review pending |
| OpenUSD Physics schema | https://openusd.org/dev/api/usd_physics_page_front.html | Rigid bodies, colliders and constraints as interchange schema | Official docs only; schema exchange ≠ same numerical dynamics |
| OpenUSD collision API | https://openusd.org/dev/api/class_usd_physics_collision_a_p_i.html | Collider can be on rigid-body child or static object | Docs only; round-trip test pending |
| OpenUSD rigid body examples | https://openusd.org/release/wp_rigid_body_physics.html | Stage units/timecodes and physics schema sample | Docs only; asset right and implementation not imported |

## Evidence grading

**Confirmed from inspected public specifications:** collision settings and margins matter; a simulation depends on state, constraints and time; Blender provides cloth/fluid/rigid workflows and bakes; USD schema represents physics semantics; Jolt/Bullet published permissive core licenses. **Inference requiring tests:** comparative runtime advantage on Time's PC, frame-perfect cross-engine replay, energy stability of a specific solver, correct production-grade cloth collision on Tevin, fluid conservation thresholds, and how much GPU will help.

## License gate before native packaging

1. Pin a specific commit/release of each dependency and record copyright/license file tree and third-party terms.
2. Use external solvers via documented adapters, never silently copy or relabel their copyrighted source. Keep MGR-owned experience, manifests, validation rules and inventions native; retain required acknowledgments for redistributed dependencies.
3. Keep GPL Blender executable/process separation and outputs' underlying input-asset rights review distinct from embedding/relinking its code.
4. Verify specific PhysX SDK submodule/binary terms separately; conflict between root BSD and SDK nested statements means **not approved** as one blanket license.
5. Review scenes/textures/capture data independently, even if the solver library is open-source.

## Required empirical follow-up

- Single approved Blender scene in background mode: 120-frame gravity fall, contact, cloth-to-rig and liquid splash; receipts must include version/build, `bpy` settings, image outputs, cache paths, frame-state data and memory/time.
- Identical known rigid fixtures through Jolt/Bullet with toleranced results; verify no tunneling, negative mass, NaN or stale collider caches.
- Quantitative solver metrics separated from visual rating; do not mark pass because a render looks attractive.
- Full source reading of solver entry points and numerical conservation/stability limitations before an MGR-specific reimplementation.
