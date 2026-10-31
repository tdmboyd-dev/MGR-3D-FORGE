# MGR Rambler — release protection and original-source sovereignty

**Current stage:** MGR-owned integrity tool v0, real CLI/negative tests. This is NOT anti-reverse engineering invisibility and NOT digital-signature infrastructure. Current product handoff: docs/HANDOFF.md. Master program: docs/MASTER-FORGE-PROGRAM-2026-10-31.md.

## Why and where Rambler lives

Rambler is a reusable hardening component used when exporting MGR-owned Forge engines, creation projects, client plugin bundles and downloadable output. It does not operate as an AI brain, reverse-engineering agent or substitute for existing auth. Owner: MGR-3D-FORGE/forge/security/rambler.py (current). The transport/auth and eventual signature broker remain with MGR-API-MCP. Do not create a second storage vault, central queue, secret broker or trusted signing key embedded in the shipped client.

- Current Python implementation: forge/security/rambler.py; CLI in forge/cli.py actions rambler-seal and rambler-verify.
- Current tests: tests/test_rambler.py (3 tests plus one real CLI smoke). Public safe receipt: evidence/security/2026-10-31-rambler-smoke.json.
- Current manifest schema: mgr.rambler.release-roster.v1. Explicit allowlist of relative forward-slash file paths, SHA-256 and byte sizes, deterministic roster digest, symlink/path-traversal denial, secret-like filenames/hidden-files exclusion, unexpected-file and tamper failure. No external calls or provider billing.
- Current protection label: UNSIGNED_INTEGRITY_ONLY. Someone who controls both the files and manifest can forge this roster. The result explicitly says publisher_authenticated=false, reverse_engineering_impossible=false. This is a useful first block, not complete release protection.

## What really protects MGR intellectual property

**Server-only value:** Keep private models, commercial algorithms, privileged systems and signing keys on infrastructure MGR controls. Expose only task/answer contracts and least-privilege customer APIs; don't ship model checkpoints or secrets to customers. If offline operation is essential, distinguish which native components may be distributed and accept that executable code can be inspected.

**Signed releases:** Future version should verify Ed25519 or platform signing through a vetted cryptographic dependency and an offline/managed private key, with a pinned public trust anchor. No home-built cryptography, no fake signature field, no private-key JSON committed. Attested build digest and SBOM must be independently checked by the consumer.

**Deployment safety:** Per-tenant access and job quotas, approved artifact URLs with expiry/revocation, encrypted objects, dependency license manifests, reproducible isolated builds, vulnerability scanning, credential leakage testing, tamper alerts and rollback. Optional minification/obfuscation may raise casual copying cost but cannot be treated as an authorization control.

**Legitimate analysis:** Rambler must never conceal harmful behavior, evade malware scanners, block owner debugging/security evaluation, or misrepresent third-party rights. Use REA against our own release in a controlled scope to measure exposed paths, symbols, secrets and tamper detection, then improve the build. Preserve diagnostic symbol bundles privately for authorized maintainers.

## Next acceptance steps

1. Maintain and test unsigned roster v0; fail closed for changed/missing/extra files, symlinks, unsafe paths, secret-like content and unsupported signature claims.
2. Add secure signing/verifier contract with owner-controlled real key provisioning, signing only after actual key vault and operating approval. Test fake signature/wrong key/future version/rotation/rollback.
3. Implement protected binaries and model packages where necessary. Prove no private weights, source secrets or token material ship in client/plugin releases.
4. Run authorized REA self-assessment against release artifacts, measure practical resistance, and record limits without impossible secrecy claims.
5. Integrate only verified verification receipts into MGR Forge Vault, downloadable artifact delivery and the future ChatGPT Forge Creator plugin.

Source risk guidance: https://mas.owasp.org/MASVS/11-MASVS-RESILIENCE/ ; https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html ; https://www.nist.gov/publications/security-considerations-code-signing .