#!/usr/bin/env python3
"""Tests for attachment cleanup state paths."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import attachments  # noqa: E402


class AttachmentCleanupTests(unittest.TestCase):
    def test_generated_output_stays_in_ignored_vault_state(self) -> None:
        self.assertEqual(
            attachments.ARTIFACT_ROOT,
            attachments.ROOT / "_system/local/state/attachments",
        )
        self.assertNotIn("Downloads", attachments.ARTIFACT_ROOT.parts)

    def test_quarantine_is_not_an_attachment_resolution_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            attachment = root / "_system/_obsidian/attachments/kept.png"
            quarantined = root / "_system/local/state/attachments/quarantine/orphan.png"
            attachment.parent.mkdir(parents=True)
            quarantined.parent.mkdir(parents=True)
            attachment.write_bytes(b"kept")
            quarantined.write_bytes(b"orphan")

            with patch.object(attachments, "ROOT", root), patch.object(
                attachments,
                "top_roots",
                return_value={"_system"},
            ):
                index = attachments.build_basename_index()

            self.assertEqual(index["kept.png"], [attachment.resolve()])
            self.assertNotIn("orphan.png", index)


if __name__ == "__main__":
    unittest.main()
