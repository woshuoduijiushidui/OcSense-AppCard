# Migration validation

## Verified on Windows, 2026-10-02

- Official OctoSense source: b221f7b4c877dd823d04e4ee510cc74880de5535.
- Pinned App Hub: 58c3c8aed8fc811a16d67c5f784a8a44214ff876.
- `python -X utf8 tools/setup.py --hub <existing dependency directory>` succeeded.
- `python -X utf8 apps/pantry-steward/tools/launch.py --check` built the
  official CLI sources, reusing `.sources/` without custom host services.
- `python -X utf8 -m unittest discover -s apps/pantry-steward/tools -p 'test_*.py'`:
  3 passed (key-generation consent, no secrets/custom microphone calls in the
  bundle, official budget semantics).
- The launcher with `--prepare-local-test --hidden --remote 18442 --app-data
  apps/pantry-steward/.local-state/qa-official` generated local test keys only
  after explicit consent; signed a separate snapshot; published ONLY to a local
  mirror; verified the catalog and installed through App Hub's real Store.
- `python -X utf8 apps/pantry-steward/tools/smoke.py --profile
  apps/pantry-steward/.local-state/qa-complete`: 17 native UI/data checks passed.
  Includes first-run onboarding, invalid quantities, preview/confirmation,
  microphone-unavailable notice, honest budget status, local mode, demo consent,
  expiry replanning, acceptance, invalid consumption, cancellation, consumption,
  and returning to the profile form without losing inventory.
- Same command with `--restart`: persistence check passed (18 UI/data checks total).
- Native remote logs after the successful run/restart contained no `[E]`,
  callback errors or on_render closure failures.
- Final default profile launcher (`--hidden --remote 18443`) opened the app in
  the unmodified official shell. `cargo build --release --locked -p octosense`
  succeeded; the official source files remained unchanged.
- Independent preview (`--standalone --hidden --remote 18444`) was admitted
  by the unmodified official card-host and rendered its initial onboarding page.
- `target/release/hub scan apps/pantry-steward/bundle --packet
  apps/pantry-steward/build/review.json` created the seven-question review packet;
  no external reviewer was used. Draft answers: REVIEW-ANSWERS.md.
- Four real full-window captures from the official-shell test were opened,
  visually inspected and copied without editing to `bundle/screenshots/`:
  `01-main.png`, `02-plan.png`, `03-confirm.png`, `04-updated.png`.
- Final bundle size: 8,308,715 bytes, below the 8,388,608-byte gate limit.

Final unsigned source-bundle gate output:

```text
pantry-steward 0.4.1 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"model", "storage"}, hosts {}, storage 16777216 bytes, agent none
```

Local signed snapshots also passed without that unsigned warning. They are not
production publisher signatures. The source bundle remains unsigned for editing.

## Compatibility gaps found and fixed

- The Windows batch entrypoint used LF-only newlines. Running it through
  cmd.exe reproduced truncated commands before Python could start. Changed it
  to ASCII with CRLF, added a Git checkout rule, and guarded its dispatch and
  failure exit status with Windows-only tests.
  All six launcher tests passed. Running run.cmd from the app directory with
  a separate qa-batch profile opened the official shell and Pantry Steward's
  first onboarding page; verified via the native UI snapshot and real capture.
  The task-owned hidden test window was closed through its remote endpoint.
- The original 2 MiB quota failed `fs.write` in the official runner, because
  this runtime counts the installed bundle/resources inside the jail. Raised
  the requested quota to the supported 16 MiB ceiling and reran onboarding.
- Official `model.budget` returns usage, not `configured` or model identity.
  Removed that assumption and stopped labelling a successful budget query as a
  configured provider.
- The tested official host has no original `microphone.start/stop` adapter.
  Removed its calls and microphone grant. The icon now explains unavailability;
  no audio is recorded. Original speech code is preserved in the source project.
- A manifest-only edit does not change the bundle digest. Local snapshot caches
  now include manifest bytes, so storage/version changes cannot reuse stale grants.

## Not verified

Live model-provider calls, no-provider response end-to-end, speech recognition,
other operating systems, mobile devices, release signing and App Hub submission.
No real AI credentials were copied or used, and no provider API call was tested.
The original project's inventory and ai.env were not migrated. All created
hidden test windows were closed through their own remote endpoint.

Publisher identity and privacy text remain unapproved; the existing listing
keeps the author's pending identity. Local test-key creation was explicitly
approved by the user. Production signing and submission were not authorized.
