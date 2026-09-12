#!/usr/bin/env python3
"""Install or verify one exact public Context Vault release."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RELEASE_PATH = ROOT / "_system/bootstrap/release.json"


class ComponentError(RuntimeError):
    pass


def release() -> dict[str, Any]:
    value = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    if not isinstance(value.get("version"), str) or not isinstance(value.get("tag"), str):
        raise ComponentError("release metadata is invalid")
    return value


def installed_root() -> Path | None:
    override = os.environ.get("CTX9_VAULT_ROOT")
    if override:
        return Path(override).expanduser()
    command = shutil.which("vault")
    if not command:
        return None
    result = subprocess.run(
        [command, "root"],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).expanduser()


def installed_version(root: Path | None) -> str | None:
    if root is None:
        return None
    path = root / "_system/bootstrap/release.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    version = value.get("version") if isinstance(value, dict) else None
    return version if isinstance(version, str) else None


def status(expected: str, *, changed: bool = False) -> dict[str, Any]:
    root = installed_root()
    actual = installed_version(root)
    return {
        "component": "vault",
        "version": expected,
        "installed_version": actual,
        "root": str(root) if root else None,
        "ready": actual == expected,
        "changed": changed,
    }


def install(metadata: dict[str, Any]) -> dict[str, Any]:
    expected = metadata["version"]
    current = status(expected)
    if current["ready"]:
        return current
    if current["installed_version"] is not None:
        raise ComponentError(
            "an existing Vault needs its repository-preserving `vault upgrade` workflow"
        )
    environment = dict(os.environ)
    environment["CTX9_VAULT_RELEASE_TAG"] = metadata["tag"]
    result = subprocess.run(
        ["/bin/bash", str(ROOT / "install.sh"), "--skip-skill-system", "--non-interactive"],
        check=False,
        stdout=sys.stderr,
        stderr=sys.stderr,
        env=environment,
    )
    if result.returncode:
        raise ComponentError("Vault bootstrap installer failed")
    result_status = status(expected, changed=True)
    if not result_status["ready"]:
        raise ComponentError("installed Vault did not report the expected release")
    return result_status


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("--verify", action="store_true")
    command.add_argument("--json", action="store_true")
    return command


def main() -> int:
    arguments = parser().parse_args()
    try:
        metadata = release()
        result = status(metadata["version"]) if arguments.verify else install(metadata)
        if arguments.json:
            print(json.dumps(result, sort_keys=True))
        else:
            print(
                f"vault {result['installed_version'] or 'not installed'}: "
                f"{'ready' if result['ready'] else 'not ready'}"
            )
        return 0 if result["ready"] else 1
    except (ComponentError, OSError, subprocess.SubprocessError) as error:
        print(f"vault component error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
