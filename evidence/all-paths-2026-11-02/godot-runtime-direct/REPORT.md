# Godot receiving and physics evidence

The official Windows Godot 4.7.2 binary was unpacked into the ignored Forge artifacts directory. The archive SHA-256 matched `731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953` from the official release metadata. Windows reported a valid signature from Prehensile Tales B.V. The verifier used the direct executable, headless import, and a separate runtime witness in temporary project copies. [Official release](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable) · [Godot CLI documentation](https://docs.godotengine.org/en/latest/tutorials/editor/command_line_tutorial.html)

The empty and five-building projects received 120 and 240 triangles respectively. Across 44 tested corners on the five-building fixture, the maximum world-space error was approximately 0.57 mm. All expected raycasts hit and the dynamic sphere settled about 0.29 m above the ground. The witness records the exact source GLB hashes, the engine executable hash and fixture details in `godot-runtime.json`.

The first run used the Windows console launcher. It imported and exercised the empty-world fixture and timed out during the second import. The direct-executable run completed both. Interactive rendering, gameplay controls and other engines remain open.
