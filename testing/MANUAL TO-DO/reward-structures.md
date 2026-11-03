# Campaign and tech reward structures

Status: **pending design and implementation**. See the
[research proposal](../../docs/research/campaign-structure-rewards.md).

After an approved implementation, record version, installed engine, mission,
progression/reward mode, player house, earned reward and generated structure ID.

1. Earn the unlock normally and confirm the sidebar price, power, prerequisite,
   build limit and cameo. An unearned structure must remain unavailable.
2. Construct it as each supported player faction. Confirm placement/foundation,
   buildup, ownership, health bar, damage/death, selling and AI targeting.
3. Compare the promised effect with the native mission or tech-building effect.
   Exercise low power, loss, sale and rebuild. Verify capture-only logic is
   deliberately adapted and bonuses neither vanish nor duplicate.
4. Check range, reload/cooldown, targeting, armor interaction, anti-air restrictions,
   mind-control capacity/release and scripted/immune targets. Record native game
   speed because frames are not universal wall-clock seconds.
5. For economy/training/healing, record measured income/healing/veterancy and
   duplicate-building stacking. Confirm no sell/rebuild or ownership-transfer loop.
6. On missions containing the native structure, confirm native AI/scripts and
   victory conditions still work; rewards must not commandeer objective providers.
7. In two-player challenges/co-op, both players use the same build and shared
   reward state. Check local construction, ownership boundaries, effect agreement,
   completion synchronization and guest restoration after disconnecting.
8. Load a pre-feature save and compare seed, mission order, pending rewards,
   completed checks and existing IDs. New content must not reroll earned progress.

Exercise the existing unlimited-buildings option and document which caps it lifts.
Any proposed strategic/economic exception requires an explicit design decision;
do not silently override the user option.
No live result is marked passed by this checklist's existence.
