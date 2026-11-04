# Update handoff: Mental Omega Randomizer 1.49.1

Update the guest player's existing Windows installation to **1.49.1**, keeping
their settings and saves. The host already has 1.49.1. Keep the working private
network connection; the guest joins the host for challenges.

## Download and source

- Fork: <https://github.com/ckbk456/Mental-Omega-Randomizer>
- Install this version: [1.49.1 release](https://github.com/ckbk456/Mental-Omega-Randomizer/releases/tag/v1.49.1).
- Earlier feature build: [1.49.0 release](https://github.com/ckbk456/Mental-Omega-Randomizer/releases/tag/v1.49.0).
  It has the reported selling defect. There is no need to install it first.
- Source branch: `codex/campaign-structure-rewards`, based on the existing
  1.48.1 work. Both versions include that foundation.
- 1.49.0 executable source: `bc94ae3329f689c80d1914d5cd9f6b88bc55bba8`.
- 1.49.1 executable source: `c6ca24e3b56b8e2b93292ff0bfc36567e8b59711`.
- Both are fork **test prereleases**, built locally with Python 3.13.2,
  PyInstaller 6.21.0 and websockets 17.0. They are not Heinki's official releases
  or builds certified by the pinned Python 3.14.6 GitHub Actions workflow.

The executable still checks **Heinki's repository** for automatic updates. Use
these direct fork downloads for this update; the in-app updater will not find it.
No local game-installation archives, player profiles, pairing codes or personal
run data are included. The executable retains the repository's existing bundled
bonus asset; newly extracted structure sprites are generated locally at launch.

## Update procedure for the receiving agent

1. Locate the existing shortcut and its Mental Omega game folder. Preserve this
   installation and its working network setup. Confirm the folder contains
   `gamemd.exe`, `Syringe.exe` and the matching Mental Omega 3.3.6 assets. Do not
   copy the host's game data or assume the host's installation path exists here.
2. Wait for the player to close the game and launcher. Back up the existing EXE,
   APWorld, shortcut, entire `RandomizerLauncherData` directory and any game-save
   directory being used. Do not reset a run, remove caches or replace player YAML.
3. Download all assets from **v1.49.1** into a separate staging directory. With
   GitHub CLI, substituting a new local staging path:

   ```powershell
   gh release download v1.49.1 --repo ckbk456/Mental-Omega-Randomizer --dir '<staging-directory>'
   ```

4. Verify every file against `SHA256SUMS.txt` and verify the manifest says launcher
   `1.49.1`, APWorld `0.6.11`, and Archipelago `0.6.8`. The executable is named
   `MentalOmegaRandomizer.exe` in the release. Its SHA-256 must be:

   ```text
   AE5AF88F166EEC9F95B87E436FE70B27BB9355CB5FCE5C2E92198D906B5C1813
   ```

   The paired `mental_omega.apworld` SHA-256 is:

   ```text
   6C9F1CE399E7DCB3117AD2790101D1D5C9CD952283B357D2C69BA2458147C68C
   ```

5. Install the EXE in that same game root. Prefer the existing launcher filename
   so the shortcut and program-specific firewall rules keep working. A versioned
   filename is also supported, but update both the shortcut and any affected
   firewall rules. Set the shortcut's working directory to the game root.
   Put the paired APWorld beside the EXE and retain the release manifest/checksums
   with the downloaded artifacts. Do not replace the existing data directory.
6. Run the installed EXE with `--self-check`, using the game root as working
   directory. This checks the real installation without opening the interface.
   Inspect `RandomizerLauncherData/self_check.json`: require `passed: true` and
   `version: "1.49.1"`. Report any failure before proceeding. Compare saved runs
   and player settings to the backup, then confirm the shortcut targets this EXE.
7. If the player uses Archipelago, install the paired APWorld in its
   `custom_worlds` folder before generating a new multiworld. Preserve existing
   rooms and their files. **Challenge play requires no Archipelago setup.**
8. Let the player open the launcher and continue their existing run. **No new seed
   is needed for the selling fix. Launch a mission afresh**; loading an old in-game
   save preserves its serialized old building types and will not apply this fix.

## Join the host for challenges

- Both players must run **1.49.1** with matching native game files and the selected
  map. Do not mix 1.49.0 and 1.49.1. The new structure-art revision participates
  in prepared-map verification.
- For the selected challenge, use **Players & speed** and choose **Friend**.
  In **Co-op Connection**, the host selects **Host** and connects; the guest
  selects **Join**, using the host's current private-network IPv4 and pairing code.
  Obtain those privately from the host; they are not repository settings.
- Each player selects their own house and a distinct permitted color. Native
  challenge house clashes are validated before launch. **Game speed and challenge
  difficulty come from the host.** The host launches; both launchers stay connected.
- Keep the existing ZeroTier/Tailscale route. Do not create a new network or use
  public port forwarding for an already working connection. If changing the EXE
  name/path broke program-specific firewall rules, inspect the supplied
  `Setup-Private-Network.ps1` and use its `-WhatIf` preview before its documented
  elevated application. Select the actual filename with `-Launcher`.
- Further details: [connection guide](https://github.com/ckbk456/Mental-Omega-Randomizer/blob/v1.49.1/COOP_CONNECTION_GUIDE.md)
  and [mixed-run flow](https://github.com/ckbk456/Mental-Omega-Randomizer/blob/v1.49.1/MIXED-RUNS.md).

## What changed and what to test

1.49.0 adds 36 access rewards: eight campaign structures and 28 tech-building
rewards, covering 40 building variants. Psychic Amplifier uses 32 control slots,
costs 15,000 credits and consumes 900 power. Gladius and the Mental Omega Device
are excluded. Secret Lab access requires the owned lab plus a War Factory for
Rejuvenator production; direct Rejuvenator access keeps its separate route.

1.49.1 supplies valid construction/sale artwork for all 39 ordinary building
variants. Native construction art is reused when available; otherwise the
installed healthy sprite and shadow provide a static transition. Concrete walls
retain native overlay behavior. Native campaign types, prices, reward IDs and
existing run schedules are unchanged by the patch.

Existing runs retain their earned rewards and frozen reward queues. To try all
new structures on a separate new run, save current preferences, import the
included `Structure-Tryout-1.49.json`, and generate a new seed. This optional
tryout is separate from updating an existing run.

Passed locally: compilation/static checks, packaged installation reports, all
22 actual challenge map exports, Lights Out co-op export, build/sell sprite
integrity, deterministic manifest replay and saved-data preservation.
**Actual sales/refunds, complete in-game ability behavior and live two-PC play
remain manual checks.** Test selling a newly built reward structure in a fresh
mission and confirm the refund/removal; then test a shared challenge.

Source and test assets are published on the fork. This handoff authorizes the
requested guest installation update; it does not ask the receiving agent to
publish changes, open a PR, merge upstream, or stop a running player's processes.
No background service or development server is required. If something fails,
retain the backup and report the version, failed check and relevant redacted log.
