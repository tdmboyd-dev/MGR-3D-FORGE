# Authorized REA self-study — static release inspection

**Original request:** Analyze official REA itself under the existing MGR BEAST X-Ray safety rules before any large source campaign. **Source of truth:** docs/HANDOFF.md and evidence/xray/2026-10-31-rea-self-static.json.

Official upstream source: https://github.com/morluto/rea . Observed upstream main SHA from the prior verified wave: 6e9ee97a69cb16c7150d8b550e705cba055ee4f0. This is not asserted to be the exact npm package build commit.

Published package identity: rea-agents@6.8.0, npm integrity sha512-9QDeRnGqEDzABZyr04eLnBXBv/c6I9/TWu/6M0MD4pEfkySI/BIgwTODIbAReX3C1x6hjw9+Jlx4A2yUSPZ9ww== . The downloaded original npm TGZ matched that publisher metadata; it is stored privately under %USERPROFILE%/.mgr-tools/rea/workspace/packs, not GitHub.

**First negative test:** REA inspect-artifact on the original npm TGZ returned unsupported_target / unsupported binary format, NOT a corrupted target. **Fix applied:** bounded and path-checked transformation of the already integrity-verified npm tarball into a ZIP analysis carrier (source tarball left intact). This is a DERIVED inspection carrier; its SHA is not the upstream npm artifact hash.

**Actual verified result:** REA 6.8.0 inspect-artifact on derived ZIP produced complete container-entry inventory for 2,398 shipped files. Full original REA Evidence saved outside Git under %USERPROFILE%/.mgr-tools/rea/workspace/.rea-evidence/rea-6.8.0-self-zip-full.json. Public stripped-down summary at evidence/xray/2026-10-31-rea-self-static.json has original and carrier SHA-256, original npm SHA-512, immutable REA evidence id, complete ZIP coverage and entrypoint file hashes. No model weights or private secrets in Git.

**Source-level evidence observed:** release includes LICENSE, THIRD_PARTY_NOTICES.md, package.json, scripts/rea.mjs, dist/mcp/main.js, and thousands of shipped JavaScript modules. Release inspection does not prove internal call graph, current runtime permissions, dynamic execution, third-party provider behavior or source-code correctness.

**Potential issue to verify before upgrading:** package.json source distribution lists scripts/plugin-mcp-launcher.mjs and .codex-plugin/mcp.json, but these were not seen among the derived ZIP contents from the actual npm release. This is a packaging discrepancy observation, not yet proof of an upstream error. Check whether those files are intentionally excluded or offered through another distribution, test official installed runtime and exact updater/installer references before calling it broken.

**MGR-native engineering implications:** Keep our custom one-tool read-only REA MCP plugin rather than expose REA's entire active analysis surface by default. Use complete Evidence with explicit source formats and limitations. Validate raw file byte digests separately. Build snapshot diff/feature trace only for legally authorized sources, with each finding converted to an owned Forge capability and independent tests. MGR Rambler can measure our own release exposure with REA, but can never guarantee zero inspection.

**Still open:** multi-file static source-to-runtime traversal of REA's own implementation, security audit of all MCP tools, full packaging discrepancy resolution, performance benchmarks and any automated bulk runs on the 184 queued candidates. No unauthorized reverse analysis of proprietary Tripo/Meshy/Higgsfield binaries is planned.