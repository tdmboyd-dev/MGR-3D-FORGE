# Decision Record

2026-10-25 baseline. Pending items are not owner-approved.

| ID | Decision | State | Reason |
|---|---|---|---|
| D-001 | Canonical research/project repo is tdmboyd-dev/MGR-3D-FORGE | LOCKED (owner) | User explicitly designated |
| D-002 | MGR-native creation platform, no Tripo/Hyper3D hard dependency | DIRECTION (owner intent) | Full ownership and cost control |
| D-003 | Prefer asset reuse and procedural CPU before generative inference | PROPOSED | Efficiency, determinism and cost |
| D-004 | Use Blender as editable creation/QA tool; inspect installed version | PROPOSED | Mature geometry, rigging, scripting, export |
| D-005 | Model adapters may be open-weight, local, rented or commercial | PROPOSED | Replacement and fallback |
| D-006 | Character identity and world continuity are versioned and locked | PROPOSED | Tevin consistency |
| D-007 | Existing Creation OS / Create Loco integration owner | PENDING REPO AUDIT | Do not assume source-of-truth |
| D-008 | Target game engine and file contract | PENDING | Unity/Godot/Unreal/web needs differ |
| D-009 | Hardware execution path | PENDING HARDWARE INVENTORY | GPU/CPU capabilities unknown |
| D-010 | Tencent licensed components in commercial MGR product | BLOCKED ON LICENSE REVIEW | Public weights != unrestricted license |
| D-011 | Full foundational model training | NOT AUTHORIZED / DEFER | First prove native pipeline |
| D-012 | Download weights, buy compute, connect accounts | REQUIRES PLAN/APPROVAL | Real spend and resource changes |
| D-013 | Default performance acceptance targets | PENDING BENCHMARK | No fabricated metrics |
| D-014 | Store owner-supplied Tevin files in public repo | REJECTED | Privacy/rights risk |
| D-015 | No automatic intensive GitHub Actions | LOCKED PREFERENCE | Owner controls CI cost |

## Architecture alternatives

- **Monolithic text->mesh foundation model:** lower pipeline complexity after training, but large training/inference burden and harder to enforce identity, parts and editability. STUDY.
- **Procedure-only:** cheap, deterministic, best for roads/buildings/terrain; weak for stylized organic novelty. ADOPT for structured environments.
- **Open-model-only:** powerful details; hardware, weight-license and consistency concerns. ADAPT behind interface.
- **Hybrid semantic director + procedural + asset memory + optional model:** preferred hypothesis. MGR-NATIVE, to be benchmarked.

## Non-negotiable truth

Research sourced != end-to-end code inspection != integrated != tested. No project-wide completion percentage is justified yet.
