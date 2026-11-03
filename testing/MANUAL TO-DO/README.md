# Consolidated manual QA

Manual results belong to a named build, game installation, map, settings and player
configuration. Record pass/fail/pending with evidence; do not infer a gameplay pass
from a map audit, screenshot, compiler or successful process launch.

| Domain | Checklist / owning guide | Current gate |
| --- | --- | --- |
| New campaign/tech reward buildings | [Reward structures](reward-structures.md) | Proposal pending; no new building behavior verified |
| Solo/AI/human challenges, houses, colors, results | [Existing challenge guide](../../CHALLENGES_TESTING.md) | Recheck changed behavior in an actual match |
| Mixed pools, saved runs, Shop and adaptive parties | [Mixed-run guide](../../MIXED-RUNS.md) | Two-PC gameplay remains pending for local 1.48.1 |
| Native connection and guest restore | [Connection guide](../../COOP_CONNECTION_GUIDE.md) | Requires both named machines/builds |
| Fortress maps, waves, perks and 2–3 players | [Fortress guide](../../FINAL_FORTRESS.md) | Map audit is separate from live survival/peer QA |
| Installation, update and rollback | [Update/release guide](../../UPDATING.md) | Named installed EXE/APWorld and recovery check |

The implementation owner updates the corresponding guide in the same change.
Keep results under ignored `logs/` or attach sanitized release/PR evidence. Never
commit full copyrighted game maps, personal profiles, pairing codes or credentials.
