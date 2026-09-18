---
type: agent-reference
status: enabled
---
# Bootstrap Export

Export the public bootstrap vault from the current vault:

```bash
vault bootstrap-export --dry-run
vault bootstrap-export --force
```

Use `vault bootstrap-export --force` for local inspection and repair only. For a public version that installed vaults can upgrade to and report against, use:

```bash
vault release publish --dry-run --bump patch
vault release publish --bump patch
```

`vault release publish` preflights both public products, reports which exports changed, and publishes only those products. Each product keeps independent SemVer metadata, tags, commits, and GitHub Releases. Use `--product vault`, `--product skills`, or `--product all` to retry one side after a partial external failure.

The export writes a root `README.md` from `_system/bootstrap/README-public-vault-template.md`. Internal bootstrap/export mechanics live in `_system/bootstrap/README.md`. With `--force`, the exporter mirrors export-owned files into the configured export root while preserving repo metadata such as `.git`, `.github`, `.gitignore`, `.gitattributes`, license files, and contribution docs.

The Vault exporter excludes `_system/agents/**` from its system tree, then explicitly copies only the canonical `vault-i` bundle to `.agents/skills/vault-i` with a Claude discovery alias. The Skill Problem System exporter separately publishes a sanitized root containing `edit/`, `internal/`, and the installation entrypoints. It includes public-safe settings, templates, runtime, schemas, canonical Vault skills, and licensed GH-managed skills. It keeps local-checkout skills, generated views, private settings, and user-excluded paths private, and writes the audit report only to ignored Vault state.

Default export root and teamspace folder output mapping live in:

```text
_system/bootstrap/bootstrap-export.json
```

Implementation script: `_system/commands/bootstrap_export.py`.

Interactive installs ask whether to install or connect the optional CTX9 skill system and public skills. Declining leaves `_system/agents` absent. If a skill system is already installed, accepting connects the Vault to its existing editable source. Otherwise, the user chooses a standalone source repository or a Vault-owned `_system/agents/` tree. The installed runtime is `~/.agents/` in either case. Vault upgrades never overwrite the skill-system source.
