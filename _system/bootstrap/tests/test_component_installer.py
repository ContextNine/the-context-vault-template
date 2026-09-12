from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "component_installer.py"
SPEC = importlib.util.spec_from_file_location("vault_component_installer", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ComponentInstallerTests(unittest.TestCase):
    def test_exact_installed_release_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            metadata = root / "_system/bootstrap/release.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(json.dumps({"version": "1.2.3"}), encoding="utf-8")
            self.assertEqual(MODULE.installed_version(root), "1.2.3")
            with mock.patch.object(MODULE, "installed_root", return_value=root):
                self.assertTrue(MODULE.status("1.2.3")["ready"])
                self.assertFalse(MODULE.status("1.2.4")["ready"])

    def test_existing_different_release_requires_vault_upgrade(self) -> None:
        with mock.patch.object(
            MODULE,
            "status",
            return_value={"ready": False, "installed_version": "1.2.2"},
        ):
            with self.assertRaisesRegex(MODULE.ComponentError, "vault upgrade"):
                MODULE.install({"version": "1.2.3", "tag": "v1.2.3"})


if __name__ == "__main__":
    unittest.main()
