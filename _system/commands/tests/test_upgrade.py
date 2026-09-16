#!/usr/bin/env python3
"""Tests for public bootstrap upgrade reporting."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

UPGRADE_PATH = SCRIPT_DIR / "upgrade.py"
SPEC = importlib.util.spec_from_file_location("upgrade", UPGRADE_PATH)
assert SPEC and SPEC.loader
upgrade = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = upgrade
SPEC.loader.exec_module(upgrade)


def latest_report(root: Path) -> dict[str, object]:
    reports = sorted((root / upgrade.REPORT_ROOT).glob("*/report.json"))
    assert reports
    return json.loads(reports[-1].read_text(encoding="utf-8"))


class UpgradeFailureTests(unittest.TestCase):
    def patch_common(self, root: Path) -> list[mock._patch]:
        install = {"installed_commit": "oldcommit", "installed_version": "0.1.0"}
        release = {
            "version": "0.1.1",
            "tag": "v0.1.1",
            "dependency_lock_sha256": "abc123",
            "repo_url": upgrade.DEFAULT_REPO_URL,
        }
        return [
            mock.patch.object(upgrade, "ensure_install_state", return_value=(install, root / "state", root / "git")),
            mock.patch.object(upgrade, "fetch_latest", return_value="newcommit"),
            mock.patch.object(upgrade, "load_policy", return_value={}),
            mock.patch.object(upgrade, "latest_release", return_value=release),
            mock.patch.object(upgrade, "changed_paths", return_value=[]),
            mock.patch.object(upgrade, "write_install"),
            mock.patch.object(upgrade, "git"),
        ]

    def test_migration_failure_reports_attempt_and_preserves_install_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            patches = self.patch_common(root)
            patches.append(mock.patch.object(upgrade, "run_migrations", return_value=[{"path": "m.py", "result": "failed"}]))
            patches.append(mock.patch.object(upgrade, "run_dependency_sync"))
            with patches[0] as _ensure, patches[1], patches[2], patches[3], patches[4], patches[5] as write_install, patches[6], patches[7], patches[8] as deps:
                with self.assertRaisesRegex(SystemExit, "Migration failed"):
                    upgrade.run_upgrade(root, apply=True)

            report = latest_report(root)
            self.assertEqual(report["result"], "failed")
            self.assertEqual(report["from_version"], "0.1.0")
            self.assertEqual(report["to_version"], "0.1.1")
            self.assertEqual(report["release_tag"], "v0.1.1")
            self.assertEqual(report["dependency_lock_sha256"], "abc123")
            write_install.assert_not_called()
            deps.assert_not_called()

    def test_dependency_failure_reports_attempt_and_preserves_install_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            patches = self.patch_common(root)
            patches.append(mock.patch.object(upgrade, "run_migrations", return_value=[]))
            patches.append(
                mock.patch.object(
                    upgrade,
                    "run_dependency_sync",
                    return_value={"result": "failed", "stdout": "", "stderr": ""},
                )
            )
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as write_install, patches[6], patches[7], patches[8]:
                with self.assertRaisesRegex(SystemExit, "Dependency sync failed"):
                    upgrade.run_upgrade(root, apply=True)

            report = latest_report(root)
            self.assertEqual(report["result"], "failed")
            self.assertEqual(report["from_commit"], "oldcommit")
            self.assertEqual(report["to_commit"], "newcommit")
            self.assertEqual(report["error"], "Dependency sync failed.")
            write_install.assert_not_called()

    def test_user_edited_vault_skill_blocks_upgrade_before_other_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ordinary = root / "_system/commands/example.py"
            ordinary.parent.mkdir(parents=True)
            ordinary.write_text("keep local\n", encoding="utf-8")
            skill = root / ".agents/skills/vault-i/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("user edit\n", encoding="utf-8")
            patches = self.patch_common(root)
            patches[2] = mock.patch.object(
                upgrade,
                "load_policy",
                return_value={"actions": {"replace": ["_system/commands/**", ".agents/skills/vault-i/**"]}},
            )
            patches[4] = mock.patch.object(
                upgrade,
                "changed_paths",
                return_value=[
                    upgrade.Change(status="M", path="_system/commands/example.py"),
                    upgrade.Change(status="M", path=".agents/skills/vault-i/SKILL.md"),
                ],
            )
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], \
                mock.patch.object(upgrade, "managed_skill_conflict", return_value="conflict"), \
                mock.patch.object(upgrade, "write_from_git") as write_from_git:
                with self.assertRaisesRegex(SystemExit, "Managed Vault skill conflict"):
                    upgrade.run_upgrade(root, apply=True)
            write_from_git.assert_not_called()
            self.assertEqual(ordinary.read_text(encoding="utf-8"), "keep local\n")
            self.assertEqual(skill.read_text(encoding="utf-8"), "user edit\n")


if __name__ == "__main__":
    unittest.main()
