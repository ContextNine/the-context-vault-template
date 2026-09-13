---
type: agent-reference
status: enabled
---
## Agent Update

`fleet update` is the central approved fleet update operation. It resolves newer versions or source revisions within declared policy, preflights every selected machine, applies the immutable plan, runs normal agent sync once, verifies, and records factual state only after acceptance.

```bash
fleet update --dry-run
fleet update
fleet update --verify
```

The command applies by default. `--dry-run` may resolve upstream versions but writes nothing. `--verify` neither resolves newer state nor writes locks.

Selectors may be combined:

```bash
fleet update --dependencies
fleet update --coding-tools
fleet update --skills
fleet update --workspace-deps
fleet update --vault-dependencies
fleet update --dependency secret-bindings --version 1.2.4 --dry-run
fleet update --dependency secret-bindings --version 1.2.4
```

`--dependencies` selects approved agent packages, applications, access providers, system capabilities, and optional services. Repeatable `--dependency ID` narrows the transaction to named dependencies. For an immutable private component, `--version X.Y.Z` with exactly one dependency changes the desired version, installs that exact catalog release across eligible machines, and records the new desired state only after the fleet apply succeeds. It does not update unrelated dependencies. `--coding-tools` uses one exact T3 nightly version and preserves Codex, Claude Code, and OpenCode installation provenance. `--skills` updates repository-scoped GH skill installations, then syncs current Vault and local-checkout sources. `--workspace-deps` is transitional and reconciles only commands declared by logical workspace ID. `--vault-dependencies` independently updates the public Vault/bootstrap manifest on the full-Vault machine.

Restrict one skill-source operation with a repeatable source selector:

```bash
fleet update --skills --skill-source gh:frontend-slides --dry-run
fleet update --skills --skill-source gh:frontend-slides
fleet update --skills --skill-source gh:skybridge
```

GitHub-managed sources use `gh:<repository-directory>`. The updater runs `gh skill update --all --dir` inside each selected `github/<repo-name>/skills` directory. Existing local checkouts are not updated here; `workspaces.json` and the workspace reconciliation workflow own their Git state.

After GH source acceptance, the command rebuilds overlays and snapshots, validates local checkout links, distributes current skill state, verifies every selected machine, and writes `_system/agents/internal/generated/state/skills.lock.json`. That lock records GH metadata, local source digests and materialization types, and fleet distribution digests. It is factual evidence only and never controls desired state.

`_system/local/dependencies.lock.json` has a separate public-release purpose. Public bootstrap and upgrade may reproduce the skill-source revisions captured by a particular Vault release. Routine `fleet update --skills` never consumes those pins. This separation permits the private fleet package to move sources forward without changing a published bootstrap contract.

Use repeatable `--target MACHINE_ID` or `--local-only` to narrow the operation. An explicit target updates only the named target; the default includes the primary and every enabled eligible worker. Normal sync may still inspect the primary as its source. Disabled machines are rejected and never appear in the default target set.

Update differs from [[Agent Sync]]: sync converges current declared state and never seeks a newer upstream version. Update resolves approved newer state, or adopts one explicitly supplied exact component version, applies typed adapters, calls sync, and verifies. Missing required direct packages remain sync-owned; update never installs software merely discovered on a machine. A second identical accepted update reports current state and makes no source, projection, or target changes.

Every report distinguishes updated, already current, absent, lifecycle-owned, manual, blocked, and failed items. A manual or failed item prevents an aligned-fleet result. Major OS upgrades, firmware, authentication, credential rotation, and production deployment are separate operations.
