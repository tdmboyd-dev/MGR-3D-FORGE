# MGR 3D FORGE — Instructions for contributing agents

- The repo is the single GitHub-backed source of truth. Keep `main` current after local verification; avoid expensive GitHub Actions for routine tests.
- Read `README.md`, `docs/PRODUCT-BIBLE.md`, `docs/BUILD-REGISTER.md`, `docs/PROGRESS-LOG.md`, `docs/IMPLEMENTATION-EVIDENCE.md`, `research/RESEARCH-REGISTER.md` before expanding scope.
- Read `docs/MGR-NATIVE-CANON.md` first. Every MGR capability, status and public-facing description is native; external research references are segregated to `research/external-provenance/` for legal/technical traceability only.
- Never label a researched idea built, or a unit-tested prototype production-ready. Track research maturity and code maturity separately. Never claim a 10x uplift without benchmark evidence.
- Use reproducible commands; document exact tested paths/results. Run `python3 -m unittest discover -v` after each change.
- No secrets, owner-private Tevin image/model references, paid model weights, or API tokens in this public repository.
- Check licenses at the exact version/repository and weights level before commercial use, model download or redistribution.
- CPU procedural geometry is intentionally independent of model APIs. Optional neural/provider adapters must have cost controls, approval gates, provenance and swappable interfaces.
- Treat exports as unverified in external engines until an actual independent import/render has occurred. Do not fabricate QA results.
- Do not delete or overwrite unrelated work, and do not burn user GitHub Actions budget.
- Update `docs/BUILD-REGISTER.md` and `docs/PROGRESS-LOG.md` alongside any tested implementation. Describe blockers and next proof clearly.
- Owner-approved autonomy is defined in `docs/MGR-NATIVE-CANON.md` under **Locked owner execution policy — hands-off Forge workspace**. Build, test and fix unattended inside the approved workspace with receipts and recoverable edits; do not expand scope to personal files, credentials, unrelated repos, destructive operations or spending without separate authorization.
