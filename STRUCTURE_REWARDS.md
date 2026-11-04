# Campaign and tech structure rewards — local 1.49.0

This build adds 36 access rewards: eight campaign structures and 28 tech-building
rewards, covering 40 physical building variants. Gladius and the Mental Omega
Device are excluded. Construction prices, power and abilities follow the
[reviewed balance table](docs/research/campaign-structure-rewards.md).

## Try the new buildings

1. Open the updated Mental Omega Randomizer shortcut.
2. Use **Load Settings** and select `Structure-Tryout-1.49.json` beside the EXE
   (the source copy is in `presets/`). This changes next-run preferences only.
3. Generate a fresh seed. The preset selects all 22 challenges and grants all
   36 new access rewards at the start, with ordinary construction costs and caps.
4. Choose a challenge and your house/color, then launch. Each new building can
   be constructed from any faction's Construction Yard. A challenge's native
   house restrictions are still checked before launch.

Save your current preferences with **Save Settings** before loading the tryout
if you want to switch back easily. Existing runs keep their frozen reward queues;
upgrading the launcher does not insert new rewards into them. For normal new runs,
keep special buildings and special rewards enabled; the additions participate in
the normal access pool. Shop prices are separate from construction credits.

## Mechanics

- Psychic Beacon has nine reversible mind-control slots. Psychic Amplifier has
  32, costs 15,000 credits, consumes 900 power and has a default cap of one.
  Normal psionic immunity applies; neither controls buildings or uses permanent
  capture or Mastermind overload logic.
- Blackout Research Station provides its own paid, manually targeted EMP pulse.
  It does not grant the existing building-free Blackout Missile reward.
- Native campaign objects and scripts retain their original types. The owned
  copies have private weapons, support powers and art. External occupancy cells
  are removed from their art; functional dock holes stay within the foundation.
  Existing installed cameos are reused where a structure lacks one.
- Tech Secret Lab Access unlocks the lab, **not direct Rejuvenator Access**.
  With this route, a War Factory and the owned lab are required. Losing the lab
  closes that route; it does not remove units already made. Direct Rejuvenator
  Access needs only the War Factory, including when both rewards are owned.
- Hospital/Field Hospital share one access reward and one cap. Their reciprocal
  construction prerequisites prevent building both under normal limits. Concrete
  bunker orientations likewise share one access reward.
- The existing unlimited-buildings option lifts the new ordinary caps, including
  the hospital pair restriction. Academy veterancy remains one rank and does not
  stack. Native Ares academy classification applies, including its Organic and
  ConsideredAircraft exceptions; exact unit lists include player clones.
- Oil Derrick and Bank pay no startup/capture cash. Tech Refinery gives no free
  miner. Airfield, Reinforcement Pad, Maintenance Facility and Missile Bunker
  retain their reviewed support behavior through isolated provider definitions.
- Global hospital/machine-shop healing follows native engine behavior; low power
  is not promised to disable those passive house bonuses.

The initial new Shop access prices are `2 + ceil(construction cost / 500)`, bounded
to 2–32 Ore; permanent access is four times that in Gems. Buffs use half the access
price rounded up, bounded to 2–10 Ore; permanent buffs cost twice that in Gems.
Existing Shop prices are unchanged. New structures currently have construction,
cost, armor, health and sight buffs; the two income buildings also have income buffs.

## Validation and limits

The local build uses Python 3.13.2 and the supported `-LocalTestBuild` path; it is
not the pinned Python 3.14.6 release build. Source/configuration integrity,
installed roster, real-map exports, art asset extraction and manifest replay are
checked separately from live engine behavior. Two-player play requires both
machines to use this same launcher build. A matching APWorld 0.6.11 is prepared.

Live placement, controller release, support timing, Weather Crystal targeting of
moving aircraft, hospital entry/healing, wall placement, and two-PC synchronization
remain in the [manual checklist](testing/MANUAL%20TO-DO/reward-structures.md).
Final Fortress's existing perk eligibility is preserved; these additions target
the ordinary randomizer reward modes.
