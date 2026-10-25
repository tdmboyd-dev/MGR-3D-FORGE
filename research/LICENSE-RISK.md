# Licensing, Rights, and Supply-Chain Gates

Research-only assessment dated 2026-10-25; NOT legal advice or commercial authorization.

## Central warning

**Public code and downloadable model weights are not necessarily open-source in the OSI/permissive commercial sense.** Separate code, weights, datasets, sample artwork, dependencies, output rights and derivative-model rights. A license that permits local experimentation may restrict commercial deployment, territories, user-count thresholds or distillation.

## Candidate dispositions

| Component | Preliminary source terms | Action before commercial MGR integration |
|---|---|---|
| Blender | GPL ecosystem with add-on/API distinctions | Check distribution and linked module obligations for packaging |
| TripoSR | Project says MIT for code and weights | Verify model-card, dependencies and sample input rights |
| TripoSG | GitHub MIT | Verify checkpoint and dependencies, attribution |
| TRELLIS.2 | MIT code/model, but nvdiffrast/nvdiffrec separate terms | Review each dependency |
| Stable Fast 3D / SPAR3D | Stability community license | Read current model terms and revenue conditions |
| Hunyuan3D-2.1 | Tencent source carries non-commercial license notice | Treat commercial use as BLOCKED pending exact terms/permission |
| Hunyuan3D-Part | Tencent community license and derivative-model clauses | Separate approval gate and license audit |
| HY-World 2.0 | Tencent HY-WORLD community license with additional commercial terms | Separate approval gate, territory/MAU/distillation review |
| Tripo/Hyper3D API outputs | Contract/provider terms | Check commercial rights, privacy, training retention, attribution, API vs studio separation |
| Research datasets | Varied and often more restrictive than code | No dataset training without dataset-by-dataset rights |
| User-owned Tevin refs | User-provided, may contain third-party art | Keep private, document origin and approved use |

## High-risk clauses to verify literally

- Geographic restrictions and license applicability.
- Required authorization at certain business scale.
- Hosted service vs downloadable product distribution.
- Required attribution/NOTICE for derivative products.
- Training or distillation from model outputs, intermediate representations or weights.
- Commercial rights to generated outputs versus rights to redistribute weights.
- Third-party dependencies and example images.
- Safety use restrictions and policy changes with model revisions.

## Primary licenses

- https://github.com/Tencent-Hunyuan/HY-World-2.0/blob/main/License.txt
- https://github.com/Tencent-Hunyuan/Hunyuan3D-Part/blob/main/LICENSE
- https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1
- https://github.com/VAST-AI-Research/TripoSR/blob/main/LICENSE
- https://github.com/VAST-AI-Research/TripoSG/blob/main/LICENSE
- https://github.com/microsoft/TRELLIS.2/blob/main/LICENSE

## Release gate

Commercial MGR build can only mark a third-party model ADOPT after an evidence receipt includes exact commit, model-card revision, downloaded weight hash, code license, weight license, all nontrivial dependencies, intended usage/territory/users, signed decision and notice obligations. Until then, vendor candidate remains isolated research.
