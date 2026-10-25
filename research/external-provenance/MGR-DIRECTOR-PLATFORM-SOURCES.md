# External platform standards investigated for MGR-native Creation Director

Inspected 2026-10-25. Study only; neither external platform defines or owns an MGR product feature.

- Web Speech API draft: https://wicg.github.io/speech-api/ — evolving speech recognition interfaces, microphone/start/result semantics and local-model availability policies. **Study / optional**; support varies by browser and cloud/on-device processing must not be misrepresented.
- W3C File API working draft: https://www.w3.org/TR/FileAPI/ — local `File`, `Blob` object URLs and revocation rules. **Adapt standards** for private, bounded image reference preview; this does not perform image-to-3D inference.
- Existing repo `forge/glb.py` + `forge/world_editor.py` is the MGR-native generated geometry/export contract. No borrowed product code or proprietary source incorporated.
