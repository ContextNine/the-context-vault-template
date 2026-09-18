#!/usr/bin/env python3
"""Move saved Vault metadata and managed dashboard links to teamspace naming."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bootstrap"))
from bootstrap_vault import entity_dashboard_base

# Old names are accepted only by this one-time data migration, never by the CLI.
FIELD_RENAMES = {
    "context_registered": "teamspace_registered",
    "source_context_folders": "source_teamspace_folders",
}
PATH_RENAMES = {
    "context-dashboard.base": "teamspace-dashboard.base",
    "context-template.md": "teamspace-template.md",
    "Context Folders": "Teamspace Folders",
}


def rewrite(text: str) -> str:
    if text.startswith("---\n") and "\n---" in text[4:]:
        end = text.index("\n---", 4)
        frontmatter = text[:end]
        for old, new in FIELD_RENAMES.items():
            if re.search(rf"(?m)^{old}:", frontmatter):
                if re.search(rf"(?m)^{new}:", frontmatter):
                    raise ValueError(f"Both registration fields exist: {old}, {new}")
                frontmatter = re.sub(rf"(?m)^{old}:", f"{new}:", frontmatter)
        text = frontmatter + text[end:]
    for old, new in PATH_RENAMES.items():
        # Rewrite link targets, including extensionless Obsidian links.
        stem = old.removesuffix(".md").removesuffix(".base")
        new_stem = new.removesuffix(".md").removesuffix(".base")
        text = re.sub(rf"(?<=\[\[){re.escape(stem)}(?=[.#|\]])", new_stem, text)
        text = re.sub(rf"(?<=/){re.escape(stem)}(?=[.#|\]])", new_stem, text)
    return text.replace('|Context Folders]]', '|Teamspace Folders]]').replace(
        'name: "Context Folder Files"', 'name: "Teamspace Folder Files"'
    )


def stable_base(text: str) -> str:
    return re.sub(r"(?m)^generated_at:.*\n", "", text)


def migrate(root: Path, apply: bool) -> dict[str, object]:
    folders = [
        child for child in sorted(root.iterdir())
        if child.is_dir() and not child.is_symlink()
        and not child.name.startswith((".", "_"))
        and (child / f"{child.name}.md").is_file()
    ]
    candidates = {root / "Dashboard.md"}
    for folder in folders:
        candidates.add(folder / f"{folder.name}.md")
        for directory in (folder / "_obsidian/bases", folder / "_obsidian/templates"):
            if directory.is_dir():
                candidates.update(p for p in directory.rglob("*") if p.suffix in {".md", ".base"})
    periodic = root / "_system/_obsidian/periodic"
    if periodic.is_dir():
        candidates.update(periodic.rglob("*.md"))

    writes: dict[Path, str] = {}
    removals: list[Path] = []
    errors: list[str] = []
    for path in sorted(candidates):
        if not path.is_file() or path.is_symlink():
            continue
        original = path.read_text(encoding="utf-8")
        try:
            rendered = rewrite(original)
        except ValueError as error:
            errors.append(f"{path.relative_to(root)}: {error}")
            continue
        if rendered != original:
            writes[path] = rendered

    for folder in folders:
        old = folder / "_obsidian/bases/context-dashboard.base"
        new = old.with_name("teamspace-dashboard.base")
        if old.is_symlink() or new.is_symlink():
            errors.append(f"Dashboard path is a symlink: {folder.name}")
            continue
        if not old.is_file():
            continue
        rendered = rewrite(old.read_text(encoding="utf-8"))
        if new.exists():
            existing = new.read_text(encoding="utf-8")
            expected = entity_dashboard_base(folder.name)
            if stable_base(existing) not in {stable_base(rendered), stable_base(expected)}:
                errors.append(f"Both dashboards contain different custom content: {folder.name}")
                continue
        writes.pop(old, None)
        writes[new] = rendered
        removals.append(old)

    config = root / "_system/bootstrap/init-vault-config.json"
    if config.is_file() and not config.is_symlink():
        data = json.loads(config.read_text(encoding="utf-8"))
        if "context_folders" in data:
            if "teamspace_folders" in data:
                errors.append("Setup configuration contains both folder keys")
            else:
                data["teamspace_folders"] = data.pop("context_folders")
                writes[config] = json.dumps(data, indent=2) + "\n"

    report: dict[str, object] = {
        "migration": "002-teamspace-terminology",
        "mode": "apply" if apply else "dry-run",
        "changed": [str(p.relative_to(root)) for p in sorted(writes)],
        "removed": [str(p.relative_to(root)) for p in removals],
        "errors": errors,
    }
    if apply and not errors:
        for path, text in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        for path in removals:
            path.unlink()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--report", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report = migrate(Path(args.root).expanduser().resolve(), args.apply)
    destination = Path(args.report).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
