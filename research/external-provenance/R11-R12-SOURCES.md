# Source evidence and rights ledger — NASA (R11) / CERN (R12)

**Inspected date:** 2026-10-25. NASA and CERN primary pages, official API/developer manuals, direct upstream README/source snippet and published licenses. **Not** a complete catalog, downloaded dataset/source archive, executable proof or counsel opinion. Source aliases map to MGR-native architectural research in `research/source-audits/R11-NASA.md` and `R12-CERN.md`.

## R11 — NASA/JPL and related project evidence

| Source / exact first-party location | Inspected technical substance | Depth and limitations | Use/rights gate |
|---|---|---|---|
| JPL/NAIF SPICE reference frames — https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html | Inertial/body-fixed/spacecraft clock-based/fixed-offset frames; transformation dependencies | Reference manual sections; **not** full C Toolkit source read or test | Kernel files/software terms require release-specific inspection |
| JPL SPICE geometry finder — https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/gf.html | Find intervals for geometric event predicates | Algorithm overview/API descriptions; no code executed | Independent native geometric predicates and own tests |
| JPL SPICE kernel concept — https://naif.jpl.nasa.gov/naif/spiceconcept.html | Mission navigation/observation geometry stored in source kernels | Project explanation; ephemeris accuracy not validated by MGR | Kernel metadata and source provenance mandatory |
| JPL SPICE tutorials — https://naif.jpl.nasa.gov/naif/tutorials.html | Official frame/time geometry worked tutorial index | Listed exercises, not fully worked locally | Tutorial diagrams not copied |
| NASA OpenSpace project — https://science.nasa.gov/sciact-team/openspace-project/ | Interactive universe across scale/time/angle with data and simulation | NASA summary, not implementation source audit | Scientific data linked separately; no asset import |
| OpenSpace upstream — https://github.com/OpenSpace/OpenSpace | Official astrovisualization source; published MIT license | README/license declaration only, dependencies not audited | MIT core with notices; exact assets/plugins separate |
| NASA Eyes — https://science.nasa.gov/eyes/ | Browser-based 3D explorations grounded in spacecraft/planetary mission context | Product documentation, not source/renderer audit | NASA data licensing per mission/source |
| NASA Eyes FAQ — https://science.nasa.gov/eyes/faq/ | Browser-based application/access route | Official FAQ only | No claim browser code open source |
| NASA Scientific Visualization Studio — https://svs.gsfc.nasa.gov/ | Scientific imagery, animation and data-backed outreach; public domain except stated exceptions | Official studio site; not all SVS projects audited | Per-asset exception and third-party credit/rights check |
| NASA SVS help/format — https://svs.gsfc.nasa.gov/help/ | Source media/frames and visualization metadata/format documentation | Official format/asset overview | Check media usage and source dataset provenance |
| NASA LRO-derived Moon 3D 2026 models — https://svs.gsfc.nasa.gov/14959/ | LRO imagery/topography-derived meshes for web/AR/animation | One item-level source description, no models downloaded | Individual file rights, topography datum, resolution |
| NASA CGI Moon Kit — https://svs.gsfc.nasa.gov/4720 | Color/displacement map workflow and explicit source scientific data caution | One original animation project explanatory notes | Generated appearance ≠ survey precision |
| NASA brand-use rules — https://www.nasa.gov/nasa-brand-center/ | Insignia/logotype/identifiers protected, no implied NASA commercial endorsement | Official use policy | Never add NASA logos/brand to MGR commercial marketing without required permission |

## R12 — CERN / ROOT / Geant4 primary evidence

| Source / exact first-party location | Inspected technical substance | Depth and limitations | Use/rights gate |
|---|---|---|---|
| ROOT Geometry manual — https://root.cern/manual/geometry/ | TGeoManager volume hierarchy, navigation, nested overlaps rules | Official technical manual, not complete source tree | Optional comparison only |
| ROOT TGeoManager — https://root.cern/doc/master/classTGeoManager.html | Navigator/geometry path, containment, top volume rules and overlap checking | Exact official API class docs and published behavior; no runtime | Own MGR fixture tests must establish defect detection |
| ROOT TGeoChecker — https://root.cern/doc/master/classTGeoChecker.html | Sampling/geometric overlap checking, implementation knobs | Class docs, no algorithm end-to-end audited | Quantify miss rate, check tolerances |
| ROOT REve — https://root.cern/doc/master/group__REve.html | Modern web-based interactive event display manager | API reference docs; app/server not installed | Design idea, not copied UI code |
| ROOT REve tutorials — https://root.cern/doc/master/group__tutorial__eve__7.html | Geometry browser, 3D event primitives examples | Tutorial names/entrypoints inspected, not executed | No claim cross-browser support tested |
| ROOT license — https://root.cern/about/license/ | LGPL version 2.1-or-later official grant | Published exact license class, no legal determination for MGR linking | Preserve notices and satisfy LGPL requirements if integrating |
| CERN CMS event display — https://opendata.cern.ch/visualise/events/CMS | Browser 3D iSpy event data; `.ig` file event collections | Actual event display documentation; did not download events | Record-level data rights required |
| CERN Open Data sample event — https://opendata.cern.ch/record/628 | JSON browser event data based on CMS collision set | Item-level metadata lists CC0 1.0; actual file not inspected | No assumption all CERN datasets CC0 |
| Geant4 general project — https://geant4.web.cern.ch/ | Scientific particle passage-through-matter simulation toolkit | Homepage/overview only, not local install | Custom Geant4 software license |
| Geant4 developer visualization overview — https://geant4.web.cern.ch/documentation/dev/bfad_html/ForApplicationDevelopers/Visualization/introduction.html | Physics/event render separation, selectable graphics drivers | Official developer technical sections | Drivers may need optional packages/build |
| Geant4 drivers — https://geant4.web.cern.ch/documentation/dev/bfad_html/ForApplicationDevelopers/Visualization/visdrivers.html | OpenGL, OpenInventor, DAWN etc. output differences | Driver docs, not build test | No promise all backends installed |
| Geant4 executable integration — https://geant4.web.cern.ch/documentation/dev/bfad_html/ForApplicationDevelopers/Visualization/visexecutable.html | Graphics visualization support compiled optionally | Developer guide; no runnable binary check | Driver dependency audit |
| Geant4 source basic example — https://github.com/Geant4/geant4/blob/master/examples/basic/B1/exampleB1.cc | Original demo source header/licensing and simulation entrypoint context | Selected public source file header, **not** full simulation algorithm audit | Respect Geant4's custom terms |
| Geant4 license text — https://github.com/Geant4/geant4/blob/master/LICENSE | Geant4 Software License 1.0 and conditions | Official license inspected, not counsel opinion | Custom notices/acknowledgments/terms before any library embedding |

## Rights distinctions

1. NASA data/product content can frequently be reused, **but** NASA's official SVS states exceptions, and NASA insignia/logotype/identifiers and endorsement claims have separate restrictions. Third-party imagery/model rights may be present.
2. OpenSpace upstream is MIT per official project; SPICE kernels/Toolkit may have their own release-specific notices. A NASA webpage is not a blanket right to proprietary code or personal likeness use.
3. ROOT is LGPL-2.1-or-later; Geant4 has its own versioned software license; CERN event records may carry CC0 or another individual dataset license. Never conflate these.
4. Neither NASA's orbital trajectories nor CERN's particle transport are automatically valid physical models for fantasy terrain, humans, fluids or magical energy. MGR should adapt evidence/geometry disciplines, not mislabel scientific simulations.

## Research maturity and next verifications

**Inspected:** primary manuals, technical API pages, README/license pages and selected item-level NASA/CERN asset data descriptions. **Not inspected:** full software source tree, real datasets/model geometry, exact Windows build, numerical benchmark runs, all NASA/CERN visualization branches or every legal exception. Next tests: native reference-frame composition, time event root-finding including tangencies, massive-scale camera precision, data-driven heightmap QA, nested-volume overlap stress, event-state/render independence and physics conservation/ray interactions. Publish measurements and license receipts before claiming production integration.
