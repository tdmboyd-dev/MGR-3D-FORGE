# Receiving animation must move the imported mesh

The creature receiving bridge imported bones/actions and rendered a preview, but inherited the exporting process's motion number. The human receiving bridge imported morph keys/actions and sampled three jaw values, without accepting or rejecting actual mesh deformation. Both paths could therefore accept an inventory of animation objects that did not establish working received deformation.

The creature receiver now evaluates its imported dependency graph at frames 1 and 16, requires stable receiving vertex correspondence and finite motion above 1 cm, and records its own moving-vertex count. Native acceptance requires those receiving measurements. The human receiver evaluates every authored frame and all eight channels at the authored FPS, measures both temporal vertex displacement and nonzero shape response, and emits per-channel extrema. Native Human Forge compares these extrema and source identity to the original timeline and requires geometry motion when the authored curves vary. Silence remains a valid static result. The face receiving render path now resolves relative paths before Blender renders; an actual relative-path run exposed and reproduced that failure.

Commands executed:

```
python scripts/verify_creature_receiver.py --out artifacts/creature-receiver-regression-20261102
python scripts/verify_human_receiver.py --out artifacts/human-receiver-regression-20261102
python -m unittest tests.test_imported_morph tests.test_creation_asset_jobs tests.test_creature_rig tests.test_creature_rig_recipe tests.test_human_lipsync tests.test_human_jobs tests.test_materials_cinematic_wardrobe tests.test_asset_atlas -v
```

Both Blender verification scripts returned `PASS`. The focused suite passed 68 tests; its log is in `../imported-morph-core-2026-11-02/tests.txt`. These were actual separate Blender 5.2.2 LTS processes, not mocked imports or provider calls.

- Creature: 19 receiving bones, one action, 1,333 receiving vertices, 220 moving vertices, maximum displacement 0.99043 m. The exporter originally had 1,196 vertices; export seams split some vertices, so the receiver compares its own stable order across frames. A negative GLB retains its skin/action inventories but freezes every animation sampler to its first value. The separate receiver explicitly refuses this asset for no vertex motion.
- Human timed cues: 30 FPS, 28 frames, 128 received facial vertices, eight shape targets, one action, 0.116386 m temporal displacement and 0.091187 m maximum response from the base shape. All eight received channel extrema match the native authored timeline within 0.0002.
- Human PCM fixture: actual owned synthetic PCM16 audio at 60 FPS also passes receiving curve and geometry checks. This remains loudness-reactive jaw motion, not speech recognition or phoneme alignment.
- Human silence: actual silent PCM at 12 FPS remains static and passes without falsely claiming speech motion.
- Human negative: morph displacement accessors are zeroed while retaining their shape/action inventories and varying key weights. The separate Blender receiver explicitly refuses the inert shapes because received vertices do not deform.

The PNGs here were opened and inspected. They remain rough generic proxy art. Measurements establish the tested animation paths, not photorealism, anatomical skin quality, approved identity, locomotion, cross-skeleton retargeting or production rig acceptance. Exact safe receipts and source SHA-256 identities are retained alongside this report; raw Blender files, WAV fixtures and logs remain in ignored artifacts.

## Wider scoped findings

Inspected source includes the original morph engine and GLB/character intake/parser/readiness owners, creature recipe and skin bridges, Human Forge timelines/audio/jobs/facial bridges, humanoid rig bridge, animation landmarks, pose guardian, wardrobe, PBR recipes/material guardian and Source Atlas. Relevant focused suites executed above. This is a scoped source/runtime audit, not a claim to have read or executed every repository file.

Generated `export_glb` currently emits POSITION/NORMAL attributes and factor-based materials; it does not author UV layouts or textures. Imported UV/image preservation is separately proven by the static morph witness, which does not establish UV creation. No general UV unwrap/atlas bake/texture-paint authoring or cross-skeleton retarget operation was found in these Forge/bridge/CLI paths. Humanoid rigging is an authored eleven-bone template with mostly rigid single-bone weights and two-bone elbow sleeves; creature rigging uses nearest-segment weights. `animation.py` is explicitly a landmark pose track, not skinned mesh export. Source Atlas is rights-aware source metadata/quarantine intake, distinct from native geometry/material generation. These gaps remain open; they are not relabeled completed by the receiver repairs.
