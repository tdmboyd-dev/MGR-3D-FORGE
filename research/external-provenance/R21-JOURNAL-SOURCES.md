# R21 — Eight Selected Peer-Reviewed Journal Sources: External Provenance

**Date:** 2026-10-25 · **Inspection:** Publisher journal pages, original authors' pages and selected openly available full text. **Sample only**; no systematic all-journals search, peer-review reproduction, full code audit, benchmark reproduction or asset license clearance. Technical interpretation and MGR-native test derivation: `research/source-audits/R21-ACADEMIC-JOURNALS.md`.

| # | Primary paper / journal | Finding established from source | Inspection/caution |
|---|---|---|---|
| J1 | David G. Lowe, [Distinctive Image Features from Scale-Invariant Keypoints](https://doi.org/10.1023/b:visi.0000029664.99615.94), *International Journal of Computer Vision* 2004; [author's SIFT resource](https://www.cs.ubc.ca/~lowe/keypoints/) | Scale/rotation-resistant local image features for robust matching. | Journal publication/authored project page. SIFT matches images, not exact hidden 3D geometry; do not copy patented-era historical implementation without current rights assessment. |
| J2 | Hoffman, Girshick, Akeley and Banks, [Vergence–accommodation conflicts hinder visual performance and cause visual fatigue](https://pmc.ncbi.nlm.nih.gov/articles/PMC2879326/), *Journal of Vision* 2008 | Controlled psychophysical evidence of depth/focus conflict affecting visual performance/fatigue. | Open full text and [PubMed record](https://pubmed.ncbi.nlm.nih.gov/18484839/); device/user specificity matters. |
| J3 | Kerbl et al., [3D Gaussian Splatting for Real-Time Radiance Field Rendering](https://doi.org/10.1145/3592433), *ACM Transactions on Graphics* 2023; [authors' project](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) | Optimized anisotropic Gaussian primitives and visibility-aware rendering support real-time view synthesis in paper's setting. | Journal/author project; do **not** equate splat appearance with rig, collision or complete metric surface. Check original repo licensing before using code/weights. |
| J4 | Radl et al., [StopThePop: Sorted Gaussian Splatting for View-Consistent Real-Time Rendering](https://doi.org/10.1145/3658187), *ACM Transactions on Graphics* 2024 | Sorting and view consistency address popping/artifacts in transparent Gaussian blending. | Journal page/abstract. Temporal QA still needed on MGR hardware and camera routes. |
| J5 | Bender, Müller, Otaduy, Teschner and Macklin, [A Survey on Position-Based Simulation Methods in Computer Graphics](https://doi.org/10.1111/cgf.12346), *Computer Graphics Forum* 2014; [authors' archive](https://animation.rwth-aachen.de/publication/0512/) | Constraint projection and position-based physics families for interactive deformations. | Peer-reviewed **survey**, not a novel experimental method or proof of unconditional physical accuracy. |
| J6 | Delp et al., [OpenSim: Open-Source Software to Create and Analyze Dynamic Simulations of Movement](https://pubmed.ncbi.nlm.nih.gov/18018689/), *IEEE Transactions on Biomedical Engineering* 2007 | Articulated musculoskeletal dynamic model and simulation exchange framework. | Original biomedical journal metadata/abstract; individual example body datasets have distinct license/consent issues. |
| J7 | Rajagopal et al., [Full-Body Musculoskeletal Model for Muscle-Driven Simulation of Human Gait](https://pmc.ncbi.nlm.nih.gov/articles/PMC5507211/), *IEEE Transactions on Biomedical Engineering* 2016 | Model validated against measured biomechanics/muscle activity in stated population and setup. | Open full text/[PubMed entry](https://pubmed.ncbi.nlm.nih.gov/27392337/). Cannot extrapolate study error ranges to an uncalibrated fictional avatar. |
| J8 | Hedman et al., [MERF: Memory-Efficient Radiance Fields for Real-Time View Synthesis in Unbounded Scenes](https://doi.org/10.1145/3592426), *ACM Transactions on Graphics* 2023 | Baked efficient representations can enable faster view synthesis with reported paper-specific quality. | Journal abstract/paper listing; no independent implementation speed or memory benchmark. |

## License and empirical-evidence boundaries

1. A publicly readable journal paper is **not** a blanket license to redistribute data, reference captures, experimental human scans, character meshes, medical datasets, code or trained model weights.
2. The open-access licenses of each PDF and attached supplementary material may differ from associated code/data repositories; review each exact distribution artifact separately.
3. Perceptual research (J2) requires participant ethics/privacy for new human-subject experiments. Biomedical studies (J6/J7) involve sensitive human-related data and cannot be used to make medical-grade claims for a fictional rig.
4. PBR/gaussian/radiance field methods' quality/speed claims are configuration-specific. GPU, scene, camera coverage, data capture and image resolution change applicability materially.
5. Mathematical expressions in the MGR paper report are conceptual reproductions/generalizations for engineering witnesses, not verbatim attributions that every journal paper used that exact parameterization.
6. The sample is spread across optics/perception, computer vision, rendering, simulation and biomechanics. Additional physically based light/volumetric and newer dynamic-world journals should be studied when tied to a specific Forge acceptance gap, with source provenance appended here.

## MGR source-to-proof chain

```
paper claim → independent equation/assumptions → MGR-owned synthetic witness →
measured acceptance/failure envelope → separately coded adapter → production evidence
```

**Recommended first tests:** (a) image feature match inliers versus known pose/occlusion; (b) Gaussian splat order and view-pop stability; (c) coat/cape constraint penetration under varied timestep; (d) skeleton/gait pose ground contact with numeric residuals; (e) eye-disparity and true-device comfort separation. No production result is asserted by citation alone.
