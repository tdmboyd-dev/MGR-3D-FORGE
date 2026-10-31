# External origin / rights ledger — MGR Source Atlas, 2026-10-30

This is **not** a product naming system or a grant of commercial reuse rights.
MGR's canonical runnable provider inventory is `forge/data/asset_sources.json`.
MGR's creative capabilities live under `docs/MGR-NATIVE-CANON.md`; no external
service defines what MGR Forge can ultimately create.

## Checked primary source facts

| Source | Primary evidence | Decision | Real boundary |
|---|---|---|---|
| 3DAssets.dev | https://3dassets.dev/docs/api and https://3dassets.dev/docs/mcp | ADAPT as read-only searchable GLB source; bounded direct download | Site asserts CC0, but attribution/source rights remain asset-level assertions. API and actual dragon GLB checked, not Blender visual quality. AI generated flag retained. |
| Poly Haven | https://polyhaven.com/license and https://polyhaven.com/uk/our-api and https://github.com/Poly-Haven/Public-API/blob/master/swagger.yml | ADAPT official live search for models, textures, HDRIs; no raw package imports yet | Assets CC0; using live API requires visible Poly Haven source credit and specific User-Agent. Actual model and texture searches checked. |
| ambientCG | https://docs.ambientcg.com/license/ and https://docs.ambientcg.com/api/ | NEXT: material/HDRI source adapter | Recheck exact API download semantics and texture set integrity before import. |
| MakeHuman / MPFB | https://www.makehumancommunity.org/about/license.html and https://extensions.blender.org/add-ons/mpfb/ | NEXT: character-shape/body/skin generator | Core asset/data CC0, software has separate GPL/AGPL obligations, third-party packs separate. Do not embed copyleft code indiscriminately. |
| Kenney | https://kenney.nl/support | NEXT: modular game kit import | Asset pages described as CC0; confirm per-pack license and component inventory. |
| Quaternius | https://quaternius.com/license.html | STUDY/ADAPT for finished products, **reject raw redistributable vault mirroring** | Current QAL v1 (2026-08-28) prohibits standalone asset resale/redistribution even when modified. Older pack/license copies may differ, so record acquisition version. |
| Smithsonian Open Access | https://www.si.edu/openaccess/faq | NEXT: per-object public-domain 3D scans | Confirm actual object's CC0 metadata; not every Smithsonian object is automatically open. |
| OpenGameArt | https://opengameart.org/content/faq | STUDY; per-file/license gate | Mixed CC0, attribution and other license terms. Never treat entire site as CC0. |
| Poly Pizza | https://poly.pizza/docs/tos | STUDY; per-file/license gate | Creative Commons license is attached to each upload, not a single site-wide unconditional rights grant. |
| Blendkit | https://www.blendkit.com/docs/licenses/ | STUDY; per-file/license gate | CC0 and royalty-free differ; royalty-free assets cannot be repackaged as standalone models. |
| Sketchfab | https://sketchfab.com/licenses | STUDY; per-file/license gate | Asset/use/trademark/person restrictions and no raw resale on some licenses. |

GitHub, Hugging Face, Godot Asset Library, Blender Extensions, Objaverse and
Mixamo are **candidate discovery surfaces**, not licensed bulk-download sources.
Each chosen repo/checkpoint/weight/dataset/asset needs its own source, version,
license and use-rights review before integration. Do not mirror their catalogs.

## Source format and proof boundaries

- Search results are `CACHED_SOURCE_METADATA`: they identify potential files,
  not accepted, fitted, rigged or visually verified assets.
- Local 3DAssets.dev GLB intake is `QUARANTINED_RIGHTS_AND_QUALITY`. It validates
  a bounded glTF 2.0 container, its content hash and original URL. It is **not**
  a full glTF validator, rights adjudication, body/face identity test or Blender
  import proof. It cannot be published as a new raw asset store by default.
- The external license and origin stay on the model record. No user-private
  character likeness, purchased kit, model weights or credentials enter Git.
- API failures and changed CDN URLs do not silently replace prior catalog data.

## Evidence and next work

- Live model search: dragon → two official 3DAssets.dev metadata results.
- Explicit small-file intake: dragon GLB 198,252 bytes, six mesh containers,
  `KHR_mesh_quantization`, SHA in `evidence/asset-atlas/2026-10-30-proof.json`.
- Live Poly Haven: rock → two real models, leather → two real textures, CC0
  provider claim and `Powered by Poly Haven` API use credit carried forward.
- Next: expand source adapters (not just static directory entries), review exact
  file rights, sample independent engine import/visual QA, asset placement,
  human/creature morph/skin/rig factory and selective kit extraction.
