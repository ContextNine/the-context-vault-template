---
type: agent-reference
status: enabled
---
## Agent Sync

Sync converges the versions and sources currently declared by the primary; it never searches for newer upstream state. Use [[Agent Update]] or `$infra-i-update-fleet-dependencies` when the intent is to update versions, applications, or skill sources.

Read [[_system/agents/edit/skills/_agents/agents-i-write-or-edit-a-skill/references/skill-authoring|Skill SOP]] for source, grouping, policy, dependency, and collision rules. The canonical command applies all selected changes by default:

```bash
fleet sync
fleet sync --dry-run
fleet sync --verify
```

With no component flags, sync applies approved direct dependencies, managed workspaces, workspace-built commands, skills, settings, and rendered instructions in that order. Select any subset by combining:

```bash
fleet sync --dependencies
fleet sync --dependency secret-bindings
fleet sync --workspaces
fleet sync --workspace-deps
fleet sync --skills
fleet sync --config
fleet sync --instructions
fleet sync --skills --instructions
```

`--skills` validates source policy, rebuilds the Vault's generated symlink catalog, and reconciles `~/.agents/skills` on the primary and every enabled target. Vault, GH, and prefixed skills are portable copies. Unprefixed local-checkout skills remain direct links or policy overlays against that machine's own `~/` checkout. Claude, Kilo, and Kilocode use per-skill aliases to the canonical global directory. Unmanaged skills are preserved.

`--dependencies` validates the complete typed registry at `_system/agents/internal/defaults/dependencies.json`, then installs and verifies required direct packages that match each machine's eligibility. Repeatable `--dependency ID` narrows the run to the named dependency and its transitive requirements; it does not inspect or update unrelated software. The `sshfs` package uses `remote-vault-clients` eligibility and is not installed on code-only Linux workers. Sync installs its value-free reference bundle under `~/.agents/`, with operating guidance owned by the relevant installed skills. Coding tools, applications, providers, system capabilities, workspace commands, and optional services remain explicit registry entries routed to their lifecycle adapters. `--workspaces` reconciles exact checkouts from `_system/agents/edit/settings/fleet/workspaces.json`. `--workspace-deps` runs tracked repository-owned installers declared in `_system/agents/edit/settings/dependencies/selections.json` only after checkout safety checks. Verified target state lives under `~/.agents/state`; the primary collects sanitized evidence in `_system/agents/internal/generated/state/dependencies.lock.json`.

Component-only dependency runs update only their selected aggregate-lock section. For example, `--workspace-deps` refreshes workspace evidence while preserving previously confirmed direct-dependency evidence; an unselected section is never replaced with `null`.

Remote macOS workspace installers run as disposable `launchctl` jobs in the logged-in user's GUI bootstrap domain so native Keychain-backed prerequisites remain available. The worker uses owner-only temporary output files, records only sanitized installer evidence, removes the job afterward, and never moves a credential into SSH, argv, or Vault state. Linux installers continue in the authenticated SSH user context with Secret Service supplied by that machine.

`--config` distributes the authoritative value-free settings into `~/.agents/settings`, plus Mattbook's `~/.codex/config.toml`, `~/.claude/settings.json`, and non-secret coding-agent service metadata such as the Langfuse instance descriptor. `--instructions` writes `~/.agents/instructions/AGENTS.md` and manages the Codex and Claude links to it. Machine-specific paths and safety overlays are rendered per target. Credentials remain machine-local and independently enrolled. Target-local Codex plugin and marketplace tables are preserved.

`--instructions` composes base, platform, role, machine, then explicitly registered Vault-authored skill fragments into `~/.codex/AGENTS.md` and keeps `~/.claude/CLAUDE.md` linked to it. When the registry has another enabled fleet machine, the machine section includes reverse-forwarded development-preview instructions rendered with the registered primary SSH alias and loopback port placeholders. A single-machine registry omits them. The schema-v7 machine footer tells code-only Linux workers to stop, remote clients to require a successful `vault access status` before reading or editing and avoid Vault Git, Gitless Mac hosts to remain Gitless, and the owner to commit the complete worktree currently visible without waiting for iCloud upload. Workspace and third-party skills cannot register global instruction fragments.

Every run preflights all selected enabled targets before applying. Use repeatable `--target MACHINE_ID`, `--local-only`, or `--require-repo-sources` when narrowing scope or performing machine acceptance. Mac mini is disabled and is never selected. The Vault intentionally provides no agent-package aliases; one package has one CLI.

Source roots:

- `_system/agents/edit/skills/<_group>`: canonical Vault-owned sources. `-i-` and invocation metadata must agree.
- `_system/agents/edit/skills/github/<repo-name>/skills`: publisher-managed `gh skill` installs.
- `_system/agents/internal/generated/overlays`: generated linked policy views.
- `_system/agents/internal/generated/snapshots`: generated prefixed copies.
- `_system/agents/internal/generated/catalog`: generated Vault-local flat symlink catalog.

Sync validates every source and global collision before changing files. It enrolls only local repositories declared in `skill-sources.json`; `workspaces.json` remains independent. Strict `--require-repo-sources` verifies that every selected target has its own configured checkout and never follows links into another machine or the Vault mount.

After a skill apply, restart Codex or open a new task because the current task's skill catalog is cached.
