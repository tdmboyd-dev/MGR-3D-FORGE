# Actual MGR Forge Studio Chrome QA — reproducible owner source

These are source-backed tests, NOT a hosted browsing application or a second 3D engine. The canonical running code and current status are in MGR-3D-FORGE/docs/HANDOFF.md.

Test files:
- creature.mjs — click actual Creation Chat, generate original creature, saved status/replay, change MorphRig bend and verify distinct GLB, create original alien biome and download, edit actual city and download, zero JS page errors; records SHA and screenshot digest
- human.mjs — click real Human Forge Studio, run original Blender human lip-sync from SAMPLE manually timed phonemes, poll status, download SHA-checked animated GLB and editable .blend, screenshot digest; audio auto-alignment is NOT tested

Prerequisites on the owner Windows workstation: real Python from Forge environment, real Google Chrome at C:\Program Files\Google\Chrome\Application\chrome.exe, Blender 5.2.2 for human mode, Node >=22, and local loopback socket permissions. This directory has a pinned playwright-core development dependency; run the following to install ONLY in this folder (no GitHub Actions required).

    npm install --prefix scripts/browser-qa --ignore-scripts --no-audit --no-fund

Use scripts/verify_browser_ui.py as the actual local orchestrator and give it an output location under a private writable directory. It builds a fresh original MGR world, creates one real Forge Studio with a session token, launches Chrome, checks job SHA and writes one safe JSON receipt. It never inserts private bearer/session tokens or raw output GLB into Git.

    python scripts/verify_browser_ui.py --mode creature --out PRIVATE_DIRECTORY
    python scripts/verify_browser_ui.py --mode human --out PRIVATE_DIRECTORY --blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

The screenshots and raw generated files remain PRIVATE under the owner-supplied --out; evidence/browser/ JSON receipts include exact hashes/limitations. Avoid uploading any screenshots with personal info or embedded tokens to a public repo. The existing React-ish WebGL page is original Forge; these scripts are tests of the actual UI, not mock screenshots. Human test involves real Blender and can take longer under CPU load. Workstation hardware is Intel Iris Xe with no NVIDIA CUDA.
