"""Canonical vault-relative paths and stable generated-file ownership IDs."""

from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_DIR = Path("_system")
COMMANDS_DIR = SYSTEM_DIR / "commands"
BOOTSTRAP_DIR = SYSTEM_DIR / "bootstrap"
DEPS_DIR = SYSTEM_DIR / "deps"
DOCS_DIR = SYSTEM_DIR / "docs"
INBOX_DIR = SYSTEM_DIR / "inbox"
LOCAL_DIR = SYSTEM_DIR / "local"
MIGRATIONS_DIR = SYSTEM_DIR / "migrations"
STATE_DIR = LOCAL_DIR / "state"
ATTACHMENT_STATE_DIR = STATE_DIR / "attachments"
SYSTEM_OBSIDIAN_DIR = SYSTEM_DIR / "_obsidian"
VAULT_PERIODIC_DIR = SYSTEM_OBSIDIAN_DIR / "periodic"
AGENTS_DIR = SYSTEM_DIR / "agents"
AGENT_EDIT_DIR = AGENTS_DIR / "edit"
AGENT_INTERNAL_DIR = AGENTS_DIR / "internal"
AGENT_SCRIPTS_DIR = AGENT_INTERNAL_DIR / "src"
AGENT_SETTINGS_DIR = AGENT_EDIT_DIR / "settings"
SKILL_CONFIG_DIR = AGENT_SETTINGS_DIR / "skills/config"
SYNC_DIR = SYSTEM_DIR / "sync"
TOOLS_DIR = SYSTEM_DIR / "tools"

DASHBOARD_PATH = Path("Dashboard.md")
VAULT_CONFIG_PATH = LOCAL_DIR / "vault.json"
DASHBOARD_ACTION_LINKS_PATH = LOCAL_DIR / "dashboard-action-links.md"
SKILL_SOURCE_CONFIG_PATH = AGENT_SETTINGS_DIR / "skills/skill-sources.json"
DEPENDENCY_LOCK_PATH = LOCAL_DIR / "dependencies.lock.json"
VAULT_PACKAGE_MANIFEST_PATH = DEPS_DIR / "packages.yaml"
MACHINE_REGISTRY_PATH = AGENT_SETTINGS_DIR / "fleet/machines.json"
WORKSPACE_REGISTRY_PATH = AGENT_SETTINGS_DIR / "fleet/workspaces.json"
WORKSPACE_DEPENDENCY_PATH = AGENT_SETTINGS_DIR / "dependencies/selections.json"
AGENT_PACKAGE_MANIFEST_PATH = AGENT_INTERNAL_DIR / "defaults/dependencies.json"
AGENT_DEPENDENCY_LOCK_PATH = AGENT_INTERNAL_DIR / "generated/state/dependencies.lock.json"

BOOTSTRAP_POLICY_PATH = BOOTSTRAP_DIR / "upgrade-policy.json"
RELEASE_PATH = BOOTSTRAP_DIR / "release.json"
INSTALL_STATE_PATH = STATE_DIR / "install.json"
UPGRADE_REPORTS_DIR = STATE_DIR / "upgrade-reports"
EXPORT_MANIFEST_PATH = STATE_DIR / "export-manifest.json"

MANAGED_DASHBOARD = "vault.dashboard"
MANAGED_PERIODIC = "vault.periodic"
MANAGED_CONTENT = "vault.content"
MANAGED_BOOTSTRAP = "vault.bootstrap"
MANAGED_TASK_CONTEXT_VIEWS = "vault.bootstrap.task-context-views"
MANAGED_EPIC_VIEWS = "vault.epic-views"
