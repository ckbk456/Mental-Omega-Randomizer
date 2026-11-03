# Campaign and tech structure reward proposal

**Status: research/proposal only — 2026-11-03.** The user explicitly chose to
propose both sets before implementing them. No reward, unit, weapon, game asset,
installed launcher or save was changed by this research.

Branch: `codex/campaign-structure-rewards`, from local 1.48.1 commit
`30745f68e61a34db594d0a6656c4c4c24bf7dd44`. Repository workflow changes are separate
from this unimplemented balance design.

## Reading the numbers

- Prices are **in-game construction credits**, not Shop Ore/Gems or the price of
  earning a randomizer reward. Each reward unlocks a type; construction still costs money.
- `−power` means continuous consumption; `+power` means generation. Weapon range
  is in map cells. Damage is before armor multipliers. ROF and EMP duration are
  simulation frames (`f`); wall-clock performance changes with selected game speed.
- Support-power recharge values use native `RechargeTime` game minutes. Device
  450 f is 30 nominal game seconds, not a promise of 30 wall-clock seconds at every speed.
- Cost, power, HP and caps below are **recommended initial balance**, unless stated
  as retained native values. They have not been playtested.
- Default caps are ordinary balance proposals. The existing unlimited-buildings
  option must have a documented interaction; no hidden exception is approved here.
  Academies do not become stackable merely because more copies can be built.

## Evidence and installed-engine baseline

The installed rules identify Mental Omega 3.3.6. `Ares.dll` file version is
20.333.289; no `Phobos.dll` was found. The installed rules cache matches the
highest-precedence `RULESMO.INI` in `expandmo 99.mix`:

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

## Ten campaign structures

| Proposed unlock | Credits | Power | HP | Proposed effect | Default cap |
| --- | ---: | ---: | ---: | --- | ---: |
| Blackout Research Station `GABSTA` | 6,000 | −300 | 2,000 | Manual Blackout Pulse: enemy susceptible buildings in radius 8, EMP330 f, recharge 7 game minutes, activation 1,000 credits | 1 |
| Weather Crystal `GARAIN` | 6,000 | −400 | 1,600 | Regenbogen CrystalHeavyGun: 60×3, ROF 10 f, range 14, two 60-damage shrapnel projectiles per impact; anti-army | 2 |
| Yuri's Bust `CAEAST02` | 3,500 | −200 | 2,000 | Native ground dissolver:100×2, ROF 50 f, range 15; retains veterancy | None |
| Psychic Beacon `NAPSYB` | 5,000 | −250 | 1,500 | 9 reversible mind-control slots; range 12; acquisition every 90 f; ground units | None |
| Psychic Amplifier `NAPSYA` | 20,000 | −1,200 | 3,200 | Unlimited **permanent** unit captures; range 18; one acquisition/180 f; no buildings | 1 |
| Mental Omega Device `MODEV` | 100,000 | −5,000 | 10,000 | Desired manual global capture,450 f cooldown, no auto attack or free reveal; universal target coverage requires prototype | 1 |
| Hybrid Tower `GAHYBR` | 5,000 | −300 | 1,050 | Ground weapon 30/ROF 2 f/range 14; bounded links within 6 cells,+20% per helper, maximum 4 helpers | 3 |
| Medic Bunker `NAHOSP` | **600** | **−10** | **1,000** | Retain native one-at-a-time infantry enter/heal/exit; no weapon | None |
| SteinsTech Spectral Tower `FTHQ` | 6,000 | −450 | 2,000 | Lights Out ground beam 150/ROF 40 f/range 20; no prism networking or AA | 1 |
| Gladius Defense System `CADEFN` | 25,000 | −2,500 | 6,000 | Custom AA beam 300/ROF 2 f/range 22;10× Hyperion's nominal weapon output; single-target initial design | 1 |

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

**Psychic Amplifier.** Ares documents unlimited **permanent** mind control. That
means captured units stay yours after the Amplifier dies. Keep normal psionic
immunity and target ground units, not buildings. Do not turn on Mastermind-style
`InfiniteMindControl` and globally disable overload: that would change unrelated
units. If reversible tower-style control is preferred, the alternative proposal
is **32 slots,15,000 credits,900 power,range 18,ROF 180 f**, released on destruction.
That alternative is finite and should be labeled honestly.
[Amplifier reference](https://moapyr.fandom.com/wiki/Psychic_Amplifier),
[Ares permanent mind control](https://ares-developers.github.io/Ares-docs/new/warheads/mindcontrol.html).

**Mental Omega Device.** 100,000 credits and 5,000 power reflect repeated global
ownership changes, far beyond a conventional tower. Keep the native base 10,000 HP,
not campaign 1,000,000 HP/invulnerability. Its 10×10 custom foundation is a real space
cost. Manual-only targeting is documented, but the universal capture promise is
not established: permanent control can affect buildings while retaining normal
immunity; Dominator options can override psionic immunity but do not capture
buildings. GenericWarhead targets a cell, not an exact object, so airborne and
single-object selection need a prototype. Target visible hostile eligible objects;
mission-critical/neutral scripted objectives require an explicit exclusion policy.
Price alone cannot prevent a broken mission. No automatic attacks or free reveal.
[Device reference](https://moapyr.fandom.com/wiki/Mental_Omega_Device),
[Ares manual targeting](https://ares-developers.github.io/Ares-docs/new/superweapons/targeting.html),
[GenericWarhead](https://ares-developers.github.io/Ares-docs/new/superweapons/types/genericwarhead.html),
[Dominator options](https://ares-developers.github.io/Ares-docs/new/superweapons/types/psychicdominator.html).

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

**Gladius.** Native `CADEFN` is a 3,000-HP story object with no reusable weapon.
Its anti-ICBM narrative does not imply a functional nuclear-missile interceptor.
A 300/2 f AA beam is exactly 10× the Hyperion's 30/2 f nominal output, with more range
and a 12.5× construction/power cost. It is strong enough to satisfy the requested
AA role without claiming ten targets. Ares split projectiles can retarget, but
neither splits nor `Burst=10` guarantees ten different simultaneous targets.
Treat multi-target fire as a separate prototype, not a promised first version.
[Gladius reference](https://moapyr.fandom.com/wiki/Gladius_Defense_System),
[Ares splits](https://ares-developers.github.io/Ares-docs/new/projectiles/splits.html).

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
| Secret Lab `CASLAB` — conditional | 2,000 | −100 | 1,100 | Fixed Rejuvenator access while owned; cap 1; canonical unlock/reward overlap must be decided first |

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
7. Secret Lab's fixed native `REJU` boon overlaps Rejuvenator Access. Resolve the
   canonical relationship and construction-vs-capture behavior before inclusion;
   no random mission boons or rebuild rerolls. [Ares Secret Labs](https://ares-developers.github.io/Ares-docs/new/buildings/secretlabs.html).
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
| Native baselines and requested structures | `RandomizerLauncherData/cameo_cache/rulesmo.ini`: Hyperion 46349; Prism 46572; GrandCannon46638; Tesla 48335; Crane 48514; Medic 48797; PsychicTower50121; Dominator 50774; Device 56331; Spectral 56363; Hybrid 56387; Blackout 56887; Crystal 56935; Beacon 57384; Amplifier 57507; Gladius 57958; Bust 64141 |
| Native tech set | Same rules file,52989–54272; Oil 53989; Bank 54028; healing constants 26–29 |
| Named weapons | Same rules file: Hyperion 75465/75480; Bust 83137; Hybrid 84548; mindcontrol 85357; Spectral 87222; permanent controller warhead 104156; BustWH109200 |
| Regenbogen Crystal | `MapsMO/Challenge/c_regenbogen.map`: immunity 25; weapons 82/91; projectile 99; GARAIN147; warhead 1692 |
| Spectral variants | `MapsMO/Cooperative/coop_slights.map:80`; `MapsMO/Challenge/c_heavyobject.map:82` |
| Blackout mission | `expandmo 97.mix → SECLIPSE.MAP`: WH49; station 166; emitter 348; team 2306; capture/destruction 3374–3375 |
| Buildable Beacon precedent | `expandmo 97.mix → SPEACE.MAP:165–189` |
| Amplifier durability | `expandmo 97.mix → ENIGHT.MAP:273–290` |
| Device mission extremes | `expandmo 99.mix → AHAMARTIA.MAP:3699–3706`, `EMIGDAL.MAP:4594–4602` |
| Artwork/footprints | `RandomizerLauncherData/cameo_cache/artmo.ini`: Bust 17184; Hybrid 17227; Crystal 21364; Gladius 21620; Device 22242; Spectral 23567; Beacon 23702/23746; Amplifier 23854 |
| Retired Protector | `configs/rewards/catalogue.json`, `retired_reward_by_name` |
| Academy reference plumbing | `randomizer/maps/base.py`, `resolved_academy_clone_rules` |

## Decisions before gameplay implementation

Recommended first group: Medic Bunker, Bust, Weather Crystal, Hybrid and Spectral,
plus verified economic/support/training tech structures. Beacon follows with a new
isolated weapon. Blackout needs a dedicated provider. Amplifier, Device and Gladius
need the specific behavior decisions and engine checks described above.

Choose permanent versus 32-slot reversible Amplifier; desired Device exceptions;
whether a powerful single-target Gladius is acceptable before multi-target research;
which economic caps the unlimited-buildings option may lift; and whether Secret
Lab adds a distinct reward or is an alternate Rejuvenator access route. These are
pending balance/product decisions, not requests to publish, merge or install.
