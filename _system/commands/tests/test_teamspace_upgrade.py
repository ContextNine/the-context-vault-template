"""Exercise saved teamspace data conversion through the public migration CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SYSTEM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYSTEM / "bootstrap"))
from bootstrap_vault import entity_dashboard_base


class TeamspaceUpgradeTests(unittest.TestCase):
    def run_migration(self, root: Path, report: Path, apply: bool) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SYSTEM / "migrations/002-teamspace-terminology.py"),
             "--root", str(root), "--report", str(report), "--apply" if apply else "--dry-run"],
            text=True, capture_output=True,
        )

    def test_upgrade_preserves_user_content_registration_and_custom_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vault"
            report = Path(temporary) / "report.json"
            folder = root / "studio"
            bases = folder / "_obsidian/bases"
            bases.mkdir(parents=True)
            note = folder / "studio.md"
            original = "---\nstatus: active\ncontext_registered: false\n---\nMy context matters.\n![[studio/_obsidian/bases/context-dashboard.base]]\n[[Context Folders|Context Folders]]\n"
            note.write_text(original)
            old = bases / "context-dashboard.base"
            custom = entity_dashboard_base("studio").replace("Teamspace Folder Files", "Context Folder Files") + "# My custom view\n"
            old.write_text(custom)
            new = bases / "teamspace-dashboard.base"
            new.write_text(entity_dashboard_base("studio"))
            config = root / "_system/bootstrap/init-vault-config.json"
            config.parent.mkdir(parents=True)
            config.write_text(json.dumps({"context_folders": [{"name": "studio", "status": "archived"}]}))
            rollup = root / "_system/_obsidian/periodic/daily/2030-01-01.md"
            rollup.parent.mkdir(parents=True)
            rollup.write_text("---\nsource_context_folders:\n  - studio\n---\nSaved rollup.\n")
            task = folder / "_obsidian/tasks/Call.md"
            task.parent.mkdir()
            task.write_text("---\ncontexts:\n  - studio\n---\nCall the customer.\n")
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}

            dry = self.run_migration(root, report, False)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})
            applied = self.run_migration(root, report, True)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertFalse(old.exists())
            self.assertEqual(new.read_text(), custom.replace("Context Folder Files", "Teamspace Folder Files"))
            self.assertEqual(note.read_text(), original.replace("context_registered", "teamspace_registered").replace("context-dashboard", "teamspace-dashboard").replace("Context Folders", "Teamspace Folders"))
            self.assertEqual(task.read_bytes(), before[task.relative_to(root)])
            self.assertIn("source_teamspace_folders:", rollup.read_text())
            self.assertEqual(json.loads(config.read_text()), {"teamspace_folders": [{"name": "studio", "status": "archived"}]})

            inventory = subprocess.run([sys.executable, str(SYSTEM / "commands/inventory.py"), "--root", str(root), "--json"], capture_output=True, text=True)
            self.assertEqual(inventory.returncode, 0, inventory.stderr)
            self.assertEqual(json.loads(inventory.stdout)["teamspaces"], [])
            again = self.run_migration(root, report, True)
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertEqual(json.loads(report.read_text())["changed"], [])

    def test_conflicting_dashboard_stops_before_any_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vault"
            report = Path(temporary) / "report.json"
            bases = root / "studio/_obsidian/bases"
            bases.mkdir(parents=True)
            (root / "studio/studio.md").write_text("---\nstatus: active\ncontext_registered: true\n---\n")
            (bases / "context-dashboard.base").write_text("# Original custom dashboard\n")
            (bases / "teamspace-dashboard.base").write_text("# Different custom dashboard\n")
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = self.run_migration(root, report, True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertTrue(json.loads(report.read_text())["errors"])
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
