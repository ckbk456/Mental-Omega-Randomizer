# Campaign and tech structure reward proposal

**Status: approved and implemented for local testing — 2026-11-04.** The user
requested implementation after selecting the decisions below. This document
retains the initial balance and research; current behavior and validation limits
are in [STRUCTURE_REWARDS.md](../../STRUCTURE_REWARDS.md).

Branch: `codex/campaign-structure-rewards`, from local 1.48.1 commit
`30745f68e61a34db594d0a6656c4c4c24bf7dd44`. Repository workflow changes are separate
from this unimplemented balance design.

## Selected decisions — 2026-11-04

- Psychic Amplifier uses **32 reversible slots, 15,000 credits and 900 power**.
  Range 18, 3,200 HP, acquisition every 180 frames and default cap 1 remain proposed.
  Controlled units return to their previous owners when the controller is destroyed.
- Gladius Defense System and Mental Omega Device are **removed from this feature**.
- Secret Lab remains a **separate buildable access reward**. Direct Rejuvenator
  Access permits production with a War Factory. Secret Lab Access requires the
  player to construct the lab as well before its Rejuvenator production is available.
  The two access rewards must not be merged, aliased or treated as duplicates.

These decisions are implemented in local 1.49.0; live gameplay verification remains pending.

## Reading the numbers

- Prices are **in-game construction credits**, not Shop Ore/Gems or the price of
  earning a randomizer reward. Each reward unlocks a type; construction still costs money.
- `−power` means continuous consumption; `+power` means generation. Weapon range
  is in map cells. Damage is before armor multipliers. ROF and EMP duration are
  simulation frames (`f`); wall-clock performance changes with selected game speed.
- Support-power recharge values use native `RechargeTime` game minutes; their
  wall-clock duration changes with game speed.
- Cost, power, HP and caps below are **recommended initial balance**, unless stated
  as retained native values. They have not been playtested.
- Default caps are ordinary balance proposals. The existing unlimited-buildings
  option must have a documented interaction; no hidden exception is approved here.
  Academies do not become stackable merely because more copies can be built.

## Evidence and installed-engine baseline

The installed rules identify Mental Omega 3.3.6. `Ares.dll` file version is
20.333.289; no `Phobos.dll` was found. The installed rules cache matches the
highest-precedence `RULESMO.INI` in `expandmo99.mix`:

`SHA-256 8607e14e36a3bfeef16427f739123605baa92d094b8370a5f47253dfda29b747`

The wiki describes campaign identity, but installed rules/map overrides determine
this proposal's mechanics. Direct Fandom page fetches were blocked; indexed page
text and installed definitions were used. Differences are recorded rather than
assuming a wiki number matches this installation. Official Ares documentation
provides feature semantics, not proof that a proposed combination works in-game.

### Conventional balancing anchors

| Native structure | Credits | Power | HP | Actual role / weapon |
| --- | ---: | ---: | ---: | --- |
| Psychic Tower | 1,500 | −100 | 1,050 | 3 control slots, range 8, acquisition ROF90 f |
| Prism Tower | 1,200 | −75 | 850 | Ground; damage 110, ROF 50 f, range 8 |
| Tesla Coil | 1,200 | −75 | 850 | Ground; damage 200, ROF110 f, range 8 |
| Grand Cannon | 1,800 | −150 | 1,650 | Damage 145, ROF 140 f, range 14, area 2 |
| Hyperion | 2,000 | −200 | 2,000 | AA damage 30, ROF 2 f, range 15, area 0.7; cap 2 |
| Repair Crane | 800 | −100 | 800 | Vehicle repair radius 4 |
| Psychic Dominator | 5,000 | −400 | 1,350 | Native 10-minute recharge |
| Tesla Reactor | 600 | +150 | 750 | Ordinary early power |
| Nuclear Reactor | 2,000 | +2,000 | 1,400 | Higher-output faction reactor, dangerous death effect |
| Ore Purifier | 3,000 | −200 | 1,100 | Native economy bonus plus 20 credits/100 f |

Nominal damage divided by ROF is only a comparison tool. Armor, acquisition delay,
burst timing, splash, retargeting and overkill affect actual output.

## Eight campaign structures

| Proposed unlock | Credits | Power | HP | Proposed effect | Default cap |
| --- | ---: | ---: | ---: | --- | ---: |
| Blackout Research Station `GABSTA` | 6,000 | −300 | 2,000 | Manual Blackout Pulse: enemy susceptible buildings in radius 8, EMP330 f, recharge 7 game minutes, activation 1,000 credits | 1 |
| Weather Crystal `GARAIN` | 6,000 | −400 | 1,600 | Regenbogen CrystalHeavyGun: 60×3, ROF 10 f, range 14, two 60-damage shrapnel projectiles per impact; anti-army | 2 |
| Yuri's Bust `CAEAST02` | 3,500 | −200 | 2,000 | Native ground dissolver:100×2, ROF 50 f, range 15; retains veterancy | None |
| Psychic Beacon `NAPSYB` | 5,000 | −250 | 1,500 | 9 reversible mind-control slots; range 12; acquisition every 90 f; ground units | None |
| Psychic Amplifier `NAPSYA` | 15,000 | −900 | 3,200 | 32 reversible mind-control slots; range 18; one acquisition/180 f; ground units, no buildings | 1 |
| Hybrid Tower `GAHYBR` | 5,000 | −300 | 1,050 | Ground weapon 30/ROF 2 f/range 14; bounded links within 6 cells,+20% per helper, maximum 4 helpers | 3 |
| Medic Bunker `NAHOSP` | **600** | **−10** | **1,000** | Retain native one-at-a-time infantry enter/heal/exit; no weapon | None |
| SteinsTech Spectral Tower `FTHQ` | 6,000 | −450 | 2,000 | Lights Out ground beam 150/ROF 40 f/range 20; no prism networking or AA | 1 |

### Identity, feasibility and balancing decisions

**Blackout Research Station.** This is an EMP/ECM installation, not a generic
research/stat power-up provider. In Eclipse it is a 2,000-HP script anchor: triggers
spawn an emitter with radius 225 EMP lasting 660 f; capture/destruction stops the
blackouts. The portable reward needs its own power/provider rather than copying
those triggers. Radius 8 is twice the native Blackout Missile radius, with the
native-style paid cast and slow recharge. It must coexist deliberately with the
existing Blackout Missile Power reward, not produce duplicate free timers.
[Station reference](https://moapyr.fandom.com/wiki/Blackout_Research_Station),
[technology background](https://moapyr.fandom.com/wiki/Development_of_Foehn%27s_technology).

**Weather Crystal.** Use the actual offensive Regenbogen weapon graph. Its warhead
has 0% against conventional building armor; it is not an all-purpose siege tower.
Strip the challenge's `sp_rain` invulnerability, shield animation and objective
flags; give the owned copy normal defensive armor. Native projectiles permit AA,
but legacy `EMEffect` has a documented moving-target problem without Phobos. Keep
AA marked provisional until a cloned-warhead fix is verified against moving aircraft.
[Crystal reference](https://moapyr.fandom.com/wiki/Weather_Crystal),
[Phobos documentation of the legacy issue](https://phobos.readthedocs.io/_/downloads/en/v0.2/pdf/).

**Yuri's Bust.** Preserve its installed 100×2/range 15 values; the wiki's 90×2/range 14
belongs to a different rules revision. The warhead is only 50% against ordinary
heavy vehicle armor, so its burst is not 200 damage to every target. The extra
reach, health and anti-infantry performance justify 3,500 credits. The special
Obsidian Sands AA override does not become a universal unlock property.
[Bust reference](https://moapyr.fandom.com/wiki/Yuri%27s_Bust).

**Psychic Beacon.** The Peace Treaty mission already prices it at 5,000 credits,
250 power and 1,200 HP. Its campaign control is scripted; a reusable 9-slot weapon is
new design. Three Psychic Towers cost 4,500/300 power and provide 9 slots over several
positions; this Beacon trades positional flexibility for 12-cell reach and a
single vulnerable controller. Destroying it releases its controlled units.
[Beacon reference](https://moapyr.fandom.com/wiki/Psychic_Beacon).

**Psychic Amplifier.** The selected design is **32 reversible slots, 15,000 credits,
900 power, range 18 and acquisition every 180 frames**, with 3,200 HP and default cap 1.
It uses ordinary finite tower-style control: controlled units return to their
previous owners when the Amplifier is destroyed. Preserve normal psionic immunity
and restrict acquisition to ground units. Do not use permanent capture or alter
Mastermind overload settings. Finite capacity and a slower acquisition cadence
balance its substantially larger capacity and reach than the Beacon.
[Amplifier reference](https://moapyr.fandom.com/wiki/Psychic_Amplifier).

**Hybrid Tower.** The native placeholder 1,600-credit cost is not a good cross-faction
unlock price for its rapid 30/2 f/range 14 ground weapon. The installed support weapon
has range 15 and inherits a 125% global prism modifier unless explicitly replaced;
chain length 6 does not mean support range 6. The proposal explicitly bounds links
at +20% each. With the default three-building cap, only two helpers can support one
receiver; the four-helper ceiling still bounds it if ordinary caps are lifted.
[Hybrid reference](https://moapyr.fandom.com/wiki/Hybrid_Tower),
[Ares prism forwarding](https://ares-developers.github.io/Ares-docs/new/buildings/prismforwarding.html).

**Medic Bunker.** Keep its existing 600-credit,10-power native price. It is an
infantry support bunker, not an armed defense. Native `Hospital=yes` admits one
patient; general rules heal 20 HP at the `.001` repair interval. Its installed HP is
1,000, despite the wiki listing 600. It is already cheaper than the 800-credit Repair
Crane, with a narrower infantry-only role and far lower power draw.
[Medic reference](https://moapyr.fandom.com/wiki/Medic_Bunker).

**Spectral Tower.** Use Lights Out's actual 150/40 f/range 20 beam rather than
Heavyobject's weaker 120/range 14 override. Remove the mission's `Factory=InfantryType`
convenience and unusual armor. Its range is the premium; it should not also gain
free prism networking or AA. Art is `FAHQ`, footprint 4×4.
[Spectral reference](https://moapyr.fandom.com/wiki/SteinsTech_Spectral_Tower).

## Buildable tech-building access rewards

No ordinary capturable tech building currently has a buildable access reward in
the shipped roster. Add reviewed types through the existing player-owned
special-building/defense system in a later implementation; do not globally make
native map structures buildable. The [official tech structures overview](https://mentalomega.com/index.php?page=tech_structures)
describes their roles. Installed definitions supply the values below.

### Economy, utility, training and support

| Proposed tech reward / native ID | Credits | Power | HP | Effect / ordinary default cap |
| --- | ---: | ---: | ---: | --- |
| Oil Derrick `CAOILD` | 2,000 | 0 | 1,400 | 20 credits/100 f; no startup/capture payout; cap 3 |
| Deposit Bank `CABANK` | 4,000 | 0 | 1,600 | 40 credits/100 f; no startup/capture payout; cap 1 |
| Power Plant `CAPOWR` | 1,000 | +250 | 1,000 | Native power; no cap |
| Nuclear Plant `CANRCT` | 2,000 | +1,000 | 1,100 | Native reduced nuclear death explosion; no cap |
| Ore Refinery `CAREFN` | 1,000 | −25 | 1,000 | Native ore drop-off; no free miner; no cap |
| Base Expansion Post `CAEXPS` | 1,200 | −100 | 1,200 | Native build-radius extension and radius 4 vehicle repair; normal placement rules |
| Satellite Hack Center `CACOMN` | 3,000 | −100 | 1,500 | Native map reveal; cap 1 |
| Infantry Academy `CAACAD` | 2,500 | −100 | 1,300 | New trainable infantry start veteran; cap 1 |
| Heavy Machinery `CAHMCH` | 3,000 | −100 | 1,200 | New trainable non-naval vehicles start veteran; cap 1 |
| Aeronautics `CAAERO` | 3,000 | −100 | 1,200 | New trainable AircraftTypes start veteran; cap 1 |
| Defense Bureau `CADEFB` | 2,500 | −100 | 1,300 | Newly constructed trainable defenses start veteran; cap 1 |
| Military Docks `CADOCK` | 2,000 | −75 | 1,200 | New eligible trainable ships start veteran; cap 1 |
| Machine Shop `CAMACH` | 3,000 | −100 | 1,000 | Native global vehicle self-healing 10 HP/100 f; cap 1 |
| Hospital / Field Hospital `CATHOSP` / `CAFHOSP` | 2,000 | −50 | 1,000 | Global infantry self-healing 20 HP/100 f; one shared reward/cap 1, two visual variants |
| Airfield `CAAIRP` | 2,000 | −75 | 1,100 | Four docks; native paid paradrop 1,200 credits, recharge 4; cap 1 |
| Reinforcement Pad `CATPAD` | 4,000 | −100 | 1,200 | Native automatic faction-specific vehicle shipment, recharge 5; cap 1 |
| Maintenance Facility `CASTRF` | 2,500 | −100 | 1,000 | Native building-maintenance power, radius 12/effect 600f/recharge 5; cap 1 |
| Missile Bunker `CAMISL` | 3,000 | −150 | 1,200 | Native Missile Strike,1,500 credits per activation/recharge 7.5; cap 1 |
| Secret Lab `CASLAB` | 2,000 | −100 | 1,100 | Separate access reward: construct the lab, then produce Rejuvenators at a War Factory while the lab is owned; cap 1 |

Oil and bank both repay their price after 10,000 simulation frames before losses,
without capture bounties. Bank consolidates two derricks into one weaker combined
footprint/HP total. Keeping the refinery miner-free prevents repeated free-unit
purchases. Native Tech Nuclear output is half the ordinary Soviet reactor's at
the same proposed cost: this deliberately pays for faction-independent access and
the reduced native death blast, not maximum energy efficiency. Revisit that price
if it proves unattractive in play.

Academies are one veteran rank, not free elite status, and do not stack.
Aeronautics uses the engine AircraftType category; airborne VehicleTypes follow
vehicle training instead. Heavy Machinery excludes the native naval list, which
must be expanded for player clones. Hospital
and Machine Shop are global maintenance benefits, unlike the local entry-based
Medic Bunker or local vehicle Repair Crane. Passive global bonuses may not obey
`Powered=yes` outages; do not promise low-power shutdown before engine verification.

### Secret Lab and direct Rejuvenator Access

The user confirmed that these are distinct progression paths. Direct Rejuvenator
Access enables the unit once a usable War Factory exists. Secret Lab Access first
unlocks construction of the lab; the player pays its 2,000-credit construction cost
and 100-power requirement before that lab supplies Rejuvenator access.

| Earned access / owned structures | Rejuvenator production from these rewards |
| --- | --- |
| Direct Rejuvenator Access + War Factory; no lab | Available |
| Secret Lab Access + War Factory; lab not constructed | Unavailable |
| Secret Lab Access + constructed/owned lab + War Factory | Available while the lab remains owned |
| Both rewards + War Factory; lab absent or lost | Available through direct Rejuvenator Access |
| Either path without a usable War Factory | Unavailable |

Losing or selling the lab removes only the lab-provided route to future production.
It must not revoke separately earned direct Rejuvenator Access or delete units
already produced. The lab grants a fixed Rejuvenator boon, with no capture/rebuild
reroll. Preserve unrelated native capturable labs and their mission scripts.
The implementation uses explicit owned-lab prerequisites rather than native secret
boon logic. Generated maps verify both routes and compact references; live queue
behavior remains a manual check.

### Native tech defenses and fortifications

Retain native weapon behavior. The first six defense prices already exist in
installed rules; they are the starting recommendation rather than invented costs.

| Tech defense | Credits | Power | HP | Native weapon / capacity |
| --- | ---: | ---: | ---: | --- |
| HMG Tower `CAHMG` | 600 | 0 | 1,050 | 40×2,ROF 20 f,range 10,minimum 2 |
| Turret `CACANN` | 800 | 0 | 1,050 | 100,ROF 60f,range 8 |
| SAM Site `CASSAM` | 800 | 0 | 1,050 | AA50×2,ROF 40 f,range 12.5 |
| Cannon Bunker `CATUR` | 1,500 | −50 | 1,750 | 225,ROF 85 f,range 8.5,minimum 2 |
| Artillery Bunker `CAART` | 1,500 | −100 | 1,750 | 175,ROF 140 f,range 18,minimum 5 |
| SAM Bunker `CASAM` | 1,500 | −50 | 1,750 | AA40×6,ROF 100 f,range 14 |
| Concrete Bunker `CABUNK01–04` | 1,000 | 0 | 2,000 | 8 infantry; one reward covers four orientations |
| Concrete Fortress `CAFORT` | 2,500 | 0 | 4,000 | 20 infantry |
| Concrete Wall `CAWALL` | 100 | 0 | 1,200 | Wall segment |
| Tech Protector `CASHLD` — hold | 2,000 | −150 | 1,000 | Native local vehicle-armor support; disabled until missing-art/placement issue resolved |

Tech Protector Access is already explicitly retired for unavailable artwork.
Do not resurrect its retired reward name or change old-save interpretation to
activate it. Objective-only objects such as `CAOILDOM`/Tech Supply Bunker are not
normal reward candidates. A Tech Resource Forge was not found in this installed roster.

## Reward and compatibility design for later implementation

1. Give each reviewed building a stable access identity under existing defenses or
   special buildings. Ordinary side effects belong to its player-owned clone.
   Visual hospital/bunker variants share an unlock rather than diluting the pool.
2. Never change native IDs, map objectives, AI providers or campaign ownership.
   Campaign-only weapons must be copied with complete dependencies; native same-name
   map overrides must not alter a reward copy later.
3. Review cameos, remaps, foundations, buildup and occupancy. Most tech artwork
   lacks a normal buildup/cameo; Hospital has extra occupancy cells and Expansion
   Post removes some cells. Avoid repeating invisible blocked-cell/deploy failures.
4. Reconcile capture-only flags (`NeedsEngineer`, `Nominal`, `Unsellable`,
   `Insignificant`) in reward copies, with no neutral/objective script tags.
5. Set oil/bank `ProduceCashStartup=0`. Preserve periodic income deliberately;
   no repeated build/sell/capture windfall. [Ares cash production](https://ares-developers.github.io/Ares-docs/new/buildings/producecash.html).
6. Expand both `Academy.Types` and`Academy.Ignore` to each map's actual compact player
   clones. Military Docks whitelists ships; Heavy Machinery excludes them. The
   existing resolver covers `Academy.Types` in power-provider rules only and is not
   a complete solution for all new buildings. [Ares academies](https://ares-developers.github.io/Ares-docs/new/buildings/academy.html).
7. Keep Secret Lab Access and direct Rejuvenator Access as separate reward IDs.
   The lab route requires a constructed/owned player lab plus a usable War Factory;
   the direct route requires no lab. Verify activation on construction and loss/sale
   without revoking direct access or deleting produced units. No random mission
   boons or rebuild rerolls. [Ares Secret Labs](https://ares-developers.github.io/Ares-docs/new/buildings/secretlabs.html).
8. Extend clone-aware refinery docking and Expansion Post provider references.
   Support powers retain their intended recharge, per-use cost and shared-provider
   semantics; duplicate buildings must not silently multiply timers.
9. Preserve frozen old seeds, pending/earned reward IDs and RNG ordering. New
   entries affect deliberately generated new runs; do not rewrite old reward plans.
   Keep Shop/APWorld compatibility decisions explicit and build matching artifacts
   if published catalogues/IDs change. Fortress is a separate product domain.
10. Use the [reward-structure manual checklist](../../testing/MANUAL%20TO-DO/reward-structures.md)
    after real-map audits. All new gameplay effects remain unverified until then.

## Installed evidence locator

Paths are relative to the actual game installation. Game files are not committed.
An ignored factual-stat report is under`logs/campaign-structures-research/` in this
checkout. Rule section IDs are the stable lookup key; line numbers refer to this
specific installed version and can move after updates.

| Evidence | Location / section |
| --- | --- |
| Native baselines and requested structures | `RandomizerLauncherData/cameo_cache/rulesmo.ini`: Hyperion 46349; Prism 46572; GrandCannon46638; Tesla 48335; Crane 48514; Medic 48797; PsychicTower50121; Dominator 50774; Spectral 56363; Hybrid 56387; Blackout 56887; Crystal 56935; Beacon 57384; Amplifier 57507; Bust 64141 |
| Native tech set | Same rules file,52989–54272; Oil 53989; Bank 54028; healing constants 26–29 |
| Named weapons | Same rules file: Hyperion 75465/75480; Bust 83137; Hybrid 84548; mindcontrol 85357; Spectral 87222; BustWH109200 |
| Regenbogen Crystal | `MapsMO/Challenge/c_regenbogen.map`: immunity 25; weapons 82/91; projectile 99; GARAIN147; warhead 1692 |
| Spectral variants | `MapsMO/Cooperative/coop_slights.map:80`; `MapsMO/Challenge/c_heavyobject.map:82` |
| Blackout mission | `expandmo97.mix → SECLIPSE.MAP`: WH49; station 166; emitter 348; team 2306; capture/destruction 3374–3375 |
| Buildable Beacon precedent | `expandmo97.mix → SPEACE.MAP:165–189` |
| Amplifier durability | `expandmo97.mix → ENIGHT.MAP:273–290` |
| Artwork/footprints | `RandomizerLauncherData/cameo_cache/artmo.ini`: Bust 17184; Hybrid 17227; Crystal 21364; Spectral 23567; Beacon 23702/23746; Amplifier 23854 |
| Retired Protector | `configs/rewards/catalogue.json`, `retired_reward_by_name` |
| Academy reference plumbing | `randomizer/maps/base.py`, `resolved_academy_clone_rules` |

## Implementation handoff

The eight selected campaign structures and the complete reviewed functional tech
set are implemented in local 1.49.0. Ordinary caps follow the existing unlimited-
buildings option; there are no hidden economic exceptions. The Amplifier uses
32 reversible slots, and Secret Lab remains independent of direct Rejuvenator
Access. Gladius and Mental Omega Device are excluded.

Static and generated-map audits verify portable definitions, provider references,
lab prerequisites and art dependencies. Actual engine effects, placement,
controller release and two-PC gameplay remain manual checks. See the current
mechanics and tryout instructions in [STRUCTURE_REWARDS.md](../../STRUCTURE_REWARDS.md).
The later explicit implementation request authorized a local test build/install;
publication, PR, merge and release tagging remain unauthorized.
