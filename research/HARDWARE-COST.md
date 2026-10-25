# CPU/GPU, Latency, and Cost Research

Updated 2026-10-25. All numbers from vendor/project claims unless flagged as MGR measurements. **No MGR measurements yet.**

## Key question

Can MGR own a useful 3D creation system without a discrete GPU? **Yes for modeling, procedural worlds, assembly, test and some CPU inference.** Can it match frontier high-detail generative models on a CPU at practical turnaround? **Unproven and unlikely with currently reviewed model requirements.**

## Workload split

| Workload | CPU-only | GPU role | Proof |
|---|---|---|---|
| World graph, zoning, roads, heightfields, building grammar | Yes | optional visualization | Deterministic algorithm/Blender |
| Blender mesh editing, rig validation, glTF export | Yes | viewport/render acceleration | Blender API |
| Asset indexing, dedupe, provenance, validation | Yes | optional embedding inference | Standard compute |
| TripoSR single image -> draft mesh | Supported fallback | Default ~6GB VRAM | Project README/CPU flag |
| TripoSG image -> shape | Not yet proven practical | >=8GB CUDA GPU stated | Project README |
| TRELLIS.2 4B image -> PBR mesh | Not supported by published stack | NVIDIA >=24GB, Linux tested | Microsoft README |
| Hunyuan3D 2.1 shape + texture | CPU practicality unknown | 10GB shape, 21GB texture, ~29GB combined | Tencent README |
| HY-World 2.0 high-quality world generation | No verified CPU path | CUDA and potentially multi-GPU for some stages | Tencent README |
| LLM prompt -> scene specification | CPU possible with smaller model / rule engine | accelerator for larger LLM | Depends on model |
| Game runtime rendering / 3DGS | CPU may render slowly or limited | GPU desirable for real-time scene | Must benchmark target |

## Three modes

1. **GPU-free base**: scene planner, procedural terrain/roads/buildings/rooms, asset reuse, Blender background mode on CPU, collision metadata, GLB export, deterministic checks. No promise of neural photorealism.
2. **Local hybrid**: above plus small image-to-3D model if enough RAM/VRAM and dependencies compatible. Latency budget must be measured, including first load.
3. **Elastic quality**: call explicitly approved ephemeral GPU worker only for hard textures, organic sculpt, world reconstruction/generation; export assets once and reuse forever. Budget and stop at provider boundary.

## Cost accounting

True cost per **accepted** asset = (GPU minute charges + CPU energy/time allocation + API credits + storage/network + postprocessing labor + failed attempts + retries) / count of assets accepted by matching quality criteria.

Compare alternatives with same input set and required export quality. Track P50/P95 wall time, peak VRAM/RAM, CPU/GPU minutes, first-load time, geometric errors, texture quality, rig success, reviewer acceptance, and end-to-end cost.

### Hosted baseline (not native target)

Tripo API: public pricing lists 10–30 credits for common H-series text/image generation; 1 API credit ~$0.01 in USD-facing docs. Studio subscription credits are separate from API credits. Hyper3D Rodin: base 0.5 credit per generation and direct credits $1.50/credit; Business API plan $120/mo listed. Subscription inclusion and extra processing alter economics. Verify before benchmarking: https://developers.tripo3d.ai/en/pricing ; https://hyper3d.ai/pricing ; https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5 .

## Research needed

- Exact available user hardware: GPU(s), VRAM, CPU threads, RAM, disk, OS, Blender runtime.
- Small model on CPU: test TripoSR with CPU, fixed resolution, 3 repeat trials; log memory/time/quality.
- CPU procedural benchmark: 100 / 1,000 / 10,000 buildings with instance vs realized meshes, export size, scene open time.
- GPU tiers: 8/12/16/24/48GB, with legal weights, actual latency and postprocessing quality. Do not assume VRAM threshold equals good performance.
- Smaller/quantized models, inference runtimes, pruning/distillation — legal training and derivative rights first; benchmark quality degradation.
- Cloud GPU costs: only obtain current quotes for an approved region/provider and include idle/setup/data transfer overhead.

## STOP gates

No purchase, cloud worker launch or heavy model download without an exact plan, license review and cost confirmation. Do not claim GPU-free entire world generation from public 3DGS demos. Do not present research author benchmarks from H100 as consumer hardware predictions.
