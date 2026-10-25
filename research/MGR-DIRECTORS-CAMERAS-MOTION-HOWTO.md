# MGR Directors, Cameras & Motion — native creation research and build contract

Owner: MGR. Current status: researched/specified foundation, partial implementation.
External technical citations are kept in `research/external-provenance/`.
This is an MGR capability specification, **not** a clone of any third-party tool.

## 1. Definition

Directing is the conversion of intent into a sequence of visual beats with a
subject, dramatic purpose, framing, timed movement, environment, continuity and
final edit. A camera is a 3D projection and its tracked state; motion is a
time-dependent transform, skeletal pose or simulation. These are different
services with explicit ownership and receipts.

## 2. Production use

Typical production stages: brief/story beat → blocking and subjects → lens,
angle and framing → set lighting → camera blocking → character motion → timing
and cuts → render → dailies/quality review → edit/revisions. Film-like workflows
include camera cut, continuity, close/mid/wide shot scales, dolly/crane/orbit,
shot-to-shot geography, focus pulls, camera collision, and audio sync.

## 3. Formats and standards

- glTF 2.0: 3D meshes, skinning, transforms, sampled animations and PBR.
- OpenUSD: composited scene description with time-sampled and layered transforms.
- Blender: cameras, lights, Timeline camera-bound markers, keyframes, Actions,
  Dope Sheet, Graph Editor, NLA, constraints and render engine settings.
- Image EXR/PNG: deterministic QA stills; actual video/audio editorial is open.

## 4. Research and production lessons

Camera position alone is not direction. A tracked camera can still obstruct
the subject, cut to the wrong angle, lose screen direction or fail a hand pose.
World geometry must inform composition. Lens/field of view and motion timing
must be explicit. Moving-object animation and moving-camera animation need
independent tracks and stable frame rates.

## 5. Open implementations and expert references

The production system's building blocks are Blender (local scene authoring),
glTF (exchange), OpenUSD (future richer composition) and engine timelines.
Current MGR build does not vendor third-party code or use externally authored
cinematic templates.

## 6. Models

No generative model required to compile deterministic shots or move cameras.
Optional future models: prompt/storyboard parser, pose-estimation, image-depth,
human motion synthesis, shot-composition critic and motion-retargeting.
Each requires a separate license/hardware/quality gate.

## 7. Datasets

First-party QA fixtures: scripted camera shots of generated scenes, synthetic
landmark poses, negative samples with occluded subjects and intersecting cameras,
one exact render reference per approved camera/material/lighting condition.
External film/pose datasets must be independently licensed before use.

## 8. Licensing

Authored MGR shot contracts and CPU generators belong to MGR. Public format
standards can be implemented. Fonts, motion-capture clips, music, paid LUTs,
actor likenesses and downloaded camera/animation libraries require explicit
usage-rights review before redistribution.

## 9. Providers and services

Provider-neutral contracts: Blender local subprocess; future Unreal/Godot
consumer adapters; optional video, motion or depth API only under cost/approval
gates. Current implementation needs no paid API.

## 10. Native architecture

1. **MGR Narrative Director**: typed scenes, beats, emotional objectives,
   subject IDs, duration, continuity and approvals. *Queued*.
2. **MGR Shot Director**: shot list, screen direction, composition rules,
   lens/target, cut markers, shot timing and camera clearance. *Partial*.
3. **MGR Camera Intelligence**: subject framing, multi-lens choices, tracking,
   focus, shot-size classification, occlusion and motion paths. *Partial*.
4. **MGR Motion Director**: object and bone trajectories, easing, foot plants,
   constraints, motion blending, collision and retarget. *Prototype easing*.
5. **MGR Lighting Director**: reproducible key/fill/rim/ambient, exposure,
   weather/time variations, practical-light continuity. *Three moods partial*.
6. **MGR Scene & Character Continuity**: same asset identity across frames,
   transforms, garments, props, pose transitions and shot axis. *Partial locks*.
7. **MGR Cinematic Judge**: image composition, contact, focus, silhouettes,
   shot consistency, material appearance, motion/temporal QA. *Minimal tests*.
8. **MGR Editorial Director**: cut/trim/transitions, soundtrack, subtitles,
   render assembly and delivery formats. *Not started*.

## 11. Hardware/runtime

Deterministic shot planning and sampled movement are CPU/stdlib workloads.
Blender modeling/rendering is actual desktop work; 8-sample Cycles CPU preview
proved feasible on the owner's integrated-GPU laptop. Final-resolution
cinematic rendering and generative motion/video may benefit from accelerator
hardware; no general GPU-free production-quality claim.

## 12. Cost

Current tested local code and Blender CLI use no paid model calls. Marginal
costs are local electricity, render time/storage and artist QA. Future
dedicated GPU/cloud/paid model costs require timed representative benchmarks.

## 13. Failure modes

- Camera intersecting buildings: detect camera center vs authored AABBs.
- Subject fills frame/cut off: inspect real render and scale/elevation.
- Wrong camera across cuts: bind distinct cameras to timeline markers.
- Jerky motion: use explicit interpolation/easing and endpoint tests.
- Foot sliding/body stretch: evaluate pose and floor contacts; not solved.
- Lighting blowout/murky shadows: PBR exposure and real rendered-frame review.
- Occluded/missing character parts: topology/alpha/pose checks; not solved.
- Temporal continuity loss: per-frame owned asset identity and shot-state locks.
- No engine playback: receiver-side import and timing tests must be added.

## 14. Evaluation

Measure: shots generated, camera-cut marker count, frame coverage, no timeline
overlaps, camera AABB clearance, subject-visible fraction and silhouette bbox,
frame-to-frame motion smoothness, velocity/acceleration/jerk, identity locks,
bone lengths and skin weights, PBR material round trips, render file/bytes,
reproducibility, load/render time, real receiving-engine playback quality.

## 15. Placement and contracts

- `forge/cinematic.py`: world-backed camera positions, clearance-aware.
- `forge/shot_design.py`: lighting and shot validation.
- `forge/director.py`: frame range, cuts, easing and sampled motion.
- `bridge/blender_cinematic.py`: materialize actual cameras, timeline markers,
  keyframes, lights, `.blend`, render and receipt.
- `forge/pose_guardian.py`: current limited skeletal checks; not cinematic QA.
- `forge/creation_memory.py`: identity/continuity locks for later consumers.
- `docs/BUILD-REGISTER.md`: acceptance states, no fabricated completeness.

## 16. Acceptance tests / remaining research queue

**Implemented tests:** invalid reels, duplicate shots, finite coordinates,
no camera inside authored building, monotonic nonoverlapping cuts, frame-rate
bounds, smooth interpolation endpoints, actual Blender CPU rendered shot.

**Still required before production:** visual subject framing score, tracking
constraints, animated dolly/crane/orbit proof, depth of field and lens
comparison, subject occlusion, camera/actor moving collision, 10+ shot
continuity regression, actual multiframe render/clip export, FPS/audio sync,
real skeletal walk and film/game engine import validation.

The current director foundation is **not complete cinematography intelligence**.
New capability subbranches go back into this file and `docs/BUILD-REGISTER.md`.
