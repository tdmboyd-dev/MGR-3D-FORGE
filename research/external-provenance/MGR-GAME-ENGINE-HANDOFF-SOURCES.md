# F98 — External format evidence only (not MGR-native feature ownership)

Inspected 2026-10-25. This document records source/format evidence; MGR Forge's authored export contract lives in `forge/engine_handoff.py`.

| Source | Exact relevant finding | Caveat | Disposition |
|---|---|---|---|
| Godot stable docs, [available 3D formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html) | Binary glTF (`.glb`) is supported for import and will be processed as a project asset | Source acceptance in a Godot 4 runtime remains required | ADAPT |
| Godot API, [BoxShape3D](https://docs.godotengine.org/en/stable/classes/class_boxshape3d.html) | Box shape size is the width/height/depth used by `CollisionShape3D` | Axis, scale and collision must be tested in engine | ADAPT |
| Godot import configuration, [3D scene import](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html) | Import settings and asset-processing steps affect collision, materials and reimport behavior | GLB content being valid is not equivalent to playable quality | STUDY |

MGR native placement: `godot-handoff` and Studio package route construct an ownable project from a previously SHA-verified authored world, preserve the source GLB, and generate explicit authored boxes for deterministic collision basics. They do not execute Godot or prove collision contact, input controls, animations, rendering fidelity, or exported standalone game distribution. Runtime acceptance must record the Godot version, import logs, scene-object count, collision measurements, screenshot and executable exit code.
