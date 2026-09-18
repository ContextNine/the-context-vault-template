#!/usr/bin/env python3
"""Map a sanitized public agent package into a Context Vault."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


class SkillSystemInstallError(RuntimeError):
    pass


def existing_source(home: Path) -> Path | None:
    manifest = home / ".agents/state/installed.json"
    if not manifest.is_file():
        return None
    try:
        value = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillSystemInstallError(f"invalid installed skill-system state: {exc}") from exc
    raw = value.get("source_root")
    if raw is None:
        launcher = home / ".local/bin/fleet"
        if launcher.is_file() and "# fleet.managed" in launcher.read_text(encoding="utf-8"):
            match = re.search(r'--root ("(?:[^"\\]|\\.)*"|[^\s]+)', launcher.read_text(encoding="utf-8"))
            if match:
                captured = match.group(1)
                root = Path(json.loads(captured) if captured.startswith('"') else captured).resolve()
                candidate = root / "_system/agents" if (root / "_system/agents/edit/settings").is_dir() else root
                raw = str(candidate)
    if not isinstance(raw, str) or not Path(raw).is_absolute():
        raise SkillSystemInstallError(
            f"skill-system source is unknown; select and adopt the existing source before connecting this Vault: {manifest}"
        )
    source = Path(raw).resolve()
    if not (source / "edit/settings/fleet/machines.json").is_file() or not (source / "internal/src/fleet.py").is_file():
        raise SkillSystemInstallError(f"installed skill-system source is missing or incomplete: {source}")
    return source


def connect_vault(source: Path, home: Path, vault_root: Path) -> Path:
    source = source.resolve()
    home = home.resolve()
    vault_root = vault_root.resolve()
    if existing_source(home) != source:
        raise SkillSystemInstallError(f"{source} is not the installed skill-system source")
    machine_id_path = home / ".agents/state/machine-id"
    if not machine_id_path.is_file():
        raise SkillSystemInstallError(f"installed machine identity is missing: {machine_id_path}")
    machine_id = machine_id_path.read_text(encoding="utf-8").strip()
    paths = [source / "edit/settings/fleet/machines.json", home / ".agents/settings/fleet/machines.json"]
    updates: list[tuple[Path, dict[str, object]]] = []
    for path in paths:
        try:
            registry = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SkillSystemInstallError(f"invalid machine registry {path}: {exc}") from exc
        selected = next((item for item in registry.get("machines", []) if item.get("id") == machine_id), None)
        if selected is None or selected.get("role") != "primary" or selected.get("platform") != "macos":
            raise SkillSystemInstallError(f"only the installed primary Mac can connect a local Vault: {path}")
        current = selected.get("roots", {}).get("vault")
        if current not in (None, str(vault_root)):
            raise SkillSystemInstallError(f"machine already connects to a different Vault: {current}")
        selected["roots"]["vault"] = str(vault_root)
        selected["vault"] = {"enabled": True, "checkout_mode": "primary-external-git", "required": True}
        registry["vault_git"]["owner_machine_id"] = machine_id
        registry["vault_git"]["refresh_owner_machine_id"] = machine_id
        updates.append((path, registry))
    for path, registry in updates:
        path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    manifest = json.loads((home / ".agents/state/installed.json").read_text(encoding="utf-8"))
    owned = set(manifest.get("owned_paths", []))
    command = [
        sys.executable, str(source / "internal/src/fleet.py"), "install",
        "--source", str(source), "--home", str(home), "--apply", "--discovery-aliases",
    ]
    if str(home / ".agents/instructions/AGENTS.md") in owned:
        command.append("--global-instructions")
    if str(home / ".claude/CLAUDE.md") in owned:
        command.append("--claude-alias")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SkillSystemInstallError(result.stderr.strip() or "updating installed skill instructions failed")
    record_source(source, vault_root)
    return source


def record_source(source: Path, vault_root: Path) -> None:
    state = vault_root / "_system/local/state/skill-system-install.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        json.dumps(
            {"schema_version": 1, "installed": True, "source_root": str(source), "placement": "standalone"},
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


def copy_standalone(source_repo: Path, destination: Path) -> Path:
    source = source_repo.resolve()
    target = destination.expanduser().resolve()
    if not (source / "edit/settings").is_dir() or not (source / "internal/src/fleet.py").is_file() or not (source / "install.sh").is_file():
        raise SkillSystemInstallError(f"public skill-system source is incomplete: {source}")
    if target.exists() or target.is_symlink():
        raise SkillSystemInstallError(f"refusing to overwrite skill-system source: {target}")
    if source == target or source in target.parents or target in source.parents:
        raise SkillSystemInstallError("standalone source destination must be separate from the reviewed package")
    if any(path.is_symlink() for path in source.rglob("*")):
        raise SkillSystemInstallError(f"public skill-system source contains symlinks: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git"))
    subprocess.run(["git", "init", "-b", "master", str(target)], check=True)
    return target


def install_tree(
    source_repo: Path,
    vault_root: Path,
    *,
    source_url: str,
    release_version: str,
    commit: str,
) -> Path:
    source = source_repo.resolve()
    target = vault_root.resolve() / "_system/agents"
    if not (source / "edit/settings").is_dir() or not (source / "internal/src").is_dir():
        raise SkillSystemInstallError(f"public skill system source is incomplete: {source}")
    if target.exists() or target.is_symlink():
        raise SkillSystemInstallError(f"refusing to overwrite an existing agents tree: {target}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise SkillSystemInstallError(f"public skill system contains a symlink: {path}")
    target.mkdir(parents=True)
    shutil.copytree(source / "edit", target / "edit")
    shutil.copytree(source / "internal", target / "internal")
    readme = source / "README.md"
    if readme.is_file():
        shutil.copy2(readme, target / "README.md")
    state = vault_root / "_system/local/state/skill-system-install.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "installed": True,
                "source_root": str(target),
                "placement": "vault",
                "source_url": source_url,
                "release_version": release_version,
                "commit": commit,
                "selected_integrations": ["global-public-skills"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--existing-source", action="store_true")
    parser.add_argument("--connect-existing", action="store_true")
    parser.add_argument("--record-source", action="store_true")
    parser.add_argument("--copy-standalone", action="store_true")
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--home", type=Path)
    parser.add_argument("--source-repo", type=Path)
    parser.add_argument("--vault-root", type=Path)
    parser.add_argument("--source-url")
    parser.add_argument("--release-version")
    parser.add_argument("--commit")
    args = parser.parse_args()
    if args.existing_source:
        if args.home is None:
            parser.error("--existing-source needs --home")
        print(existing_source(args.home) or "")
        return 0
    if args.connect_existing:
        if args.home is None or args.vault_root is None:
            parser.error("--connect-existing needs --home and --vault-root")
        source = existing_source(args.home)
        if source is None:
            parser.error("no existing skill system is installed")
        print(connect_vault(source, args.home, args.vault_root))
        return 0
    if args.record_source:
        if args.home is None or args.vault_root is None:
            parser.error("--record-source needs --home and --vault-root")
        source = existing_source(args.home)
        if source is None:
            parser.error("no skill system was installed")
        record_source(source, args.vault_root)
        print(source)
        return 0
    if args.copy_standalone:
        if args.source_repo is None or args.destination is None:
            parser.error("--copy-standalone needs --source-repo and --destination")
        print(copy_standalone(args.source_repo, args.destination))
        return 0
    if not all((args.source_repo, args.vault_root, args.source_url, args.release_version, args.commit)):
        parser.error("a new install needs source, Vault, and release identity")
    print(
        install_tree(
            args.source_repo,
            args.vault_root,
            source_url=args.source_url,
            release_version=args.release_version,
            commit=args.commit,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
