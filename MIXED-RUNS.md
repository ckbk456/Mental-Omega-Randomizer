# Mixed runs and adaptive parties

Local launcher build **1.48.1** organizes setup as **Mode → Mission pool → Run rules → Players**. It includes the ARPA2 mission fixes from 1.47.1 and the mixed-run features from 1.48.0. This is a local build, not an upstream release.

## 1. Choose the mode and reward system

Start at the top of **Settings**. Game Mode determines which mission selection controls appear. Standard, Chaos and Randomizer Arsenal change rewards; they do not remove missions based on your chosen player house. Shop and Final Fortress display their own fixed reward systems.

| Mode | Mission selection |
| --- | --- |
| Grid Mode / Mission List | Combine supported categories and factions in the matrix. |
| Classic | Choose Campaign, Co-op or Challenges as the base category. Campaign and Co-op may also include challenges. Missions follow catalogue order; campaign and native co-op are not combined into a mixed Classic run. |
| Shop Mode | Use Shop's solo/native co-op mission choice and build-type filters. Challenges are unavailable. Optional 1v1 skirmishes are supported in solo Shop. Shop stock faction controls purchasable rewards, not mission inclusion. |
| Final Fortress | Use its dedicated defense-map catalogue, player setup and perk progression. Campaign pool filters do not apply. |
| Archipelago | Keep the existing MO campaign/co-op slot setup. Its distributed catalogue contains 97 MO campaign missions or 36 native co-op missions. Mixed pools, ARPA2, challenges and progression skirmishes are not added to Archipelago by this update. |

Only the controls belonging to the selected setup are shown. Changing next-run settings does not reroll or replace an existing run. Shop and Final Fortress retain their separate saves.

## 2. Select the mission pool

For standalone Grid Mode and Mission List, select matrix cells or use a preset. Challenge columns describe the **enemy faction**. Player houses are chosen later and never remove challenges from the catalogue.

| Installed content | Missions | Native play type |
| --- | ---: | --- |
| MO campaign | 97 | Solo |
| MO co-op | 36 | Two humans |
| Challenges | 22 | Solo, AI teammate or friend, subject to each map's native player requirements |
| ARPA2 campaign | 24: 12 Allied + 12 Soviet | Solo |
| ARPA2 special ops | 6: 3 Allied + 3 Soviet | Solo |

ARPA2 special operations are `ACO1–3` and `SCO1–3`. The `CO` in their map codes does **not** mean co-op. There is no ARPA2 co-op row.

Cell counts show installed maps. Build-type filters and individual exclusions can narrow the generated pool further. The matrix owns ARPA2 special-op inclusion: select or clear that row. **Include MO special operations** affects the 19 operations inside the MO campaign row only. Classic's legacy operations filter retains its existing scope.

Old 1.48.0 settings are interpreted without changing frozen runs. The former ARPA2 campaign choice becomes campaign plus special ops, except when the old global operations filter excluded them. The obsolete empty ARPA2 co-op choice is discarded. New campaign-only selections remain campaign-only.

Individual mission exclusions remain in **Advanced Pool**. Optional 1v1 progression skirmishes have one separate control in supported solo Grid/Shop setups.

## 3. Set run rules and generate

Choose the run length, reward rules and progression options that apply to the mode.

- **Flexible · finish solo:** the mission goal selects a solo-capable core. Selected native co-op missions are additional optional branches. They award rewards but cannot block the solo path or replace its final mission.
- **Co-op required:** native co-op can appear on the required path. Two people may be needed to finish.

The seed, mission order, rewards and progression are frozen when generated. Player choices and later pool edits do not regenerate them. New runs are saved separately in the Run library.

## 4. Set up the selected mission

Select a mission, then use **Players & speed** beside Launch to reach its setup. Party controls choose participants; they do not select categories for the next run.

| Mission | Participants | Houses |
| --- | --- | --- |
| Campaign / ARPA2 special op | Solo; a connected friend waits in a mixed run | Scripted by the mission |
| Challenge | Solo, AI teammate or Friend in mixed and challenge-only runs | Choose player houses and colors before launching |
| Native co-op | Two humans | Fixed by the authored map |

Challenges validate house clashes, colors and native player requirements at launch. AI teammate difficulty is selectable. The host controls game speed; guests receive that setting. Change the party between matches; there is no hot join.

## Play with a friend

Both players should use this launcher build (lobby protocol 6) and have Mental Omega plus the assets required by the selected team mission. Use the existing Party connection workflow: the host opens the run and the guest joins. A guest can join before creating a personal run.

In mixed runs, the host may play solo campaign missions or challenges while the guest stays connected. The guest does not need ARPA2 merely because the host's pool includes it; both installations are checked when launching a team mission. Missing host-only missions remain visible to the guest.

The host owns shared progression. Guest unlocks come from the host's run during the session. Leaving restores the guest's personal run and configuration. Completion is recorded against the run, mission and launch attempt to prevent duplicate rewards after reconnecting.

## Resume existing progress

**Run library** keeps each run separately. The four legacy state files are imported independently when non-empty. Original files remain untouched. Seeds, mission order, grid, rewards and completed checks are retained; runs are never merged. Shop and Final Fortress continue using their existing saves.

New run saves live under `RandomizerLauncherData/runs` in packaged installations. Keep that directory and the rest of `RandomizerLauncherData` when updating or transferring a profile.

## Validation limits

The filtering changes were reviewed against the actual installed catalogue and checked with Python compilation. The mixed-run implementation has also undergone packaged installation reports, native map audits, Tk startup/rendering, generation/reload checks and legacy-save preservation checks. A two-computer live match remains a manual check.
