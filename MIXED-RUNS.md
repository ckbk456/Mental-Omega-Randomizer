# Mixed runs and adaptive parties

Local launcher build 1.48.0 adds a unified mission pool and a refreshed native Tk interface. It includes the APRA2 mission fixes from 1.47.1. This is a local build, not an upstream release.

## Create a run

In **Settings → Mission pool**, select category/faction cells or use a preset. Counts reflect installed missions. MO campaign, MO co-op, challenges and APRA2 campaign can share one run. Challenge columns describe the enemy faction; choosing a player house never removes maps.

- **Flexible · finish solo:** the mission goal selects a solo-capable core. Selected native co-op missions are additional optional branches. They award rewards but cannot block the solo path or replace its final mission.
- **Co-op required:** native co-op can appear on the required path. Two people may be needed to finish.

Mixed pools support standalone **Grid Mode** and **Mission List**. Classic and Archipelago retain their legacy setup; mixed-pool generation/export is explicitly unsupported. Shop and Final Fortress keep their own setup, progression and saves. Optional 1v1 skirmishes retain their separate control.

The installed APRA2 v1.0 pack has 30 campaign missions and no co-op missions. Its co-op row is intentionally disabled. Missing packs and categories without authored missions are distinguished in cell help.

The pool, rewards and seed are frozen when generated. Editing settings prepares the next run; it does not replace the current run. Individual mission exclusions remain in Advanced Pool.

## Set up each mission

Select a mission, then use **Players & speed** beside Launch to reach its setup.

| Mission | Participants | Houses |
| --- | --- | --- |
| Campaign | Solo; a connected friend waits | Scripted by the mission |
| Challenge | Solo, AI teammate or Friend | Choose each player's house and color before launching |
| Native co-op | Two humans | Fixed by the authored map |

Challenges validate houses, colors and native player requirements at launch. AI difficulty is selectable. Player choices do not regenerate the run. The host controls game speed; guests receive that setting. Change the party between matches; there is no hot join.

## Play with a friend

Both players need this launcher build (party protocol 5), Mental Omega, and the assets required for the selected team mission. Use the existing Party connection workflow: host opens the run, guest joins. A guest can join before creating a personal run.

The host may play solo campaign missions or challenges while the guest stays connected. The guest does not need APRA2 merely because the host's pool includes it; both installations are checked when launching a team mission. Missing host-only missions remain visible to the guest.

The host owns shared progression. Guest unlocks come from the host's run for the duration of the session. Leaving restores the guest's personal run and configuration. Completion is recorded against the run, mission and launch attempt to prevent duplicate rewards after reconnecting.

## Resume existing progress

**Run library** keeps each run separately. The four legacy state files are imported independently when non-empty. Original files remain untouched. Seeds, mission order, grid, rewards and completed checks are retained; runs are never merged. Shop and Final Fortress continue using their existing saves.

New run saves live under `RandomizerLauncherData/runs` in packaged installations. Keep that directory and the rest of `RandomizerLauncherData` when updating or transferring a profile.

## Validation limits

This change was checked with Python compilation, a packaged installation report, real installed mission/map audits, actual Tk startup/rendering, mixed-run generation and reload, legacy-save preservation, and Shop transitions. A two-computer live match remains a manual check.
