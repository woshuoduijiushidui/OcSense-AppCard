# Pantry Steward

English | [简体中文](README.zh-CN.md)

An independent script bundle for the unmodified official OctoSense desktop.
The original project's UI, onboarding, inventory, local planner, confirmation
and persistence are retained. No custom model or speech service is injected.

## Run locally

Requires Python 3.11+, Rust and the official repository's prepared `.sources/`.
From the repository root (verified on Windows; see VALIDATION.md):

```powershell
.\apps\pantry-steward\run.cmd --prepare-local-test
```

Only run `--prepare-local-test` after the person approves generating local test
keys. It creates keys outside the repository in the platform's local app-data
directory, under `OctoSense/pantry-steward-local-test-keys`. These are NOT the
publisher's production identity. No remote submission is performed.
Subsequent starts: `apps/pantry-steward/run.cmd`.

The launcher builds unmodified CLI sources at the App Hub revision the official
workspace pins, reusing `.sources/`; checks an unsigned source bundle; signs a
separate test snapshot; creates a verified local catalog; and installs through
App Hub's real `Store` digest, signature and policy checks. It opens the app
in the official shell. Test data and shell settings stay in `.local-state/`,
without replacing the person's normal desktop or original pantry data.

## AI and voice

Configure providers through OctoSense's own AI providers settings in this test
profile. The app never reads `ai.env`, sees a key, or asks for one. `model.budget`
reports usage, NOT provider readiness. A missing provider is handled explicitly;
the local planner remains available. Live provider requests are **unverified**.

The microphone icon is retained, but only explains that speech recognition is
unavailable; this version does not record audio or request microphone permission.
The original project still contains the previous local speech adapter.

## Check and standalone preview

These check and preview commands were verified on Windows; see VALIDATION.md:

```powershell
python -X utf8 apps/pantry-steward/tools/launch.py --check
python -X utf8 apps/pantry-steward/tools/launch.py --standalone
```

The official standalone card-host does not offer model services. It must remain
fully usable with local rules. Only `bundle/` is an App Hub submission candidate,
not `.local-state/`, tools or the whole OctoSense repository. Publisher identity,
privacy text and production signing/submission remain human checkpoints.

Do not delete this folder's `.local-state/` without backing up needed test data.
Keep the official host at a tested revision before a competition demonstration.
