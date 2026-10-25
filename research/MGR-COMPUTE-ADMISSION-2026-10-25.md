# MGR Compute Admission — Owner Laptop Evidence

**Date:** 2026-10-25. **Source:** read-only hardware inventory run through the owner-authorized Windows machine. **Type:** factual local hardware snapshot, not a neural benchmark.

## Observed configuration

- Device reports `Dell XPS 13 9305`.
- GPU name reported by Windows: **Intel Iris Xe Graphics**.
- Windows `Win32_VideoController.AdapterRAM` reported **2,147,479,552 bytes** (~2 GiB). **Important:** integrated GPU shared-memory reporting is not a reliable dedicated-VRAM guarantee. Do not convert this property into confirmed usable dedicated GPU memory.
- Installed physical RAM reported **16,889,540,608 bytes** (~15.73 GiB).
- CUDA-capable NVIDIA device **not observed** in the video-controller query. This is not a comprehensive machine-learning backend audit.
- Blender **5.2.2 LTS** and CPU procedures were independently tested on this PC.

## Native decision

Keep geometry generation, Blender scripts, GLB QA, rigging smoke tests, image pixel QA and world path rehearsal local by default. Do **not** automatically pull large neural 3D checkpoints onto this laptop. Candidate adapters must demonstrate their exact backend, model-weight licensing, actual RAM/VRAM requirements, installer safety and an owner-authorized compute budget.

`forge/hardware.py` now implements the conservative admission decision. It does not launch models, install drivers or guess a CUDA runtime. When GPU resources are missing or uncertain, the engine recommends a CPU path or a separately reviewed optional worker—not automatic paid/API execution.

## Completion gap

Benchmark small CPU-capable neural options if available; validate physical RAM under sustained rendering; inventory graphics/compute runtimes without modifying Windows drivers; test commercially permitted model weights under approved isolated workers. Any future model-locality decision must be backed by measured inference receipts.
