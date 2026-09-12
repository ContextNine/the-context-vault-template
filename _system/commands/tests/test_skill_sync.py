#!/usr/bin/env python3
"""Focused tests for flat skill discovery and external materialization."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


AGENT_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "agents/_package/src"
sys.path.insert(0, str(AGENT_SCRIPTS_DIR))

import sync_skills  # noqa: E402
import working_repo_skills  # noqa: E402


class SkillSyncTests(unittest.TestCase):
    def fixture(self, temporary: str) -> tuple[Path, Path, Path]:
        base = Path(temporary)
        root = base / "vault"
        home = base / "home"
        repo = home / "Code/example-repo"
        for relative in (
            "_system/agents/skills/_code",
            "_system/agents/skills/github",
            "_system/agents/skills/catalog",
            "_system/agents/skills/overlays",
            "_system/agents/skills/snapshots",
            "_system/agents/_package/instance/skills",
        ):
            (root / relative).mkdir(parents=True)
        repo.mkdir(parents=True)
        self.write_config(root, [])
        return root, home, repo

    def write_config(self, root: Path, repos: list[dict[str, object]], gh: dict[str, object] | None = None) -> None:
        path = root / "_system/agents/_package/instance/skills/skill-sources.json"
        path.write_text(json.dumps({"schema_version": 4, "gh_skills": gh or {}, "repos": repos}) + "\n", encoding="utf-8")

    def write_skill(self, path: Path, name: str, *, implicit: bool | None = None, body: str = "") -> Path:
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test.\n---\n\n# Code · Test\n\n{body}", encoding="utf-8")
        if implicit is not None:
            (path / "agents").mkdir()
            (path / "agents/openai.yaml").write_text(
                f"policy:\n  allow_implicit_invocation: {'true' if implicit else 'false'}\n",
                encoding="utf-8",
            )
        return path

    def write_gh_skill(self, root: Path, name: str) -> Path:
        path = root / f"_system/agents/skills/github/example-pack/skills/{name}"
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test.\nmetadata:\n  github-repo: https://github.com/example/pack\n  github-path: skills/{name}\n  github-ref: main\n  github-tree-sha: abc\n---\n\n# Test\n",
            encoding="utf-8",
        )
        return path

    def test_flat_vault_groups_require_i_marker_to_match_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, _, _ = self.fixture(temporary)
            self.write_skill(root / "_system/agents/skills/_code/code-i-example", "code-i-example", implicit=True)
            skills = sync_skills.scan_vault_sources(root / "_system/agents/skills")
            self.assertEqual([(skill.name, skill.mode) for skill in skills], [("code-i-example", "auto")])
            metadata = root / "_system/agents/skills/_code/code-i-example/agents/openai.yaml"
            metadata.write_text("policy:\n  allow_implicit_invocation: false\n", encoding="utf-8")
            with self.assertRaisesRegex(sync_skills.SyncError, "marker and invocation policy disagree"):
                sync_skills.scan_vault_sources(root / "_system/agents/skills")

    def test_gh_repository_discovery_preserves_installed_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, home, _ = self.fixture(temporary)
            source = self.write_gh_skill(root, "third-party")
            before = (source / "SKILL.md").read_text(encoding="utf-8")
            plan, skills = sync_skills.discover_skills(root, home=home)
            self.assertEqual(plan.actions[0].kind, "overlay")
            self.assertEqual(skills[0].name, "third-party")
            self.assertEqual((source / "SKILL.md").read_text(encoding="utf-8"), before)

    def test_unprefixed_repo_skill_is_a_direct_link_when_policy_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, home, repo = self.fixture(temporary)
            source = self.write_skill(repo / ".agents/skills/example-repo-do-work", "example-repo-do-work", implicit=False, body="first\n")
            self.write_config(root, [{"path": "~/Code/example-repo", "all_skills": True}])
            plan, skills = sync_skills.discover_skills(root, home=home, require_repo_sources=True)
            selected = next(skill for skill in skills if skill.name == "example-repo-do-work")
            self.assertEqual(selected.materialization, "direct")
            self.assertEqual(selected.path.resolve(), source.resolve())
            self.assertEqual(plan.actions, ())
            (source / "SKILL.md").write_text((source / "SKILL.md").read_text().replace("first", "second"), encoding="utf-8")
            self.assertIn("second", selected.path.joinpath("SKILL.md").read_text())

    def test_policy_only_repo_change_builds_linked_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, home, repo = self.fixture(temporary)
            source = self.write_skill(repo / ".agents/skills/example-repo-do-work", "example-repo-do-work", implicit=True)
            self.write_config(root, [{"path": "~/Code/example-repo", "all_skills": True}])
            plan = working_repo_skills.plan(root, home=home, require_sources=True)
            self.assertEqual(plan.skills[0].materialization, "overlay")
            working_repo_skills.apply(plan, root)
            overlay = plan.skills[0].path
            self.assertTrue((overlay / "SKILL.md").is_symlink())
            self.assertEqual((overlay / "SKILL.md").resolve(), (source / "SKILL.md").resolve())
            self.assertIn("allow_implicit_invocation: false", (overlay / "agents/openai.yaml").read_text())

    def test_prefix_builds_snapshot_and_rewrites_named_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, home, repo = self.fixture(temporary)
            self.write_skill(repo / ".agents/skills/example-repo-one", "example-repo-one", implicit=False, body="Use $example-repo-two.\n")
            self.write_skill(repo / ".agents/skills/example-repo-two", "example-repo-two", implicit=False)
            self.write_config(root, [{"path": "~/Code/example-repo", "all_skills": True, "prefix": "local"}])
            plan = working_repo_skills.plan(root, home=home, require_sources=True)
            self.assertTrue(all(skill.materialization == "snapshot" for skill in plan.skills))
            working_repo_skills.apply(plan, root)
            snapshot = root / "_system/agents/skills/snapshots/example-repo/local-example-repo-one/SKILL.md"
            text = snapshot.read_text(encoding="utf-8")
            self.assertIn("name: local-example-repo-one", text)
            self.assertIn("$local-example-repo-two", text)

    def test_config_rejects_unsafe_paths_unknown_fields_and_selection_conflicts(self) -> None:
        bad = [
            {"path": "/tmp/repo", "all_skills": True},
            {"path": "~/Code/repo", "all_skills": True, "skills": [{"source": "skills/a"}]},
            {"path": "~/Code/repo", "all_skills": True, "mode": "manual"},
        ]
        for repo in bad:
            with self.subTest(repo=repo), tempfile.TemporaryDirectory() as temporary:
                root, home, _ = self.fixture(temporary)
                self.write_config(root, [repo])
                with self.assertRaises(working_repo_skills.ProjectionError):
                    working_repo_skills.plan(root, home=home)

    def test_catalog_remains_symlink_only_and_second_apply_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, home, _ = self.fixture(temporary)
            source = self.write_skill(root / "_system/agents/skills/_code/code-example", "code-example", implicit=False)
            sync_skills.sync(root, home, True, manage_home_discovery=False, manage_agent_configuration=False)
            link = root / "_system/agents/skills/catalog/code-example"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), source.resolve())
            plan, skills = sync_skills.discover_skills(root, home=home)
            self.assertEqual(plan.actions, ())
            self.assertEqual(sync_skills.plan_catalog(link.parent, skills), [])
            self.assertFalse(any(path.is_dir() and not path.is_symlink() for path in link.parent.iterdir()))


if __name__ == "__main__":
    unittest.main()
