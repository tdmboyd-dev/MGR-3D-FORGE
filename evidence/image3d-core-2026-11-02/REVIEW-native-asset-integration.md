# Independent native asset integration review

Scope: complete `forge/creation_asset_jobs.py`, `forge/request_binding.py`,
`viewer/asset-preview.js`; changed Studio route/file/response handling plus its
owner/Host/Origin checks and job identity helpers; Creation Director upload,
create/cancel, saved-history/reopen, authenticated download and preview callers
in `viewer/runtime.js`; corresponding input/preview template sections. Existing
world movement/rendering outside these changes was not a full review target.
This is a bounded code and failure review, not a whole-product security audit.

## Concrete finding and repair

**P2 — initial admission persistence failure leaked an unowned job folder.**
The adapter originally allocated `create_job()` and performed its first
`_atomic_json(journal, rows)` outside the protected execution block. A real
disposable fixture with that first write throwing `OSError` produced one empty
job directory and no journal row. Repeating the exact original request then
created a second directory and materialized with `replayed:false`; the first
empty directory remained. The observed before-repair output was:

```json
{"failure_phase":"first journal persistence after create_job","jobs_after_failed_admission":1,"ledger_after_failed_admission":false,"jobs_after_retry_same_exact_request":2,"second_status":"MATERIALIZED","second_replayed":false,"first_job_remains_empty":true}
```

No original geometry had executed before that failed admission. The defect was
lost request/allocation recovery and orphaned storage, not demonstrated
duplicate output or permission bypass. The scratch reproducer was executed at
`C:/Users/cool/Documents/Codex/2026-11-02/u/work/review_creation_orphan.py` before
the repair; its post-failure indexing deliberately assumes the old orphan exists
and is not a passing after-repair test.

At the parent's direction, only the initial admission block was repaired.
Under the same existing world lock, it rereads the original journal after the
write exception. An explicit missing file or readable valid ownership map can
establish that neither this request nor this job was admitted. Only then does
`rmdir()` remove the newly allocated, still-empty, nonsymlink directory. It
never recursively deletes work. A committed row, a different request owning
the job, a populated directory, unreadable/corrupt/invalid journal or uncertain
cleanup preserves the original allocation and original error.

If the write committed before reporting an error, its `STARTED` identity
survives. Replay returns the same job with `NEEDS_RECONCILIATION`, never a second
allocation or fabricated completion. The separately owned execution body and
existing asset tests were not rewritten.

`tests/test_creation_admission.py` adds five tests covering before-commit
failure for both kinds, committed-then-error for both kinds, corrupt/invalid/
populated state, explicit permission failure on recovery read, and another
request owning the allocated job. Those five plus the seven existing asset-job
tests passed **12/12 in 7.573 seconds**, captured in `admission-final.txt`.
`git diff --check` passed for this repair. Full combined suite and final runtime
source qualification are parent-owned; prior API/native proof hashes precede
this additional native repair.

## Other reviewed boundaries

No additional actionable P0/P1 finding was established in this scope:

- Uploaded bytes have native size/schema/hash/morph/PNG checks. Both original
  native preflights happen before persistent allocation. The earlier accidental
  simultaneous smooth/marching arguments are corrected to one rounded-surface
  mode.
- Exact request IDs bind encoded original instructions. Materialized replay
  checks saved request bytes, each original source, output receipt and output
  GLB hashes. Changed instructions do not reuse an accepted result. Interrupted
  execution remains reconciliation state.
- New routes reuse original Studio token, exact local Host and optional same
  Origin checks. File names/subfolders are native constants; private GETs remain
  token-gated, symlink/refolder escapes are checked and no upload path can select
  an arbitrary server file.
- Browser metadata and errors are written through text content. Artifact URLs
  are allowlisted same-origin paths, downloads/preview attach the token header,
  redirect following is refused, and preview hashes actual fetched bytes before
  rendering. The current generation counter and abort controller prevent an
  older delayed preview from replacing a newer selection.
- Preview uses the selected glTF scene and node hierarchy, composes parent and
  child transforms, checks accessor bounds/finite source samples, bounds visited
  nodes/triangles, and does not fetch image/texture URIs. Its stated profile is
  static triangle geometry and material colors, not textures, animation or a
  general glTF receiver. Original native imported-model validation is the
  preceding geometry authority; this small browser preview is not a replacement
  for independent Blender/engine acceptance.
- Stopping the browser wait aborts the request transport, not the native saved
  job. The corrected response writer handles a lost connection without changing
  or retrying that job. Reopening saved work is still read-only.

Residual limits: filesystem power-loss durability/multiple concurrent independent
Studio owners, arbitrary malicious-glTF preview conformance, all-path rig/art
quality, internet deployment and independent engine acceptance were not proved
by this bounded review. No new permission engine, ledger or uploader was added.

## Reviewed source fingerprints

Post-repair bytes at review close (SHA-256):

| File | SHA-256 |
|---|---|
| `forge/creation_asset_jobs.py` | `10fbbf8fb405bb2e302774f203f07399016696247d6617c5a5fe835e8c27fd92` |
| `tests/test_creation_admission.py` | `54134d8cfc9a156428af68296ec3f9d69caa867b50f7d37c63997d2c1df3ccd6` |
| `forge/request_binding.py` | `07ef1fd4c022234457e9f79e990980a9d981583d3ed1920727dc4c035eae238b` |
| `forge/studio_server.py` | `26c38907b5d64f4455b17a17c70ca7377d6420abe33a6f347e41cfe98418a03b` |
| `viewer/asset-preview.js` | `1138ebe97c1ff8eda0f2e8acf40e96b641b8c300df722293a1ca795cc79d2738` |
| `viewer/runtime.js` | `807d25ac52901c61256a20017c6bd42d4fc23fa39755fa14492266bf4458ebd4` |

These identify the reviewed window. Later root integration changes require
scoped review/verification rather than silently inheriting this result.
