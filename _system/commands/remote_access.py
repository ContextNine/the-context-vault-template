#!/usr/bin/env python3
"""Inspect registered Vault worktree health on local Macs and remote clients."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from vault_layout import VAULT_ROOT


ROOT = VAULT_ROOT
REGISTRY = ROOT / "_system/agents/edit/settings/fleet/machines.json"
HELPER = (
    ROOT
    / "_system/agents/edit/skills/_infrastructure/infra-i-onboard-machine/"
    "scripts/remote_vault_access.py"
)


def load_helper() -> Any:
    specification = importlib.util.spec_from_file_location("remote_vault_access", HELPER)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load remote Vault helper: {HELPER}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


ACCESS = load_helper()


def current_machine_id() -> str:
    identity = Path.home() / ".config/vault/machine-id"
    if identity.is_file():
        value = identity.read_text(encoding="utf-8").strip()
        if value:
            return value
    result = subprocess.run(
        ["git", "-C", str(ROOT), "config", "--get", "vault.machine-id"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.stdout.strip():
        return result.stdout.strip()
    raise ACCESS.AccessError("machine identity is unresolved")


def topology() -> tuple[dict[str, Any], dict[str, Any]]:
    registry, machines = ACCESS.load_registry(REGISTRY)
    machine_id = current_machine_id()
    machine = machines.get(machine_id)
    if not machine or not machine.get("enabled") or not machine.get("vault", {}).get("enabled"):
        raise ACCESS.AccessError(f"machine is not an enabled Vault participant: {machine_id}")
    return registry, machine


def status() -> dict[str, Any]:
    registry, machine = topology()
    mode = machine["vault"]["checkout_mode"]
    if mode == "remote-sshfs":
        return ACCESS.client_status(ACCESS.client_config())
    health = ACCESS.icloud_health(ROOT)
    return {
        "ok": bool(health.get("access_ready")),
        "machine_id": machine["id"],
        "mode": mode,
        "mount": {
            "mounted": True,
            "healthy": ROOT.is_dir() and (ROOT / "AGENTS.md").is_file(),
            "read_write": os.access(ROOT, os.R_OK | os.W_OK | os.X_OK),
            "target": str(ROOT),
            "source": "local-icloud",
        },
        "host": {
            "machine_id": machine["id"],
            "vault_root": str(ROOT),
            "icloud": health,
        },
        "git_owner": registry["vault_git"].get("owner_machine_id") == machine["id"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("mount")
    sub.add_parser("unmount")
    status_parser = sub.add_parser("status")
    status_parser.add_argument("--json", action="store_true")
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if args.action in {"mount", "unmount"}:
        result = {
            "ok": True,
            "detail": "local iCloud Vault is not mounted through SSHFS",
            "mount": status()["mount"],
        }
    else:
        result = status()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ACCESS.AccessError, OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        print(f"Vault access failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
