# Challenges, mixed runs and parties

Owner: mission/party implementation. Current behavior is in
[MIXED-RUNS.md](../../MIXED-RUNS.md); network setup is in
[COOP_CONNECTION_GUIDE.md](../../COOP_CONNECTION_GUIDE.md).

Record actual build, game installation, map, seed/run ID, mode, speed, player
houses/colors, AI difficulty or both human machines, and result evidence.

- Verify all 22 installed challenges are discoverable regardless of chosen house.
  Launch-time validation must reject actual map house/color clashes without
  removing missions or regenerating a seed.
- Use Solo and AI teammate, then change houses/colors before the next mission.
  Confirm AI keeps native forces while human rewards remain player-owned.
- Host a challenge, join with the same build, choose independent houses/colors,
  and verify host speed. Launch the same map on both machines and compare outcome.
- In a mixed run, play a solo campaign and ARPA2 Special Op with a connected guest
  waiting, then resume a shared challenge/native co-op mission without rerolling.
- Native co-op needs its authored human seats and house setup. Verify missing
  required local map/assets blocks launch with a useful message.
- Test victory, defeat, surrender/exit and a stale debug log. Only a fresh matching
  result may grant completion; reconnect must not grant the same reward twice.
- Leave the party and verify the guest's own run/config returns intact. Repeat
  resume and settings import across Grid/List, Classic, Shop and Fortress.
- Verify flexible co-op branches cannot block the solo core's final goal; required
  co-op remains a deliberate choice. Check locked and completed mission views.
- Confirm mode-first settings have one owner for inclusion, generation and player
  choices. Next-run edits must not alter the current frozen mission/reward plan.

Status: manual checks pending for future changes. Earlier compilation, map audits,
installation reports or Tk captures are not a live two-computer gameplay pass.
