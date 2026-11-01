# MGR Forge — Create, Morph, Rig, Animate and Lip-Sync: Source-Based How-To

**Read before modifying:** docs/HANDOFF.md, docs/ACTUAL-FORGE-MODULE-MAP-2026-10-31.md, docs/FORGE-ENGINEERING-HANDBOOK.md and affected source/tests. This handbook describes what the current repository REALLY implements, followed by the explicit missing path to master-quality output.

## A. Native original creature — working CLI workflow

Run from MGR-3D-FORGE root. Python 3.10+; no GPU service needed for this current procedural workflow.

```powershell
python -m forge.cli imagine-creature --prompt "Invent a horned winged forest animal with a long tail" --seed 21 --variants 8 --out artifacts/creature-21
python -m forge.cli inspect artifacts/creature-21/creature.glb
python -m forge.cli rig-creature --source artifacts/creature-21 --out artifacts/creature-21-rigged --blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
```

Look at `creature.json` (DNA, chosen variant, morphology recipe, exact GLB SHA and limitations), `creature-21-rigged/creature-rigged.glb`, `creature-rigged.blend`, `skin-proof.json` and actual preview PNG. This may be a rough, low-poly stylized creature. Rig output is independently reimported in a second Blender process when the command succeeds; shape/motion art acceptance and per-target engine use remain separate.

Existing source chain: `forge/imagination.py -> forge/morph_engine.py -> forge/creature_rig_recipe.py -> forge/creature_rig.py -> bridge/blender_creature_skin.py -> bridge/blender_creature_reimport.py`. Retain the generated input DNA and exact shape hash. Current proximity-based skin weighting and simple appendage animation need improvement; no guarantee of arbitrary creature topology support.

## B. Existing character parts and Blender intake

```powershell
python -m forge.cli character --pose T --out artifacts/generic-tpose
python -m forge.cli character-intake --source artifacts/owned-reference.glb --out artifacts/intake
python -m forge.cli character-readiness --source artifacts/intake/candidate.glb --out artifacts/readiness.json
python -m forge.cli character-blender --candidate artifacts/intake --blend artifacts/new.blend --report artifacts/import-proof.json --binary blender
```

Actual source modules: `forge/character.py`, `forge/character_intake.py`, `forge/character_readiness.py`, `forge/wardrobe.py`, `forge/garment_fit.py`. These do not make photo-real, user-approved human faces or hair by themselves. For source photos, obtain appropriate rights and map camera/view consistency before reconstruction.

## C. Existing geometric morph — what it does

`forge/morph_engine.py` applies size/stretch and Y-axis twist to an existing geometry field, with input bounds and per-face normal recalculation. `forge/imagination.py` applies one shared extent across material meshes so sections don't twist at different rates. `forge/creature_rig_recipe.py` transforms skeleton joint endpoints with that same field. This is **mesh-level deformation of already existing geometry**, not arbitrary AI invention of anatomy or a facial muscle system.

When adding a new morph, preserve source, source-model SHA and original mesh; store a reversible DNA delta, transform both vertices AND joint endpoints with one common coordinate convention, and then re-solve skin weights plus any attached clothing. Test degeneracy, bone inversion, self-intersection, feet/hand grounding and imported GLB validity. A passing triangle count alone is insufficient.

## D. How to build MGR advanced mesh + rig morphing (NOT done yet)

1. **Semantic anatomy graph:** classify bones, joints, limbs, surface regions, eyes, mouth, tail, wings, torso, cloth and accessories; preserve original vertex IDs/provenance and a reversible edit graph.
2. **Coordinate-safe deformation:** use reusable space mappings for mesh, skeleton, skinning bind poses, corrective shape keys and attached garments. When changing limb count, regenerate topology/bones/weights and invalidate incompatible animation clips rather than silently snapping them onto wrong joints.
3. **Morph + rig continuum:** design a shared parameter schema for body proportion, joint placement, bend/twist range, fingers, jaw, tail, multi-wing rigs, and inverse bind constraints. Add Blender skinning QA on animated motion, not just rest pose.
4. **Motion retargeting:** map source skeleton semantics to target skeleton, protect bone lengths and ground contacts, retarget root motion and rig constraints, and compare multi-frame poses in Blender and Godot. Track original motion sources/licensing.
5. **Procedural locomotion:** different motion families for quadrupeds, biped, serpents, birds, swimming animals, multi-legged fantasy hybrids and massive monsters. Different limbs require different ground/wing physics; reusable actions alone won't invent believable motion.
6. **Rig quality proof:** normalize skin weights, detect orphan/duplicate joints, severe knee/elbow/shoulder/corner deformation, collisions and extreme interpolation; require independent engine import and animated visual acceptance for each species.
7. **Rig/mesh repair:** maintain a visible before/after deformation score and user override to keep original source unchanged when repairs don't improve quality.

Useful current components: `forge/character_motion.py`, `forge/animation.py`, `forge/pose_guardian.py`, `forge/meshqa.py`, `forge/repair.py`, `bridge/blender_creature_skin.py`. External UniRig, AniGen, Rigger and Rigify research stays in `research/external-provenance/NEXT-GEN-MORPH-RIGGING-2026-10-31.md`; don't auto-install model weights or restricted Blender add-ons without code AND checkpoint licenses.

## E. MGR lip-sync and expression engine — truth + recommended design

**Current status: OPEN.** Source search in this audit found no actual phoneme/aligned-viseme generator in Forge. `forge/voice.py` captures/transcribes a voice command under a platform-specific contract; it does **not** drive mouth animation.

**Input contract** should contain approved speech/audio + transcript, language, consent, actor rig identity, sample rate, alignment timestamps, confidence, emotion/intensity, and output target. Speech-to-text is NOT time-aligned phonemes by default; require forced alignment from a legally usable engine or timing supplied by user. Original or authorized voice only.

**Pipeline:** audio -> transcript + language -> phoneme time alignment -> bounded coarticulated viseme channels -> jaw open/lower lip/tongue/teeth and mouth corners -> facial expressions/eye/blink -> clip exporter -> independent real-time Blender preview -> GLB/VRM and Godot animation.

**Suggested explicit animation tracks:** jawOpen, mouthClose, mouthFunnel, mouthPucker, mouthSmileLeft/Right, mouthFrownLeft/Right, mouthDimpleLeft/Right, mouthRollUpper/Lower, mouthShrugUpper/Lower, mouthPressLeft/Right, mouthLowerDownLeft/Right, mouthUpperUpLeft/Right, cheekPuff, cheekSquint, tongueOut and voice-specific extra controls. These are TARGETS, not current implemented shape keys. ARKit's 52 common blendshape names are a useful interoperability reference; real rig mapping must be measured.

**Acceptance gates:** 1) time-coded phoneme evidence matches source audio; 2) per-frame blendshape weights stay bounded with smoothing; 3) lips align to actual speech, teeth/tongue don't intersect mesh; 4) speech+emotion shape blends remain facially consistent; 5) independent Blender and GLB action import; 6) visual comparison to user-provided reference; 7) acceptable latency and device cost. Until tested, label output as TIMELINE_PROPOSAL, not synchronized audio.

## F. Source and license gates

Model checkpoints and Blender add-ons may have different terms than their GitHub root; use per-subtree, model-card, dependency and output license review. Quaternius's newer pack rules restrict standalone raw redistribution; AniGen CUBVH has a restricted NVIDIA folder; Adobe RigAnything is research-only; many model runtimes need rented GPUs. Asset Vault stores source/version/hashes; approval is independent of a useful model or a passing Blender import. `docs/HOW-TO-SOURCE-VAULT-REA.md` is the operations guide.

## G. Checklist for a legitimate production creature/motion feature

Owner brief -> source/DNA -> newly generated GLB + hash -> mesh/UV normals -> material/skin/rig -> physically sane deforming poses -> audio/motion timing -> independent Blender action reopen -> Godot target engine -> owner visual acceptance -> versioned re-editable project and durable receipts. A feature is not 100% complete until every declared user-facing criterion passed.


## H. New official source research — exactly sourced, NOT installed (XR-0185–187)

**SkinTokens / TokenRig**: https://github.com/VAST-AI-Research/SkinTokens . MIT code according to its root LICENSE, unified mesh -> skeleton + skin weights, project claims NVIDIA GPU >=14 GB and Python >=3.11; actual checkpoint/model/data/QLoRA or Qwen3 dependencies must be separately reviewed. Research on 2026-10-31; no MGR inference or side-by-side result yet. Stronger architecture candidate for new topology and direct edit-to-rig feedback than simply importing an old animation.

**NVIDIA Audio2Face-3D**: https://github.com/NVIDIA/Audio2Face-3D . Publisher distinguishes MIT SDK, Apache training code, NVIDIA Open Model lip-sync weights, custom Audio2Emotion model terms and evaluation-only training sample data. This can drive real blendshapes/joints from audio, but no binary, weight or dataset was installed or licensed into Forge. Treat SDK/weights/emotion/data as **four separate intake decisions** and compare exact performance/rights before trying to make Tevin talk.

**Rhubarb Lip Sync**: https://github.com/DanielSWolf/rhubarb-lip-sync and https://github.com/DanielSWolf/rhubarb-lip-sync/blob/master/LICENSE.md . MIT CLI with additional third-party notices. Produces timing for discrete mouth shapes mainly for 2D assets; useful as a permissive reference for low-cost audio-to-mouth-cue timing, **not** proof of MGR-native 3D facial motion or a modern Blender plugin. The original Blender add-on https://github.com/scaredyfish/blender-rhubarb-lipsync states it does not work with Blender 3.2+, so DO NOT install it as the 5.2 production solution.

**UniRig caveat**: README at https://github.com/VAST-AI-Research/UniRig documents skeleton and skinning inference, but the publisher's https://huggingface.co/VAST-AI/UniRig model card describes a narrower currently released checkpoint. This mismatch must be resolved by exact checkpoint/files and tests before calling full rigging weights available. The existing MGR rigging pipeline remains the fallback.

**Research tracking:** three candidate records XR-0185 to XR-0187 are SOURCED_PUBLIC_DOCS, not end-to-end read, not REA-scanned, not installed. Final comparison requires Blender 5.2 and target-engine testing on the same authorized meshes and recorded licenses, VRAM, latency, topology and visual deformation.
