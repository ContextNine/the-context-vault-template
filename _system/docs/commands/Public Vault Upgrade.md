---
type: agent-reference
status: enabled
---
# Public Vault Upgrade

Public bootstrap installs keep upstream Git state outside iCloud and use it for setup updates:

```bash
vault upgrade status
vault upgrade --dry-run
vault upgrade
vault upgrade doctor
vault upgrade repair-prompt
```

Install metadata lives in `_system/local/state/install.json`; exported policy and release metadata live directly under `_system/bootstrap/`. Upgrade reports live under `_system/local/state/upgrade-reports/`.

The teamspace terminology migration converts saved registration and periodic-source fields, setup configuration, and managed dashboard names and links. It preserves TaskNotes' `contexts` field and custom dashboard content. Conflicting dashboard copies stop the migration before it writes anything. Setup choices in `_system/bootstrap/init-vault-config.json` are preserved across upgrades.

Commands now select folders with `--teamspace-folders` and default capture with `--default-teamspace-folder`. Project listing uses `--teamspace`. Update scripts that call these commands; old flag aliases are not accepted. See [[Inventory]] for the current JSON output fields.

`vault upgrade --dry-run` previews only the Vault product. `vault upgrade` applies public Vault bootstrap updates and public Vault dependencies; it does not require, install, update, or inspect a standalone agent package. Agent-package upgrades are an independent `fleet` workflow when that optional product is installed.

If the current vault has no public bootstrap install state, `vault upgrade --dry-run` and `vault upgrade` skip the public bootstrap step and run dependency repo sync only. This lets source/private vaults still use `vault upgrade` as the broad "bring external dependencies current" command.

Implementation script: `_system/commands/upgrade.py`.
