# MGR BEAST X-Ray — Real REA Research on Rigging, Lip Sync and Terrain
Date: November 1, 2026

**Meaning of completion:** This is an authorized STATIC source study, not four neural inference engines installed or 187 source packages reverse engineered. Same canonical Forge authority: docs/HANDOFF.md. Source/asset creation remains in original MGR Forge. Full third-party source ZIPs and complete REA Evidence stay PRIVATE in the owner's Windows temporary audit workspace, not Git.

## Exact verified evidence

Two public JSON evidence files:
- evidence/xray/2026-11-01-public-engine-rea-source-batch.json: pinned four public GitHub source commit SHAs, exact archive hashes, full or oversize status, actual REA results. Complete source ZIP inventory succeeded for SkinTokens (70 original files). Other three full upstream source archives exceeded the bounded 21MB cap, so this did NOT silently accept them.
- evidence/xray/2026-11-01-research-exact-partial-source-rea.json: Rhubarb (18 exact raw publisher source files), UniRig (5) and Terrain3D (18) selected source files, each with publisher SHA, source path, byte SHA and REA-complete inventory of **the selected derived ZIP ONLY**. Never imply those are complete repositories.

Official installed owner REA version: rea-agents@6.8.0. Each selected archive was observed by real REA inspect-artifact, with complete container-entries coverage. No third-party programs, scripts or downloaded model weights were executed. The separate static code inspection read publisher class/function signatures to identify technical relationships; complete runtime semantics remain unverified.

## Study A — SkinTokens TokenRig (ADAPT principles; weights not admitted)

Original publisher: https://github.com/VAST-AI-Research/SkinTokens
Pinned Git commit: 273b691d35989d71cd17ff2895fdc735097b92d1.
The complete bounded publisher source ZIP contained 70 files; actual REA inventory succeeded. Root LICENSE says MIT for code; trained model checkpoints, Qwen3 backbone, mesh dependencies and training data are separately scoped and NOT yet cleared.

Observed real source modules:
- src/model/tokenrig.py — TokenRig, skeleton/skin token sequence generation, logits processor, predict/training entrypoints
- src/model/skin_vae_model.py — SkinVAEModel, encode/decode and latent conditioning
- src/data/augment.py — part/joint transforms, optional changes in anatomy
- demo.py — model-loading/Blender service integration boundaries
These suggest an MGR-native future semantic anatomy graph and a skin-weight continuation across changing skeleton structure, but no claim that a research MIT root means pretrained weights can be used commercially.

Current Forge code compared: forge/creature_rig_recipe.py parametric role graph; forge/morph_engine.py shared mesh-bone bend/taper; bridge/blender_creature_skin.py real local skin export.
Decision: design original mesh-to-rig semantic/weight interface and benchmark only a legally accepted checkpoint with suitable CUDA rental after explicit cost permission; do NOT embed this model now.

## Study B — UniRig (ADAPT separate skeleton/skin pipeline)

Original publisher: https://github.com/VAST-AI-Research/UniRig
Pinned commit: 6793c6640ff01c8fb389f3993434124bb43d2933.
Full source archive >21MB; bounded derived ZIP with LICENSE/README/requirements and TWO publisher neural model files, real REA inventory succeeded on 5 files.
- src/model/unirig_ar.py — UniRigAR with encode_mesh_cond, generate, logits processor; skeletal sequence generator
- src/model/unirig_skin.py — BoneEncoder, SkinweightPred and UniRigSkin, separate conditioning and skin inference stage
Decision: MGR's original system should validate the semantic skeleton first, then calculate weights with an independently testable stage and correct bind pose/retarget/collision QA. The actual downloadable model-card checkpoint availability, weights and dependencies are still not checked fully. No UniRig binary installed/executed.

## Study C — Rhubarb Lip Sync (ADAPT timed mouth cue notion)

Publisher: https://github.com/DanielSWolf/rhubarb-lip-sync
Pinned commit: 9b9573cd21b253c9ba58739bbd1aa0b50b991bff.
Full archive exceeded 21MB; bounded source subset includes 18 exact files and root LICENSE.md and rhubarb/src/animation/mouthAnimation.cpp; real REA inventory passed for selected sources. Source primarily controls 2D discrete mouth animation cues; third-party WebRTC dependencies have separate notices.
Decision: original Human Forge uses forge/lipsync.py manually timed phonemes; new forge/audio_motion.py CPU WAV loudness-driven jawOpen/mouthWide, independently rendered in Blender. This is NOT an accurate forced phoneme aligner. No Rhubarb executable installed, bundled code copied or terms erased. Future licensed aligner must prove actual timestamps and accuracy, then map to MGR's 3D facial shapes.

## Study D — Terrain3D (ADAPT streaming collision mechanics, do not assume Godot compatibility)

Publisher: https://github.com/TokisanGames/Terrain3D
Pinned commit: cdcd382cd639f0b043444d7d161f1a6c00d30977.
Full archive >21MB; 18 bounded source files were selected and inventoried via REA, including LICENSE.txt, README.md, src/terrain_3d_collision.cpp and associated LOD baking editor add-on scripts.
Observed actual Terrain3DCollision methods initialize(), build(), update(), set_shape_size() and per-region shape transforms. These show region-specific dynamic terrain collision rather than a flat-static model. Full streaming/physics source and runtime are NOT inspected or exercised. MIT root code; nested addons need provenance checks. Owner's previous portable Godot 4.3 may be too old for latest Terrain3D; exact target version and runtime must be verified.
Decision: original World Forge now produces original biomes plus one real Blender city+terrain GLB through forge/world_composition.py, with source SHA lineage. Godot project packaging exists; real streaming/navmesh/collisions remain a separate open acceptance, not instantly solved by source study.

## Source-to-MGR build status

| MGR result | Actual source and proof | Unfinished gate |
|---|---|---|
| Original 3D creature morph | forge/morph_engine.py, forge/creature_rig_recipe.py, actual Chrome/Blender tests | arbitrary learned topology, skin deformation and 200+ verified motions |
| Speaking generic Human face | forge/lipsync.py, forge/audio_motion.py, forge/human_lipsync.py, Blender GLB+8 morph targets | phoneme recognition/alignment, teeth/jaw/tongue/face realism and identity acceptance |
| City + terrain as ONE asset | forge/world_composition.py, bridge/blender_world_compose.py and independent second Blender receiver | actual playable Godot physics/navmesh/large streaming world and owner art |
| Existing shared MCP service | MGR-API-MCP/src/forge-catalog-client.ts and src/forge-mcp-tools.ts | actual remotely deployed OAuth issuer/worker/artifact store and Tevin/ChatGPT clients |
| Optional neural generation | forge/data/generative_engines.json and forge/generative_backends.py profile/preflight | licenses/checkpoint/GPU/real inference/quality/cost evidence |

**Next REA study queue:** Khronos glTF Validator, glTF-Transform, meshoptimizer, legitimate voice alignment/viseme and rig weighting resources. Every analysis must record publisher SHA, nested code/weights/data license, exact read/REA coverage, original MGR target capability and **independent 3D output test**. REA ZIP inventories are only one layer of actual engineering evidence.
