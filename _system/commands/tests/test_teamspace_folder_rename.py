#!/usr/bin/env python3
"""Tests for teamspace folder rename structured rewrites."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from teamspace_folder_rename import rename_teamspace_folder, rewrite_text_for_context, validate_slug  # noqa: E402


class TeamspaceFolderRenameTests(unittest.TestCase):
    def test_validate_slug_accepts_dot_suffix_and_camel_case(self) -> None:
        self.assertEqual(validate_slug("someString.nosync", "new teamspace folder"), "someString.nosync")
        self.assertEqual(validate_slug("business.nosync", "new teamspace folder"), "business.nosync")

    def test_markdown_rewrites_structured_references_only(self) -> None:
        text = """---
entity: business
context_type: business
aliases:
  - business
---
# Note

See [[business/foo]] and ![[business/bar.png]].
Control note: [[business/business|Business]].
Task path: business/_obsidian/tasks/x.md
Tag token: @business
Do not rewrite grow your business here.
"""
        rewritten = rewrite_text_for_context(Path("note.md"), text, "business", "studio")

        self.assertIn("entity: studio", rewritten)
        self.assertIn("context_type: business", rewritten)
        self.assertIn("  - studio", rewritten)
        self.assertIn("[[studio/foo]]", rewritten)
        self.assertIn("![[studio/bar.png]]", rewritten)
        self.assertIn("[[studio/studio|Business]]", rewritten)
        self.assertIn("studio/_obsidian/tasks/x.md", rewritten)
        self.assertIn("@studio", rewritten)
        self.assertIn("grow your business", rewritten)

    def test_json_rewrites_paths_and_exact_values_but_not_context_type(self) -> None:
        text = json.dumps(
            {
                "name": "business",
                "context_type": "business",
                "folder": "business/_obsidian/tasks",
                "control_note": "business/business.md",
                "nested": ["@business", "[[business/foo]]"],
            },
            indent=2,
        )
        rewritten = rewrite_text_for_context(Path("data.json"), text, "business", "studio")
        data = json.loads(rewritten)

        self.assertEqual(data["name"], "studio")
        self.assertEqual(data["context_type"], "business")
        self.assertEqual(data["folder"], "studio/_obsidian/tasks")
        self.assertEqual(data["control_note"], "studio/studio.md")
        self.assertEqual(data["nested"], ["@studio", "[[studio/foo]]"])

    def test_rename_moves_folder_and_rewrites_vault_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "business").mkdir()
            (root / "business" / "business.md").write_text(
                "---\nentity: business\ncontext_type: business\n---\n[[business/foo]]\n",
                encoding="utf-8",
            )
            (root / ".obsidian/plugins/tasknotes").mkdir(parents=True)
            (root / ".obsidian/plugins/tasknotes/data.json").write_text(
                json.dumps({"taskCreationDefaults": {"defaultContexts": "business"}}, indent=2) + "\n",
                encoding="utf-8",
            )
            (root / "_system").mkdir()
            (root / "_system" / "README.md").write_text(
                "Path business/_obsidian/tasks/x.md\nSentence grow your business.\n",
                encoding="utf-8",
            )

            result = rename_teamspace_folder(root, "business", "studio")

            self.assertTrue(result.moved)
            self.assertFalse((root / "business").exists())
            self.assertTrue((root / "studio").is_dir())
            context_note = (root / "studio" / "studio.md").read_text(encoding="utf-8")
            self.assertFalse((root / "studio" / "business.md").exists())
            self.assertIn("entity: studio", context_note)
            self.assertIn("context_type: business", context_note)
            self.assertIn("[[studio/foo]]", context_note)
            tasknotes = json.loads((root / ".obsidian/plugins/tasknotes/data.json").read_text(encoding="utf-8"))
            self.assertEqual(tasknotes["taskCreationDefaults"]["defaultContexts"], "studio")
            context = (root / "_system" / "README.md").read_text(encoding="utf-8")
            self.assertIn("studio/_obsidian/tasks/x.md", context)
            self.assertIn("grow your business", context)


if __name__ == "__main__":
    unittest.main()
