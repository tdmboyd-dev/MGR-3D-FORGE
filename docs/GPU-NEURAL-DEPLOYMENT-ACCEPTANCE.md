# MGR 3D Forge — Neural GPU and hosted-Forge deployment acceptance (source truth)

Last verified 2026-10-31. Keep this as an execution acceptance specification UNDER the existing one docs/HANDOFF.md, not a new independent product or replacement Forge.

## What is actually available

The same MGR Forge repo already has forge/generative_backends.py, forge/data/generative_engines.json, forge/gpu_rental.py, forge/gpu_packer.py, forge/hardware.py, forge/gpu_lifecycle.py and forge/adapters.py. The first is a preflight, the planner provides no-spend quotes, and candidate profiles are NOT downloaded models. Current source records 16 engines, with native CPU procedural imagination the sole runnable backend. SkinTokens, NVIDIA Audio2Face-3D, TRELLIS.2, Pixal3D, Hunyuan 3D and other public/hosted models are NOT installed, with model/data/dependency rights unaccepted.

Owner Windows workstation observed Intel Iris Xe integrated graphics and no nvidia-smi/CUDA provider. Large 3D neural checkpoint requirements (14GB+ and sometimes 24GB+ NVIDIA VRAM) are not satisfied. Do not attempt costly model installations locally or mislabel a CPU procedural mesh as Meshy/Tripo-quality neural inference.

## Correct product integration

The existing MGR-API-MCP repository owns the real authenticated web/MCP boundary: src/http-server.ts, src/mcp-http.ts, src/jwt-verifier.ts, src/forge-catalog-client.ts and src/forge-mcp-tools.ts. It already supports a trusted HTTPS Forge service URL at the client contract, and the local Forge Studio only listens on 127.0.0.1 with strict matching local Host. Setting an HTTPS URL in config does NOT create a deployed worker, secure relay, shared storage or accessible 3D GPU.

Hosted topology should have ONE MGR API/MCP auth/tenant scope and ONE Forge-native job/vault/receipt owner. For trusted remote execution, build a genuinely authenticated provider-hosted Forge worker or a secure **outbound** pull worker from the owner workstation, with tenant-scoped signed job leases, idempotency, cost caps, revocable artifact transport and private object storage. Avoid exposing the loopback Studio and its permanent bearer token to the internet, hardcoded VPN credentials or a second independent app queue.

## Activation gates, in order

1. Select one legally usable upstream code revision and EXACT weights/checkpoint/card/dataset dependencies. Preserve publishers, nested folder rights and output usage restrictions; copyright ownership of model-generated outputs does not automatically follow code MIT licensing.
2. Verify resources: runtime, CUDA and memory on a rented pay-per-use GPU or owner-provided server. Obtain an actual fresh provider quote and explicit spend authorization before launching any paid job. The current GPU planner is only a dry-run and excludes startup/storage/egress/failure costs.
3. Run isolated model start with a hash-pinned image/requirements, no untrusted arbitrary scripts or outbound access beyond an allowlist; record GPU model, actual allocation, VRAM peak, model SHA, inference duration and total billed amount.
4. Emit real output GLB plus original source images/text and immutable job receipt; run independent Blender import/render, inspect topology/UV/PBR/skin as applicable, then game-engine target. Do not mark a generated character as rigged unless a deforming skeleton/action survives reimport.
5. Compare EXACT same permitted brief/reference to native Forge and lawful Tripo/Meshy results (if available), including geometry, texture, rigging, consistency across views, prompt adherence, render visual human acceptance, speed and real cost. No unmeasured 100x or global-best claims.
6. Host the real MGR-API-MCP with OAuth issuer/JWKS, audience, scopes tools:read/tools:execute and approved tenant; then prove a real hosted authorized client can start, poll, cancel, resume and retrieve an artifact after process restart without another noncanonical job store. Hosted edge and remote worker must use independent short-lived identities and private credentials.
7. Bind the existing private ChatGPT Forge Creator plugin to the real deployed shared MCP, then perform an actual iPhone/Tevin 3D artifact creation, preview, owner revision and download, with negative tenant, expired-token, replay, interrupted-worker and tamper tests.
8. Before marking released, confirm source rights for redistribution/derivative artwork, owner consent on human images/voice, storage retention/deletion, disaster recovery and repair. If no GPU/model entitlement is available, keep native Forge operational and the neural lane UNAVAILABLE.

## Current verified status (do not change without proof)

- Fully executable local original CPU models, browser and Blender acceptance receipts, and local shared MCP protocol fixture test: YES, by their individual evidence paths and dates.
- Authentic remotely deployed MGR API/MCP + Forge worker + real OAuth/JWKS client to trusted private model store: NOT YET PROVEN.
- Permitted high-quality neural model inference with real weights, GPU, PBR output and cost receipt: NOT YET PERFORMED.
- Tevin/iPhone creator and automatic waveform-driven facial animation: NOT YET ACCEPTED.

Canonical current status is docs/HANDOFF.md; feature-level acceptance F151. Do not treat this plan as code already built.
