# Development workflow and command registry

## Repository evidence and baseline

Inspected on **2026-11-03**. This is an existing Python/Tk Windows launcher with
Ares/INI map-generation logic, a separate Archipelago package and a Wine build
path. It is not the neighboring RA2MoDern project.

- Remote: `https://github.com/Heinki/Mental-Omega-Randomizer.git`.
- Verified remote default: `main`, commit `50c835704467ebd576a1f6a2d1e5516a06b1b97b`.
- Requested branch point: current local 1.48.1, `30745f68e61a34db594d0a6656c4c4c24bf7dd44`,
  containing three commits beyond verified main. No rebasing away those features.
- Work branch: `codex/campaign-structure-rewards`; reused the clean task-owned
  checkout at `C:/YURIS REVENGE/Mental Omega Challenges Test/RandomizerLauncher`.
- The prior fetch refspec was tag-only (`V1.47`). `origin/main` was explicitly
  fetched for verification; a plain fetch alone did not establish synchronization.
- Existing architecture, generated-map isolation, atomic saves, no-unit-test
  policy and release CI are preserved. No formatter/typechecker/linter manifest,
  custom Git hook, CODEOWNERS, deployment service or production database was found.
- Filename inspection found no tracked credential-shaped files. Player YAML,
  extracted rules and caches are ignored; their values were not published.
- No equivalent repository build, game or launcher was running at bootstrap.
  Unrelated Codex/Node processes were left alone. Native process cwd could not be
  verified from the read-only process inventory; no app listener was attributed.

## Runtime and environments

The release scripts and CI require **Python 3.14.6** and
`requirements-build.txt` (including PyInstaller 6.21.0 and websockets 17.0).
Runtime dependencies are in `requirements-runtime.txt`. These are pinned
requirements files, not a hash-locked dependency resolver lockfile.

This machine currently has Python **3.13.2**. The supported `-LocalTestBuild`
exception accepts >=3.13; it does not make a local artifact an official reproducible
release. Never silently relax CI pins. Select the intended Python/venv on PATH
before using the portable commands below.

Source path resolution uses the repository's **parent** as GAME_ROOT and the
checkout as APP_DIR. A generic worktree elsewhere is not automatically a complete
game installation. Packaged builds use their EXE directory and a separate
`RandomizerLauncherData` profile. Installation reports/map audits require actual
licensed game assets; keep their generated output out of Git. There is no web
server, deployment URL, migration or provider account to provision for this task.

## Command registry

Times are estimates, not SLAs; cost depends on map count, caches and machine.
Run one intensive command per worktree and inspect existing processes first.

| Purpose / command | Source of truth | Expected duration / CPU | Environment / gate |
| --- | --- | --- | --- |
| `python -m pip install -r requirements-runtime.txt` | requirements-runtime.txt | <2 min; low | Selected venv; conditional network install |
| `python -m pip install -r requirements-build.txt` | requirements-build.txt; CI | 1–5 min; moderate | Python3.14.6 release venv; conditional network install |
| `python -m compileall -q launcher_gui.py randomizer Archipelago tools` | DEVELOPER_GUIDE; CI compilation | <30 sec; low | Source checkout; deterministic syntax gate |
| `python -c "from randomizer.config.static import REQUIRED_STATIC_CONFIGS, validate_static_configs; validate_static_configs(REQUIRED_STATIC_CONFIGS)"` | build_exe.ps1 preflight | <10 sec; low | Source/config assets; deterministic integrity gate |
| `git diff --check` | Developer guide | <5 sec; low | Working diff; deterministic whitespace gate |
| `python launcher_gui.py --self-check` | launcher_gui.py:run_self_check | <30 sec warm; low/moderate | Actual game parent; conditional installation report, writes ignored self_check.json/caches |
| `python tools/audit_campaign_maps.py` | tools/audit_campaign_maps.py | Several minutes; intensive | **Blocked as currently written:** mixes synthetic assertions with real-map auditing and requires exactly97 campaigns; current installation has127. Separate the valid installed-map audit before use under the no-unit-test policy. |
| `python tools/audit_final_fortress_maps.py --output logs/fortress-audit` | Tool argparse; FINAL_FORTRESS | Several minutes; intensive | Actual Fortress assets; conditional map/spawn audit, explicit output |
| `.\build_exe.ps1 -Output .\release\MentalOmegaRandomizer.exe` | build_exe.ps1 | 1–5 min; intensive | Python3.14.6 + pinned deps; deterministic packaging gate |
| `.\build_exe.ps1 -LocalTestBuild -Output .\release\MentalOmegaRandomizer.exe` | build_exe.ps1 | ~30–120 sec; intensive | Python>=3.13 + documented actual tools; conditional local artifact only |
| `.\Archipelago\build_apworld.ps1 -OutputDirectory .\dist` | Archipelago/build_apworld.ps1 | <2 min; moderate | Python source/snapshots; AP package; may refresh tracked catalogue snapshots |
| `.\build_all.ps1 -LauncherOutput .\release\MentalOmegaRandomizer.exe -APWorldOutputDirectory .\release` | build_all.ps1 | 1–5 min; intensive | Matching launcher/APWorld artifacts; conditional catalogue changes |
| `.\build_archipelago_release.ps1 -OutputDirectory release` | Both GitHub workflows | 1–5 min; intensive | Python3.14.6 pinned build environment; complete discovered PR/release packaging gate |
| `python tools/generate_randomizer_units.py --help` | Tool argparse; configs guide | <10 sec; low | Discover exact installed-rules inputs before running this mutating generator |
| `python tools/complete_weapon_registry.py --help` | Tool argparse | <10 sec; low | Inspect inputs before rewriting the weapon registry |
| `python launcher_gui.py` | launcher_gui.py | Interactive; variable | Human-owned source UI/gameplay; no automatic UI testing authorization |

Linux/Wine commands already documented in DEVELOPER_GUIDE remain separate supported
maintainer paths; this Windows bootstrap does not certify them. There is no
configured unit-test, lint, format, typecheck, migration or development-deployment
command to invent. The legacy campaign-audit driver above conflicts with the active
no-synthetic-test policy; its existence is not permission to execute that path.
Also keep EXE outputs outside `dist/MentalOmegaRandomizer.exe`: that is the builder's
internal artifact, and using the same destination would make its copy step fail.

## Gates and delivery

Local 1.49.0 adds a real installed-map export command (no launcher/UI or mock):
`python tools/export_structure_tryout.py --run <existing-run.json> --output <separate-directory>`.
It reads the run, adds the 36 structure access rewards in memory, exports all 22
installed challenges, checks manifest replay and stages required art. Use
`--maps c_regenbogen c_heavyobject coop_slights` to select actual maps, and
`--lab-route` for an explicit lab-only loadout with ordinary caps. About 30 seconds
for all challenges on this installation; moderate CPU, one command at a time.
Outputs contain copied run metadata and remain ignored local evidence.

The reviewed `presets/Structure-Tryout-1.49.json` uses the ordinary settings-import
flow and grants all additions on a fresh generated run. It contains no personal
profile or credentials. Manual gameplay remains a separate gate.

Existing `security.yml` compiles and builds a complete Windows/APWorld bundle,
then independently runs CodeQL and PR dependency review. `release-build.yml`
checks source/tag agreement, builds and verifies payloads, and prepares a draft
release for a tag. Do not trigger/tag/publish just to validate documentation.

The local setup/proposal gate consists of whitespace, local Markdown links,
compilation and static-config integrity. The complete pinned packaging gate must
pass before claiming PR-ready; local Python3.13.2 does not satisfy that release
environment. No remote CI is claimed green without an actual run.

Manual game/AI/two-PC effects and visual fidelity remain in the
[manual QA index](../testing/MANUAL%20TO-DO/README.md). No new building is implemented
or verified by a research document. A source/build artifact is not a deployment.

For later publication, retain the explicit dependency on the three local1.48
commits. Review the intended combined diff before choosing a PR base; a PR against
main would include that foundation as well. No remote publication or merge is
authorized by this bootstrap. Use the file-pr workflow only when requested.

## Local bootstrap handoff

Implemented: reconciled root AGENTS, contributor/index links, command registry,
scoped roadmap/research, PR template, local-secret/environment/save ignores, and
consolidated reward/challenge manual guides. Repaired the missing challenge-guide
entrypoint. Existing CI and product compatibility rules were preserved.
The unavailable legacy caveman instruction was replaced with the explicitly
requested standard workflow's clear-English communication convention.

Locally validated on 2026-11-03: source compilation; 16 required static configs;
39 local documentation links with no missing targets; whitespace; actual installed
catalogue report passed with 127 campaign/operation maps and 22 challenges.
Sanitized factual evidence is in ignored `logs/campaign-structures-research/`.

Not run: full pinned release packaging (Python3.14.6 unavailable here), remote CI,
agent-operated UI, manual gameplay or two-PC matches. The legacy campaign-audit
driver is blocked for the policy/catalogue reasons above. This is not a PR-ready,
CI-green, released or gameplay-verified claim.

All task-owned inspection/validation commands completed. No persistent process,
server, migration, engine dependency, generated release or installed-game update
was started. No external credential/provider permission is needed for this local
handoff. Remote publication/merge/release authority remains **not granted**.
Implementation update 2026-11-04: the user subsequently requested implementation
and a local playable build. Local 1.49.0 adds the selected 36 structure access
rewards and a matching APWorld 0.6.11. All 22 challenge map exports replay identically;
lab/direct access and provider references have additional real-map reviews.
The old 4,450 item IDs, 43,857 location IDs and 133 local-victory pairs are retained.
The installed ARPA2 catalogue adds 30 local-victory pairs after reserved IDs.
Live gameplay, two-PC QA, pinned Python 3.14.6 packaging and remote CI remain separate
gates. Source commits and local installation do not authorize publication or merging.
