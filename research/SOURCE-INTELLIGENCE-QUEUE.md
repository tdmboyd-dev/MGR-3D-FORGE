# MGR Forge — 24-source Production Intelligence Register

Owner: MGR. Updated: 2026-10-25. **The owner supplied SIGGRAPH plus twenty-three numbered targets: 24 distinct research branches.** This is additional research, not a substitute for the 20 scientific domain chapters. External names appear here solely to define technical audit targets; MGR owns every product capability and name. Detailed external links, original author credit, rights and repository revisions belong in `research/external-provenance/`.

## Scope, tracked honestly

| ID | External research target | Highest-priority MGR learning | Research state | Production state |
|---|---|---|---|---|
| R01 | SIGGRAPH papers/courses | 3D graphics, light transport, VFX/geometry, latest methods | SELECTED PRIMARY PAPERS AUDITED | Native reference parity open |
| R02 | NVIDIA Research | neural rendering, shader/GPU performance, world models | SELECTED PRIMARY PAPERS AUDITED | Model/license/compute tests open |
| R03 | Pixar papers | subdivision, hair simulation, scene composition | SELECTED PRIMARY PAPERS AUDITED | Smooth body/hair parity open |
| R04 | Disney Research | measured materials, cloth/hair, shot control | SELECTED PRIMARY PAPERS AUDITED | Light/garment/FX parity open |
| R05 | Unreal Engine source code | streaming, virtualized mesh, lighting, gameplay | PUBLIC API/STRUCTURE AUDITED; PRIVATE SOURCE ACCESS OPEN | Actual independent runtime open |
| R06 | Blender source code | actual operators, geometry, rendering, API internals | SELECTED PUBLIC SOURCE ENTRIES AUDITED | Scoped Blender integration ongoing |
| R07 | OpenGL specification | rendering precision/state, shader interoperability | SELECTED SPEC SECTIONS AUDITED | Renderer conformance open |
| R08 | Vulkan specification | explicit GPU/memory/queue/sync contracts | SELECTED SPEC SECTIONS AUDITED | Vulkan runtime proof open |
| R09 | DirectX documentation | Windows GPU feature/perf admission and diagnostics | SELECTED OFFICIAL DOCS AUDITED | Direct3D runtime proof open |
| R10 | Unity docs/source | scene, animation, streaming, material interoperability | SELECTED OFFICIAL DOCS AUDITED | Unity import/runtime proof open |
| R11 | NASA visualization research | imagery provenance, scientific data and large-scale scene accuracy | SELECTED OFFICIAL APIS/DATA AUDITED | Scientific scene comparisons open |
| R12 | CERN visualization research | measurement/geometry/particle simulation concepts | SELECTED OFFICIAL FRAMEWORKS AUDITED | Physics visualization bridge open |
| R13 | MIT OpenCourseWare | math, geometry, numerical dynamics, perception | SELECTED COURSE MATERIAL AUDITED | Algorithm correctness curriculum open |
| R14 | Stanford Graphics Lab | image reconstruction, light fields, geometry | SELECTED PAPERS/TOOLS AUDITED | Cross-view geometry proof open |
| R15 | Carnegie Mellon Robotics | robot perception, locomotion, kinematics and spatial maps | SELECTED PAPERS/TOOLS AUDITED | Avatar motion and SLAM tests open |
| R16 | Berkeley AI Lab | vision/world models, control, generative 3D | SELECTED PAPERS/TOOLS AUDITED | Evaluated open models open |
| R17 | DeepMind papers | world simulation, temporal consistency and generative agents | SELECTED PUBLIC PAPERS AUDITED | World continuity/control proof open |
| R18 | OpenAI research | visual synthesis and generative simulation research | SELECTED PUBLIC PAPERS/CODE AUDITED | Model-capability boundary and provenance open |
| R19 | Meta Reality Labs | codec avatars, tracking, VR presence and 3D capture | SELECTED OFFICIAL PAPERS/SDK AUDITED | Headset/camera tests open |
| R20 | Apple ARKit research | AR anchor, tracking, depth fusion and mobile limits | SELECTED OFFICIAL DOCUMENTATION AUDITED | Real-device drift/depth proof open |
| R21 | Academic journals | peer-reviewed 3D, graphics, optics, physics and biomechanics | EIGHT SELECTED PAPERS AUDITED | Reproduced comparative experiments open |
| R22 | Patent databases | prior-art and lawful implementation discovery | SEVEN REPRESENTATIVE FAMILIES REVIEWED; LEGAL CLEARANCE OPEN | Patent counsel/rights checkpoint open |
| R23 | Game Developer Conference talks | Game-specific production tricks, profiling, gameplay/world shipping | SELECTED SESSION/SLIDE AUDIT; FULL TALKS NOT ALL AVAILABLE | Game production profiling proof open |
| R24 | Major VFX studio breakdowns (Weta, ILM, DNEG) | Film-quality creatures, FX, lighting, simulation and shot review | SELECTED FIRST-PARTY BREAKDOWNS FOR ALL THREE AUDITED | Production-equivalent shot tests open |

**Important:** GDC and major VFX studios are separate source families. The latter needs distinct Weta, ILM and DNEG branches rather than one generic summary. Academic journals and patent databases also have separate R21/R22 entries.

## Completion gates for EACH source

1. Authoritative source URL and original author/maintainer, date and exact version or repository revision when available.
2. Actual inspected depth: catalog/abstract, full paper, documentation, source file, or executed code; identify gaps.
3. 3–5 high-value discoverable algorithms or production patterns, with formulas/data structures and counterexamples when possible.
4. Tools, model/data rights, license, patents, and legal/technical restrictions kept separate from proposed MGR design.
5. MGR-native feature mapping to existing F/N capability, runnable fixture, negative test, CPU/GPU/cost and quality metric.
6. Reproduction, independent implementation, Windows Blender/backend acceptance and owner approval reported independently.

Research may mark **AUDITED** once those source-depth fields are real. It may NOT mark the resulting product feature verified until code, tested artifacts and actual runtime receipt exist. Do not try to read the entirety of every institution's published output as a false prerequisite for shipping Tevin.

## Work batches

- Batch A: R01–R10, five concurrent pairs plus native code/build/testing. Each pair writes separate source-specific technical chapter and provenance ledger.
- Batch B: R11–R20, five concurrent pairs plus implementation.
- Batch C: R21–R24 as four substantial branches with multiple sub-source investigations, alongside source-code proof and 3D visual benchmarking.

**Research packet audit status:** R01–R24 all have an individual selected-technique paper/spec/source/production report and separately traceable external evidence ledgers. This is **24/24 scoped research reports**, not an exhaustive read of every institution's corpus, every patent claim, proprietary source, or executable production stack. The acceptance tests in their reports are an implementation queue, not already green.

All source-specific research chapters live under `research/source-audits/`; they provide evidence to `research/MGR-STUDIO-TO-NATIVE-ENGINE-LESSONS.md`. `docs/BUILD-REGISTER.md` continues to own the code state; `docs/PROGRESS-LOG.md` owns the chronology.
