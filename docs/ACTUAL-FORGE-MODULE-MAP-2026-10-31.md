# MGR Forge — actual 3D code module reference, audited baseline 2026-10-31

Read THIS alongside docs/HANDOFF.md and docs/FORGE-ENGINEERING-HANDBOOK.md. Every module path below existed on baseline 310badac0661422fd1415b9d3baa52fed7127391 and its Python AST was inspected. Direct-import test matches are heuristic, not proof of runtime linkage.

| Module path | Source docstring purpose | Public exported declarations | Direct imports from test files |
|---|---|---|---|
| `forge/__init__.py` | MGR Forge: local-first, deterministic 3D creation primitives. |  |  |
| `forge/adapters.py` | Replaceable generation adapters with explicit offline and resource contracts. | AdapterCapabilities, ProceduralWorldAdapter, UnavailableNeuralAdapter, select_adapter | tests/test_forge.py |
| `forge/ambientcg_source.py` | Official ambientCG v3 public read API adapter; metadata only, no raw download. | search_ambientcg |  |
| `forge/animation.py` | Bone-length-preserving procedural arm posing and animation metadata. | pose_landmarks, arm_pose_clip | tests/test_forge.py |
| `forge/asset_atlas.py` | MGR Source Atlas: source discovery, bounded CC0 GLB intake, honest rights gates. | inspect_import_glb, MGRSourceAtlas, MGRAssetCatalog | tests/test_ambientcg_source.py, tests/test_asset_atlas.py |
| `forge/asset_parity.py` | Independent CPU format parity audit for Forge's own GLB and OBJ exports. | audit_export_parity | tests/test_asset_parity.py |
| `forge/assets.py` | Content-addressed asset indexing with explicit rights and provenance metadata. | AssetRegistry, re_sha256 | tests/test_asset_atlas.py, tests/test_forge.py |
| `forge/benchmark.py` | Local reproducible CPU geometry and GLB exporter benchmark receipts. | run_benchmark, main | tests/test_forge.py |
| `forge/blender_bridge.py` | Optional external Blender import proof; never pretends Blender was run. | blender_command, verify_blender, blender_render_command, blender_facts_command | tests/test_director.py, tests/test_forge.py |
| `forge/blender_roundtrip.py` | Reconcile a real Blender edit back to MGR's original world geometry contract. | roundtrip_command, export_blender_edits | tests/blender_live_scene_smoke.py, tests/test_blender_roundtrip.py |
| `forge/cell_transport.py` | Bounded, integrity-checked local 3D cell transport with deterministic LRU. | MGRCellTransport | tests/test_cell_transport.py |
| `forge/character.py` | Provisional modular mannequin proving full-frame hands and detachable parts. | mannequin, build_mannequin | tests/test_character_intake.py, tests/test_character_readiness.py |
| `forge/character_glb.py` | Bounded inspection of ordinary, uncompressed glTF 2.0 GLB assets. | parse_character_glb | tests/test_character_glb.py, tests/test_character_readiness.py |
| `forge/character_intake.py` | Admission of user-owned GLB character candidates without inventing likeness/rigs. | inspect_candidate, admit_candidate, create_character_blend, verify_character_blend | tests/test_character_intake.py, tests/test_character_separation.py |
| `forge/character_motion.py` | Blender-backed export and independent receiving-import proof for deforming rigs. | export_character_motion, reimport_character_motion | tests/test_character_motion.py |
| `forge/character_readiness.py` | Evidence-only character part inventory and rig readiness for admitted GLB models. | inventory_character, write_character_readiness | tests/test_character_readiness.py |
| `forge/cinematic.py` | MGR-native editable 3D camera tour, independent of pre-rendered video. | camera_tour, interpolate_shots | tests/test_forge.py |
| `forge/cli.py` | Offline CLI: python -m forge.cli build --out /path/to/output. | build, main | tests/blender_live_scene_smoke.py, tests/image_relief_smoke.py |
| `forge/code_architect.py` | MGR Code Architect: inspectable, recoverable workspace-file jobs. | FileChange, WorkspaceFileJob | tests/test_code_architect.py, tests/test_repair.py |
| `forge/consciousness.py` | MGR Scene Consciousness: deterministic facts about generated worlds. | scene_facts, scene_query | tests/test_consciousness.py |
| `forge/creation_memory.py` | MGR Creation Memory — approved identity locks and reproducible revisions. | CreationMemory | tests/test_creation_memory.py |
| `forge/creature_jobs.py` | Native original-creature durable request adapter for the existing Forge Studio. | creature_job_status, create_creature_job |  |
| `forge/creature_rig.py` | Standalone MGR creature rig pipeline via local Blender. | rig_creature | tests/test_creature_rig.py |
| `forge/creature_rig_recipe.py` | MGR Creature DNA -> transform-compatible rig blueprint. | creature_bones, save_creature_rig_recipe | tests/test_creature_rig_recipe.py |
| `forge/director.py` | MGR Director: shots, cuts, holds and smooth camera moves in authored 3D. | compile_director_reel, ease_fraction, sample_motion | tests/test_director.py |
| `forge/durable_queue.py` | Durable local job queue with file-based checkpointing. | JobSpec, JobState, DurableJobQueue | tests/test_durable_queue.py |
| `forge/dynamics.py` | MGR CPU continuous horizontal collision guard for actor motion segments. | first_motion_contact | tests/test_dynamics.py |
| `forge/engine_handoff.py` | MGR-owned, deterministic playable-scene handoff for Godot 4. | export_godot_project | tests/test_engine_handoff.py |
| `forge/environment.py` | Reusable CPU procedural greenery for undeveloped grid lots. | generate_parks | tests/test_forge.py |
| `forge/fx.py` | MGR Fantasy Forge: deterministic CPU-authored 3D effect geometry. | create_magic_effect, export_effect_glb | tests/test_fx.py |
| `forge/fx_judge.py` | MGR FX Judge: measured atmospheric render change at a matched camera. | judge_atmosphere | tests/test_fx_judge.py |
| `forge/garment_fit.py` | MGR-native garment fitting contract. | FitResult, fit_garment, garment_coverage | tests/test_garment_fit.py |
| `forge/generative_backends.py` | Planning boundary for external open-weight 3D models. NO downloads or inference. | load_engine_profiles, preflight_generation | tests/test_generative_backends.py |
| `forge/geometry.py` | CPU-generated, real triangle geometry. Y is up; X/Z form the ground. | Mesh, create_neighborhood | tests/test_asset_atlas.py, tests/test_asset_parity.py |
| `forge/glb.py` | Minimal glTF 2.0 binary exporter/validator, using only Python stdlib. | export_glb, inspect_glb | tests/test_asset_atlas.py, tests/test_asset_parity.py |
| `forge/gpu_accounts.py` | MGR-native GPU account and credential management. | ProviderCredential, UserAccount, AccountStore, GpuAccountManager | tests/test_gpu_accounts.py |
| `forge/gpu_lifecycle.py` | GPU instance lifecycle and per-user billing ledger. | InstanceRecord, UserAccount, InstanceManager, BillingLedger | tests/test_gpu_lifecycle.py |
| `forge/gpu_packer.py` | Deterministic CPU-only GPU block packing with bounded shadow backfill. | pack_jobs | tests/test_gpu_packer.py |
| `forge/gpu_rental.py` | Dry-run rental planner. Price quotes are caller-supplied, never claimed live. | plan_rental | tests/test_gpu_rental.py |
| `forge/hardware.py` | MGR resource-aware model admission; no automatic GPU/vendor assumptions. | ComputeProfile, ModelRequirement, assess_local_model | tests/test_hardware.py |
| `forge/image_relief.py` | MGR-native PNG-to-2.5D relief: actual geometry, not imagined hidden 3D surfaces. | decode_png, make_relief, export_image_relief | tests/test_image_relief.py |
| `forge/imagination.py` | MGR native procedural imagination: new mesh geometry, not preset-kit selection. | genome_candidates, creature_meshes, create_original_creature | tests/test_creature_rig.py, tests/test_creature_rig_recipe.py |
| `forge/interiors.py` | MGR Beyond Imagery: generated, editable room hypotheses inside buildings. | generate_interiors | tests/test_forge.py |
| `forge/live_blender.py` | Translate a verified MGR edited-world bundle into an editable Blender scene. | validate_live_bundle, live_blender_command, create_live_blender_scene | tests/blender_live_scene_smoke.py, tests/test_live_blender.py |
| `forge/marching.py` | Smooth surface extraction from voxel occupancy via surface nets. | surface_nets | tests/test_multiview.py |
| `forge/material_guardian.py` | MGR material round-trip acceptance, separate from cosmetic visual quality. | validate_imported_materials | tests/test_materials_cinematic_wardrobe.py |
| `forge/materials.py` | MGR material recipes: portable, CPU-authored physically-based parameters. | validate_pbr_recipe, make_material | tests/test_materials_cinematic_wardrobe.py |
| `forge/meshqa.py` | CPU mesh health checks and conservative triangle cleanup. | analyze_mesh, remove_bad_triangles | tests/test_forge.py, tests/test_imagination.py |
| `forge/morph_engine.py` | Safe non-destructive 3D mesh morphs; preserves vertices/faces/material groups. | normalize_morph, morph_point, morph_mesh | tests/test_creature_rig_recipe.py, tests/test_morph_engine.py |
| `forge/motion_truth.py` | MGR Continuous Motion Guardian: bounded, sampled 3D kinematics. | judge_motion_samples | tests/test_motion_truth.py |
| `forge/multiview.py` | MGR-native multi-view silhouette reconstruction (space carving). | carve, reconstruct, score_against_solid, export_reconstruction | tests/test_multiview.py |
| `forge/obj.py` | CPU-only Wavefront OBJ/MTL fallback export with stable materials. | export_obj | tests/test_asset_parity.py, tests/test_forge.py |
| `forge/pack_mirror.py` | Pin and preserve explicitly chosen official CC0 kits; never auto-promote assets. | license_claim_scope, mirror_kaykit_pack | tests/test_pack_mirror.py |
| `forge/perception.py` | MGR Spatial Eyes — geometry-grounded scene visibility and evidence labels. | scene_overview | tests/test_forge.py |
| `forge/pipeline.py` | MGR Forge end-to-end offline scene build, Blender evidence and visual QA. | run_pipeline | tests/test_pipeline.py |
| `forge/planner.py` | Bounded natural-language-to-world planner; offline deterministic rules, not an LLM. | Plan, plan_neighborhood | tests/test_forge.py |
| `forge/pose_guardian.py` | MGR pose acceptance: measurable rig and detachable-part continuity. | validate_pose_frames | tests/test_pose_guardian.py |
| `forge/preview.py` | Dependency-free, isometric SVG preview of generated world manifests. | render_world_svg | tests/test_forge.py |
| `forge/quality.py` | Pure, measurable checks for worlds and character landmark requirements. | validate_neighborhood, validate_character_landmarks, compare_character_identity | tests/test_forge.py |
| `forge/receipt.py` | Cryptographic artifact receipts and tamper checks for generated bundles. | file_receipt, verify_bundle | tests/test_forge.py, tests/test_world_editor.py |
| `forge/recipes.py` | MGR Forge Model Dock — MGR-native safe model recipe inspection, never execution. | ModelRecipe, inspect_recipe | tests/test_forge.py |
| `forge/rectify.py` | Perspective-to-orthographic rectification for multi-view reconstruction. | homography, apply_homography, warp_perspective_to_orthographic, rectify_mask | tests/test_rectify.py |
| `forge/reference_pack.py` | Private multi-image reference admissions and whole-character asset job graph. | png_size, prepare_reference_pack | tests/test_reference_pack.py |
| `forge/repair.py` | MGR Self-Repair Studio: bounded recoverable file-repair coordination. | RepairOutcome, repair_until_pass | tests/test_repair.py |
| `forge/sam_adapter.py` | Optional SAM (Segment Anything) adapter behind the F108 contract. | SamAdapter, register_sam_if_available, describe_sam | tests/test_sam_adapter.py |
| `forge/scene_layers.py` | MGR-owned deterministic scene composition, independent of any vendor runtime. | compose_scene_layers | tests/test_scene_layers.py |
| `forge/security/__init__.py` | Defensive MGR-owned integrity/release controls; no hidden runtime operations. |  |  |
| `forge/security/rambler.py` | MGR Rambler v0: safe release byte-integrity manifest, not secrecy. | create_roster, verify_roster, save_roster |  |
| `forge/segmentation.py` | MGR-native segmentation adapter contract. | SegmentationError, MaskResult, SegmentationAdapter, ManualMaskAdapter | tests/test_sam_adapter.py, tests/test_segmentation.py |
| `forge/shot_design.py` | MGR Cinematic Director contract for portable, reproducible world shots. | validate_shot_reel, lighting_recipe, validate_camera_clearance | tests/test_materials_cinematic_wardrobe.py |
| `forge/smooth.py` | Vertex de-duplication and normal averaging for honest smooth shading. | smooth_normals | tests/test_multiview.py |
| `forge/spatial_truth.py` | MGR Spatial Truth: CPU 3D↔2D perspective and geometric cross-sections. | camera_project, pixel_to_ray, triangulate_parallel_views, triangulate_oriented_views | tests/test_spatial_truth.py |
| `forge/spec.py` | Strict contracts for deterministic CPU world creation. | WorldSpec | tests/blender_live_scene_smoke.py, tests/test_asset_parity.py |
| `forge/streaming.py` | Deterministic chunk registry and CPU mesh level of detail for simple worlds. | chunk_world, simple_building_lod, lod_for_distance, plan_chunk_residency | tests/test_forge.py, tests/test_residency.py |
| `forge/studio_quality.py` | Ten bounded MGR-native studio-quality *measurement primitives*. | material_reality_witness, adaptive_light_orchestra, flesh_translucence_witness, surface_anatomy_guardian | tests/test_studio_quality.py |
| `forge/studio_server.py` | Local-only MGR Forge creation workstation: browser to verified files. | ForgeWorkstation, make_handler, start_server | tests/test_creature_jobs.py, tests/test_studio_server.py |
| `forge/surface_truth.py` | MGR Surface Truth: conservative CPU triangle edge-manifold evidence. | inspect_surface_edges | tests/test_surface_truth.py |
| `forge/traversal.py` | MGR World Logic: deterministic ground-route traversal rehearsal. | rehearse_road_walk | tests/test_traversal.py |
| `forge/unclothe_3d.py` | Unclothe 3D: bounded, owner-gated separation of visible character parts. | inspect_unclothe, extract_approved_parts, materialize_unclothe_proxies | tests/test_unclothe_3d.py |
| `forge/view_identity.py` | MGR View Identity — cautious identity decisions across views and poses. | AssetView, compare_asset_views, compare_view_silhouettes | tests/test_view_identity.py |
| `forge/visualqa.py` | MGR Visual Judge: exact PNG pixel QA for repeatable Blender renders. | read_png, silhouette, compare_pngs | tests/test_visualqa.py |
| `forge/voice.py` | MGR-native voice capture and transcription contract. | VoiceCapture, WindowsSpeechCapture, UnavailableVoiceCapture, build_voice_capture |  |
| `forge/wardrobe.py` | MGR wardrobe part taxonomy and source/skin separation gate. | wardrobe_inventory | tests/test_materials_cinematic_wardrobe.py |
| `forge/web_runtime.py` | Compile a fully offline, self-contained playable WebGL2 world from Forge output. | make_world_flight | tests/test_web_runtime.py |
| `forge/workflow.py` | Dependency-aware creation plan, spend gate and durable local job state. | Step, resolve_plan, approve_plan, LocalJobStore | tests/test_forge.py |
| `forge/world.py` | Deterministic road graph, building entrances and coarse collision checks. | graph_for_world, entrance_for_building, shortest_road_path, overlaps_building | tests/test_forge.py |
| `forge/world_editor.py` | MGR-native editable world roundtrip: browser JSON -> real, independently inspectable 3D files. | apply_world_edits | tests/blender_live_scene_smoke.py, tests/test_live_blender.py |
| `forge/world_jobs.py` | Recoverable, exactly-one-owner idempotency ledger for local 3D world edits. | world_job_status, create_world_job |  |
| `forge/xray_kit.py` | REA Evidence -> Forge Vault cross-check. No copying third-party code/assets. | audit_kit_with_rea, write_xray_kit_receipt | tests/test_xray_kit.py |

Presence and parseability are not semantic correctness. Dynamic registry imports, CLI wrappers and indirect tests can provide other links. Audit the actual end-to-end path before calling a module orphaned.
