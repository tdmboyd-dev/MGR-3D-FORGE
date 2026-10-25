# R16 — MGR interpretation of Berkeley AI and robotics research

**Audit:** 2026-10-25. Research confined to primary Berkeley AI Research (BAIR) posts and UC Berkeley academic/project publication pages. Focus: perception-to-action loops, world prediction, tactile truth, moving-body first-person viewpoint and active 3D capture. Scholarly provenance/rights are separately mapped in [R15–R16 sources](../external-provenance/R15-R16-SOURCES.md). No outside code or weights imported.

## Five techniques with direct MGR benefits

| Original research finding | Native MGR capability | What to implement / measure |
|---|---|---|
| Tactile model-predictive control (“Manipulation By Feel”) combines predictive visual dynamics and touch to control contact-rich tasks | **Contact Truth** | Physics/material interactions should use contact force, friction and motion feedback where known; simulated contact fixture checks slip/penetration, not just visual overlap |
| Whole-body-conditioned egocentric video prediction considers hands/feet and expected first-person images | **Body-to-View Clock** | World camera forecast must agree with locomotion + hand/foot/pose and constraints; evaluate next-frame prediction and skeletal/scene contact in held-out motion |
| Gradient-based longer-horizon planning for world models predicts states and optimizes action sequences | **Outcome Rollout Director** | Simulate multiple short/long plans before committing scene/NPC action, recording uncertainty; evaluate rollout error, collision safety and long-horizon stability |
| Fixed-camera bimanual robot scanning with Gaussian splats/object inspection (“Omni-Scan”) uses controlled object handling/views to gather better 3D evidence | **Capture Orbit Planner** | Optimize view selection and occlusion coverage for character/prop scanning; evaluate newly observed surface gain and same-object pose consistency |
| One-shot imitation from human video uses task/meta-learning to adapt behavior from demonstrations | **Demonstration-to-Motion** | Convert lawful, consented references into editable intention and joint/trajectory proposals, then enforce biomechanical/rig limits and pose identity consistency |

## Core product architecture

Keep prediction and control distinct. An `Observation` is frame/depth/rig state/contact with timestamp and sources. A `WorldState` is physical/semantic and camera-relative truth. A `Predictor` produces *hypothesized* next state/visual frame plus uncertainty. A `Planner` tests bounded candidate actions against collisions, movement constraints and scene budgets. An `Executor` applies only approved commands and compares actual result to prediction. A `CorrectionLoop` updates the estimate without rewriting what was actually observed.

This is useful beyond physical robots: film directors anticipate a camera shot; NPCs plan plausible movement; generated characters maintain real anatomical contact; virtual world builders decide where to acquire the missing camera angles. Model output must never be mistaken for geometry measured by a real camera.

## Five high-value implementation experiments

1. **Tactile illusion test:** simulated hand grasps solid vs slippery prop with same image; physics/contact feedback must distinguish behaviors and fail collision penetrations.
2. **Whole-body prediction:** 20 diverse movements (walk, jump, reach, pivot, bend, descend stairs), compare predicted camera and body poses to ground truth over 1/5/30 steps.
3. **Rollout planning:** NPC chooses route around moving obstacle; report safety, success and runtime vs deterministic short-horizon baseline.
4. **View planning:** a multi-angle prop/Tevin scan planner proposes missing undersides/back-of-hand views; measured surface coverage improves vs fixed 4-angle baseline.
5. **Imitation adaptation:** one authorized reference gesture transfers to a rig with different limb proportions without wrist inversion, floor penetration or identity drift.

## Model/data/hardware decisions

Start with deterministic physics/IK, kinematic simulation, trajectory optimization and camera geometry before costly training. Predictive video diffusion/learned action dynamics is optional GPU-intensive work; there are meaningful cheap CPU tests for collision, constraints and view coverage. No specific Berkeley model checkpoint, dataset or repo was proven commercially redistributable by this packet. Body/face videos and physical observation datasets need subject rights. A rendered demonstration video may omit crucial 3D forces or occluded gestures; uncertainty and artist corrections are mandatory.

## Independent MGR invention opportunities

**Intent-to-Act Chain:** combine director shot plan, embodied character desire, physically constrained pose and camera-visible outcome, with reversible timeline edits.

**Reality Feedback Judge:** compare predicted view/collision to actual rendered and simulated result; file a localized repair for just the faulty world part.

**Active Imagination Scanner:** identify which next capture/view/pose would reduce uncertainty most, rather than constantly generating unverified front-side images.

## Risks / legal and evaluation boundaries

- Research publications/blogs are not implementation licenses; paper experiments may use custom sensors/robots and selected lab data that cannot be reproduced on a laptop without substitutes.
- Predictive visual consistency is not physical truth; report both video quality and world-state/collision error.
- Complex world models can hallucinate object permanence, new limbs, garment continuity and causal events; audit them across hidden views/time.
- Actual tactile hardware is not needed for simulated contact experiments, but physical sensor claims require real instrumentation.
- Respect authorship and people in training/demonstration videos; do not turn a random online performance into unlicensed commercial animation assets.

**Status:** 5 method-to-native translations and 5 benchmark fixtures specified; these are open build/test gates, not preexisting passing claims.
