# MGR source study: 3D rigging, new skeletons, facial lip-sync

October 31, 2026. SOURCE ONLY, not installed, REA-scanned or end-to-end executed. Record IDs XR-0185–XR-0187 in the 187-entry Forge research universe. Existing MGR modules: forge/creature_rig.py, forge/creature_rig_recipe.py, forge/morph_engine.py, forge/character_motion.py and forge/voice.py.

## SkinTokens / TokenRig

Publisher repo https://github.com/VAST-AI-Research/SkinTokens and MIT root code license https://github.com/VAST-AI-Research/SkinTokens/blob/main/LICENSE . It reports mesh-to-skeleton-and-skin-weights in one model, can use a provided skeleton and recommends NVIDIA CUDA >=14 GB VRAM with Python >=3.11. The reported 98–133% skinning accuracy improvement and 17–22% bone prediction improvement are THEIR benchmarks, not confirmed MGR performance. Code license does NOT automatically clear all pretrained checkpoints, Qwen3 backbone, dependencies, datasets or example meshes. Study exact versions before inference/embedding. Decision: SOURCED and prioritize as alternative to generic uniform/proximity weights; no GPU weights fetched.

## NVIDIA Audio2Face-3D SDK/models

Official publisher https://github.com/NVIDIA/Audio2Face-3D lists MIT SDK, Apache training framework, NVIDIA Open Model pretrained lip-sync weights, separate custom Audio2Emotion models, and evaluation-only training sample data. Separate code, model, emotion and data license decisions; no permissive blanket license. Audio-driven blendshapes and facial joint rotations are promising for Tevin and new speaking creatures, but source outputs require a real MGR face rig, allowed material and independently inspected animation. Decision: SOURCED, checkpoint/runtime/license audit still open, no install.

## Rhubarb Lip Sync

Source https://github.com/DanielSWolf/rhubarb-lip-sync and exact license https://github.com/DanielSWolf/rhubarb-lip-sync/blob/master/LICENSE.md . Its MIT-coded command-line tool produces time-coded mouth cues for recordings, largely a 2D mouth-animation reference, not automatic 3D jaw/tongue/muscle geometry. Older Blender add-on https://github.com/scaredyfish/blender-rhubarb-lipsync explicitly says it is incompatible with Blender 3.2+ and cannot be adopted untested for the installed Blender 5.2.2. Decision: SOURCED for timing reference only; original MGR facial shape-key target and 3D deformation QA required.

## Existing UniRig ambiguity

Repo https://github.com/VAST-AI-Research/UniRig documents skeleton+skinning inference, while https://huggingface.co/VAST-AI/UniRig model card describes narrower checkpoint availability. Resolve EXACT model file inventory and licenses before adopting a purported full weight pipeline. Release screenshots are not Forge acceptance.

## MGR-native morph and viseme acceptance blueprint

Current morph engine: bounded length/height/width/twist with a shared transform for material meshes and skeleton joints; current voice.py: capture/transcribe contract, NOT lip sync. New rig capability must allow nonlinear changes to limb count, tail/wing anatomy, bone parenting, corrective skinning, motion retargeting, cloth/face attachments and reversible DNA edits, preserving geometry and identity.

New lip-sync capability must accept authorized audio, language, timed phonemes, transcription and identity controls; produce jaw/cheek/lip/tongue/teeth expressions and corrective shape keys and emotion/eye channels; export an actual deforming Blender + GLB animation and prove timing against audio by independent multi-pose visual checking. Suggested shapes include jawOpen, mouthFunnel, mouthPucker, mouthSmileLeft/Right, mouthPressLeft/Right, mouthRollUpper/Lower, cheekPuff and tongueOut plus additional actual rig channels. These are TARGETS, not already-created shape keys.

No claim of a 200-animation library, photoreal character, real-time speech sync, no-GPU advanced neural rig or unique global-best superiority until real artifact/engine/human evidence exists. Keep all code, model weights and dataset licensing separately, ensure source URLs and future SHA pins are recorded, and avoid importing unsupported legacy Blender add-ons.
