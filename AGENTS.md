# Repository operating contract

## Scope and communication

- Work in this repository only. Communicate in clear English with evidence and
  constructive criticism. Preserve the task title unless explicitly asked to rename it.
- Research, reviews and proposals do not authorize gameplay implementation.
  An implementation request authorizes scoped changes and a local commit.
- Publishing branches/PRs, merging, tagging releases, updating installed games,
  production operations and destructive cleanup each need explicit task authority.
  A previous release is not permission to publish the next one.
- Never print credential values or commit personal profiles, game archives or logs.

## Git, ownership and processes

- Upstream integration is `origin/main` at Heinki/Mental-Omega-Randomizer.
  Verify remote HEAD and fetch state; this checkout historically fetched only a tag.
- Use `codex/<short-kebab-case-task>` branches. Never edit integration directly.
  Respect an explicitly requested baseline, including a branch from current HEAD.
- Reuse an isolated task-owned checkout where appropriate; otherwise use a dedicated
  worktree. Preserve unrelated dirty/untracked work; never stash/reset it implicitly.
- The primary agent owns scope, shared contracts, dependency ordering, combined
  validation, and the final delivery recommendation. Delegate bounded independent work.
  Implementation agents each own a branch/worktree and file/domain scope; do not race
  on shared core files. Read-only research may share the checkout.
- Each delegation states objective, included/excluded scope, dependencies, interfaces,
  checks, documentation ownership, publication authority and remaining human gates.
  Agent reports require verification.
- Inspect equivalent running processes before intensive validation. Run at most one
  CPU-intensive command per worktree, retain/poll its session, and avoid watch mode.
  Investigate builds exceeding 15 minutes; do not automatically terminate them.
- Stop only task-owned process trees. Do not close a player's launcher or game.
  Before recursive Windows filesystem changes, verify absolute paths against the
  intended workspace and use native PowerShell operations with literal paths.
- Preserve file encodings and existing line endings; stage only intended paths.

## Read before changing behavior

[Documentation index](docs/README.md) identifies the existing owning guides.
[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) owns architecture and compatibility rules;
[configs/README.md](configs/README.md) owns editable data conventions.

- Keep native campaign types and scripts intact; player rewards use owned copies.
- Preserve serialized reward/check IDs, aliases, RNG call order and old saves.
  New random choices require a separately named deterministic stream.
- Preserve INI ordering, repeated sections, numeric entries and CRLF behavior;
  use the existing INI parser, not ConfigParser.
- Preserve Ares IDs <=24 characters, Actions <=511 UTF-8 bytes, veteran lists
  <=480 bytes. Do not assume optional engine extensions are installed.
- Keep pure logic out of Tk controllers. Workers receive frozen plain data.
- Final Fortress remains independent of Shop/Grid saves, economy and launch state.
- `randomizer/core/version.py` owns versions. Catalogue/AP changes require matching
  launcher and APWorld artifacts. Never alter published releases in place.
- No separate signed-off/protected-document register currently exists. Consult the
  user before changing any subsequently designated protected product/security/legal
  contract; research documents cannot override current behavior or compatibility.

## Validation policy

**This project does not use unit tests.** Do not add, generate, restore or run unit
tests, pytest/unittest, mocks, or synthetic scenarios disguised as self-checks.
Keep CI/build scripts free of unit-test runners. This project-specific rule takes
precedence over generic workflow advice about testing layers.

Use compilation, static configuration integrity, real installation/catalogue
reports, audits of actual installed maps, packaging and manual gameplay. The
[command registry](docs/DEVELOPMENT_WORKFLOW.md#command-registry) records exact
commands, environment, source, estimated duration and CPU cost. Do not claim the
full PR gate passed from compilation alone. Record passed/failed/skipped/unavailable
checks separately; there is no configured standalone formatter, linter or typecheck.

## Documentation, manual QA and delivery

- Update the owning current-logic guide with a behavior change. Keep proposals in
  `docs/research/` and status in [the scoped roadmap](docs/ROADMAP.md); neither is
  an implemented product contract. Archive documents only when they become obsolete.
- [Manual QA index](testing/MANUAL%20TO-DO/README.md) consolidates domain ownership.
  Capture actual target/version/results; artifact capture alone does not pass QA.
- Prefer source/API/CLI inspection. Agent-operated browser/native UI testing requires
  an explicit request. Never interact with unrelated windows or accounts.
- Existing CI builds the pinned Windows release bundle, runs CodeQL and dependency
  review. Remote CI, live gameplay and two-PC synchronization remain separate gates.
- One coherent concern per PR. For batches: validate each concern, audit dependencies,
  validate the intended combined tree, merge only explicitly authorized heads, then
  perform a post-merge checkpoint. A checkpoint does not authorize all open PRs.
- Use the PR template and, when explicitly requested, the available file-pr skill.
  No automatic push, PR, merge, tag or deployment. Preserve task names after PR creation.
- Handoffs state branch/baseline/worktree, changes, validation, docs, running processes,
  publication/deployment state, remaining human decisions and merge authority.
