from __future__ import annotations

import sys
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


BOOTSTRAP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOTSTRAP))

from install_skill_system import SkillSystemInstallError, connect_vault, copy_standalone, existing_source, install_tree


class SkillSystemBootstrapTests(unittest.TestCase):
    def test_vault_first_can_add_a_standalone_skill_source_later(self) -> None:
        if sys.platform != "darwin":
            self.skipTest("local Vault ownership requires macOS")
        agents = BOOTSTRAP.parent / "agents"
        sys.path.insert(0, str(agents / "internal/src"))
        from package_export import export
        from package_installer import installed_source

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "standalone"
            export(source, apply=True)
            vault = root / "Vault"
            vault.mkdir()
            home = root / "home"
            home.mkdir()
            process = subprocess.run(
                ["bash", str(source / "install.sh")],
                env={**os.environ, "HOME": str(home), "CTX9_NON_INTERACTIVE": "1", "CTX9_VAULT_ROOT": str(vault)},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(installed_source(home), source.resolve())
            self.assertFalse((vault / "_system/agents").exists())
            self.assertIn(str(vault), (source / "edit/settings/fleet/machines.json").read_text())

    def test_vault_first_can_add_a_vault_owned_skill_source_later(self) -> None:
        if sys.platform != "darwin":
            self.skipTest("local Vault ownership requires macOS")
        agents = BOOTSTRAP.parent / "agents"
        sys.path.insert(0, str(agents / "internal/src"))
        from package_export import export
        from package_installer import installed_source

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "public-skill-release"
            export(source, apply=True)
            home = root / "home"
            home.mkdir()
            vault = root / "Vault"
            bootstrap = vault / "_system/bootstrap"
            bootstrap.mkdir(parents=True)
            shutil.copy2(BOOTSTRAP / "install_skill_system.py", bootstrap / "install_skill_system.py")
            process = subprocess.run(
                ["bash", str(source / "install.sh"), "--vault-source", str(vault)],
                env={**os.environ, "HOME": str(home), "CTX9_NON_INTERACTIVE": "1"},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(installed_source(home), (vault / "_system/agents").resolve())
            self.assertFalse((vault / "_system/agents/.git").exists())
            self.assertTrue((vault / "_system/agents/edit/agent-instructions/AGENT-INSTRUCTIONS.md").is_file())
            repeated = subprocess.run(
                ["bash", str(source / "install.sh"), "--vault-source", str(vault)],
                env={**os.environ, "HOME": str(home), "CTX9_NON_INTERACTIVE": "1"},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(installed_source(home), (vault / "_system/agents").resolve())

    def test_standalone_copy_has_its_own_repository_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.source_repo(root)
            (source / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            (source / "internal/src/fleet.py").write_text("# test\n", encoding="utf-8")
            destination = root / "owned" / "skills"
            self.assertEqual(copy_standalone(source, destination), destination.resolve())
            self.assertTrue((destination / ".git").is_dir())
            self.assertTrue((destination / "edit/skills/_test/example/SKILL.md").is_file())
            self.assertFalse((source / ".git").exists())
            with self.assertRaisesRegex(SkillSystemInstallError, "refusing to overwrite"):
                copy_standalone(source, destination)

    def test_existing_standalone_source_connects_without_copying_into_vault(self) -> None:
        agents = BOOTSTRAP.parent / "agents"
        sys.path.insert(0, str(agents / "internal/src"))
        from package_export import export
        from package_installer import install

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "standalone"
            export(source, apply=True)
            home = root / "home"
            home.mkdir()
            with patch("package_installer.platform.system", return_value="Darwin"):
                install(source, home, apply=True, global_instructions=True, claude_alias=False,
                        discovery_aliases=True, machine_id="primary", initialize_source=True)
            vault = root / "Vault"
            vault.mkdir()
            self.assertEqual(existing_source(home), source.resolve())
            self.assertEqual(connect_vault(source, home, vault), source.resolve())
            self.assertFalse((vault / "_system/agents").exists())
            self.assertEqual(existing_source(home), source.resolve())
            source_registry = (source / "edit/settings/fleet/machines.json").read_text()
            self.assertIn(str(vault), source_registry)
            self.assertIn("Vault root:", (home / ".agents/instructions/AGENTS.md").read_text())
            self.assertEqual(connect_vault(source, home, vault), source.resolve())

    def source_repo(self, root: Path) -> Path:
        source = root / "source"
        settings = source / "edit/settings"
        settings.mkdir(parents=True)
        (settings / "profile.json").write_text("{}\n", encoding="utf-8")
        (source / "internal/src").mkdir(parents=True)
        skill = source / "edit/skills/_test/example"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: example\ndescription: Test.\n---\n", encoding="utf-8")
        return source

    def test_opt_out_leaves_agents_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            vault.mkdir()
            self.assertFalse((vault / "_system/agents").exists())

    def test_opt_in_copies_public_tree_and_initializes_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            vault = root / "vault"
            vault.mkdir()
            install_tree(self.source_repo(root), vault, source_url="test", release_version="0.1.0", commit="abc")
            self.assertTrue((vault / "_system/agents/edit/skills/_test/example/SKILL.md").is_file())
            self.assertTrue((vault / "_system/agents/edit/settings/profile.json").is_file())
            self.assertTrue((vault / "_system/local/state/skill-system-install.json").is_file())

    def test_existing_agents_tree_is_preserved_and_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            vault = root / "vault"
            existing = vault / "_system/agents"
            existing.mkdir(parents=True)
            marker = existing / "keep.txt"
            marker.write_text("keep\n", encoding="utf-8")
            with self.assertRaisesRegex(SkillSystemInstallError, "refusing to overwrite"):
                install_tree(self.source_repo(root), vault, source_url="test", release_version="0.1.0", commit="abc")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")


if __name__ == "__main__":
    unittest.main()
