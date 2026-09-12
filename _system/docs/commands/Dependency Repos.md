---
type: agent-reference
status: enabled
---
# Skill Source Repositories

Skill enrollment is private agent-package configuration at:

```text
_system/agents/_package/instance/skills/skill-sources.json
```

It has two responsibilities:

- `gh_skills` adds optional prefix or invocation policy to repository-scoped installs already present under `_system/agents/skills/github/<repo-name>/skills`.
- `repos` enrolls skills from existing local checkouts using literal `~/` paths and either `all_skills: true` or explicit source-only selections.

The registry does not clone or reconcile repositories. `_system/agents/_package/instance/fleet/workspaces.json` independently owns repository registration and reconciliation. A checkout can supply skills without being registered there.

Validate and inspect configuration with:

```bash
fleet config validate
fleet config get skills.sources
```

Install public third-party skills with `gh skill install --dir "$(vault root)/_system/agents/skills/github/<repo-name>/skills"`. Update them through:

```bash
fleet update --skills --dry-run
fleet update --skills
fleet update --skills --skill-source gh:<repo-name>
```

Update operates only on GH-managed installs. It does not mutate local checkout Git state. Normal skill sync resolves each configured `~/` path on every target machine, then creates a direct link, linked policy overlay, or prefixed snapshot according to the Skill SOP.

Public Vault install, upgrade and release never consume the private registry. Public agent export includes reviewed canonical Vault and licensed GH sources; it excludes local-checkout skills and generated materializations.

Executable dependencies belong in `_system/agents/_package/defaults/dependencies.json`. Skill sources never install arbitrary executable hooks.
