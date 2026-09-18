#!/usr/bin/env python3
"""Print live, low-context vault routing inventory for agents."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from script_utils import teamspace_folder_note_path, resolve_vault_root
from vault_layout import VAULT_PERIODIC_DIR


DEFAULT_TASK_STATUSES = ["backlog", "up-next", "to-be-resumed", "ongoing", "in-progress", "done", "archived"]
ROUTING_TASK_STATUSES = ["in-progress", "ongoing", "to-be-resumed", "up-next"]
PERIODS = ("daily", "weekly", "monthly", "quarterly", "yearly")
CONTENT_FEATURE_DIRECTORIES = {
    "blog": ("items/blog-posts", "publications/blogs"),
    "social-content": ("items/social-posts", "items/youtube-videos", "publications/youtube", "ideas", "archive"),
    "newsletters": ("items/newsletter-issues", "publications/newsletters"),
}


def clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in text[4:end].splitlines():
        if raw_line.startswith("  - ") and current_key:
            result.setdefault(current_key, []).append(clean_scalar(raw_line[4:]))
            continue
        current_key = None
        if ":" not in raw_line or raw_line.startswith(" "):
            continue
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "":
            result[key] = []
            current_key = key
        else:
            result[key] = clean_scalar(value)
    return result


def truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"true", "yes", "1"}


def active_periods(day: dt.date) -> dict[str, str]:
    iso = day.isocalendar()
    quarter = ((day.month - 1) // 3) + 1
    return {
        "daily": day.isoformat(),
        "weekly": f"{iso.year}-W{iso.week:02d}",
        "monthly": f"{day.year}-{day.month:02d}",
        "quarterly": f"{day.year}-Q{quarter}",
        "yearly": str(day.year),
    }


def note_info(root: Path, teamspace: str, kind: str, path: Path) -> dict[str, Any]:
    metadata = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    return {
        "teamspace": teamspace,
        "title": str(metadata.get("title") or path.stem),
        "status": str(metadata.get("status") or ""),
        "epic": str(metadata.get("epic") or ""),
        "path": str(path.relative_to(root)),
        "kind": kind,
    }


def task_statuses(root: Path) -> list[str]:
    config = root / ".obsidian/plugins/tasknotes/data.json"
    if not config.exists():
        return DEFAULT_TASK_STATUSES
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return DEFAULT_TASK_STATUSES
    statuses = []
    for item in data.get("customStatuses", []):
        value = item.get("value") or item.get("id")
        if value:
            statuses.append(str(value))
    return statuses or DEFAULT_TASK_STATUSES


def teamspace_periodic_paths(root: Path, name: str, periods: dict[str, str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for period, period_id in periods.items():
        path = Path(name) / "_obsidian/periodic" / period / f"{period_id}.md"
        result[period] = {"path": path.as_posix(), "exists": (root / path).exists()}
    return result


def discover_teamspaces(root: Path, periods: dict[str, str]) -> list[dict[str, Any]]:
    teamspaces = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name.startswith("_"):
            continue
        note = teamspace_folder_note_path(child)
        if not note.exists():
            continue
        metadata = frontmatter(note.read_text(encoding="utf-8", errors="replace"))
        if str(metadata.get("teamspace_registered", "true")).strip().lower() in {"false", "no", "0"}:
            continue
        content_root = child / "_obsidian/content"
        features = [
            feature
            for feature, directories in CONTENT_FEATURE_DIRECTORIES.items()
            if any((content_root / directory).is_dir() for directory in directories)
        ]
        teamspaces.append(
            {
                "name": child.name,
                "status": str(metadata.get("status") or "none"),
                "features": features,
                "periodic_notes_enabled": truthy(metadata.get("periodic_notes_enabled", "true")),
                "content_schedules_enabled": truthy(metadata.get("content_schedules_enabled")),
                "default_capture": truthy(metadata.get("default_capture")),
                "note_path": note.relative_to(root).as_posix(),
                "periodic_notes": teamspace_periodic_paths(root, child.name, periods),
            }
        )
    return teamspaces


def default_capture_teamspace(teamspaces: list[dict[str, Any]]) -> str:
    for teamspace in teamspaces:
        if teamspace["default_capture"]:
            return str(teamspace["name"])
    for teamspace in teamspaces:
        if teamspace["status"] == "active":
            return str(teamspace["name"])
    return str(teamspaces[0]["name"]) if teamspaces else ""


def vault_periodic_paths(root: Path, periods: dict[str, str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for period, period_id in periods.items():
        path = VAULT_PERIODIC_DIR / period / f"{period_id}.md"
        result[period] = {"path": path.as_posix(), "exists": (root / path).exists()}
    return result


def current_content_schedules(root: Path, teamspaces: list[dict[str, Any]], day: dt.date) -> list[dict[str, str]]:
    schedules: list[dict[str, str]] = []
    for teamspace in teamspaces:
        if not teamspace["content_schedules_enabled"]:
            continue
        folder = root / str(teamspace["name"]) / "_obsidian/content-schedules"
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            metadata = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            if metadata.get("type") != "content-schedule":
                continue
            start = str(metadata.get("schedule_start") or "")
            end = str(metadata.get("schedule_end") or "")
            if start and end and start <= day.isoformat() <= end:
                schedules.append(
                    {
                        "teamspace": str(teamspace["name"]),
                        "path": path.relative_to(root).as_posix(),
                        "schedule_start": start,
                        "schedule_end": end,
                    }
                )
    return schedules


def collect_notes(root: Path, teamspaces: list[dict[str, Any]], kind: str) -> dict[str, list[dict[str, Any]]]:
    folder_name = "projects" if kind == "project" else "epics"
    grouped: dict[str, list[dict[str, Any]]] = {}
    for teamspace in teamspaces:
        teamspace_name = str(teamspace["name"])
        folder = root / teamspace_name / "_obsidian" / folder_name
        grouped[teamspace_name] = []
        if folder.exists():
            grouped[teamspace_name] = [
                note_info(root, teamspace_name, kind, path)
                for path in sorted(folder.glob("*.md"))
            ]
    return grouped


def optional_date(value: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def task_sort_key(task: dict[str, Any]) -> tuple[int, dt.date, dt.date, dt.date, str]:
    priority = {"high": 0, "normal": 1, "low": 2, "none": 3, "": 4}
    far_future = dt.date.max
    return (
        priority.get(str(task.get("priority", "")).lower(), 4),
        optional_date(task.get("due")) or far_future,
        optional_date(task.get("scheduled")) or far_future,
        optional_date(task.get("dateCreated")) or far_future,
        str(task.get("title") or "").lower(),
    )


def collect_tasks(root: Path, teamspaces: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, int]]]:
    grouped = {status: [] for status in ROUTING_TASK_STATUSES}
    counts: dict[str, dict[str, int]] = {}
    for teamspace in teamspaces:
        name = str(teamspace["name"])
        counts[name] = {}
        folder = root / name / "_obsidian/tasks"
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            metadata = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            status = str(metadata.get("status") or "")
            if not status:
                continue
            counts[name][status] = counts[name].get(status, 0) + 1
            if status not in grouped:
                continue
            grouped[status].append(
                {
                    "teamspace": name,
                    "title": str(metadata.get("title") or path.stem),
                    "status": status,
                    "priority": str(metadata.get("priority") or ""),
                    "scheduled": str(metadata.get("scheduled") or ""),
                    "due": str(metadata.get("due") or ""),
                    "dateCreated": str(metadata.get("dateCreated") or ""),
                    "path": path.relative_to(root).as_posix(),
                }
            )
    for tasks in grouped.values():
        tasks.sort(key=task_sort_key)
    return grouped, counts


def build_inventory(root: Path, active_only: bool, day: dt.date | None = None) -> dict[str, Any]:
    day = day or dt.date.today()
    periods = active_periods(day)
    all_teamspaces = discover_teamspaces(root, periods)
    teamspaces = [item for item in all_teamspaces if not active_only or item["status"] == "active"]
    tasks, task_counts = collect_tasks(root, teamspaces)
    return {
        "date": day.isoformat(),
        "active_periods": periods,
        "default_capture_teamspace": default_capture_teamspace(all_teamspaces),
        "task_statuses": task_statuses(root),
        "teamspaces": teamspaces,
        "vault_periodic_notes": vault_periodic_paths(root, periods),
        "content_schedules": current_content_schedules(root, teamspaces, day),
        "task_counts": task_counts,
        "tasks": tasks,
        "backlog_counts": {name: counts.get("backlog", 0) for name, counts in task_counts.items()},
        "epics": collect_notes(root, teamspaces, "epic"),
        "projects": collect_notes(root, teamspaces, "project"),
    }


def print_grouped(title: str, grouped: dict[str, list[dict[str, Any]]]) -> None:
    print(f"\n{title}:")
    for teamspace, items in grouped.items():
        print(f"  {teamspace}:")
        if not items:
            print("    - none")
            continue
        for item in items:
            status = f" [{item['status']}]" if item["status"] else ""
            epic = f" epic={item['epic']}" if item["epic"] else ""
            print(f"    - {item['title']}{status}{epic} -> {item['path']}")


def print_path_group(title: str, paths: dict[str, dict[str, Any]]) -> None:
    print(f"\n{title}:")
    for period, item in paths.items():
        missing = " (missing)" if not item["exists"] else ""
        print(f"  - {period}: {item['path']}{missing}")


def print_inventory(inventory: dict[str, Any]) -> None:
    print("Vault inventory")
    periods = inventory["active_periods"]
    print(f"Date: {inventory['date']}")
    print("Periods: " + ", ".join(f"{period}={periods[period]}" for period in PERIODS))
    print(f"Default capture: {inventory['default_capture_teamspace'] or 'none'}")
    print(f"Task statuses: {', '.join(inventory['task_statuses'])}")
    print("\nTeamspaces:")
    for teamspace in inventory["teamspaces"]:
        flags = [teamspace["status"], *teamspace["features"]]
        if not teamspace["periodic_notes_enabled"]:
            flags.append("periodic notes disabled")
        if teamspace["content_schedules_enabled"]:
            flags.append("content schedules")
        if teamspace["default_capture"]:
            flags.append("default capture")
        print(f"  - {teamspace['name']} [{', '.join(flags)}] -> {teamspace['note_path']}")
        if teamspace["status"] == "active" and teamspace["periodic_notes_enabled"]:
            for period, item in teamspace["periodic_notes"].items():
                missing = " (missing)" if not item["exists"] else ""
                print(f"      {period}: {item['path']}{missing}")
    print_path_group("Vault periodic rollups", inventory["vault_periodic_notes"])
    print("\nContent schedules:")
    if not inventory["content_schedules"]:
        print("  - none")
    for schedule in inventory["content_schedules"]:
        print(f"  - {schedule['teamspace']}: {schedule['path']} ({schedule['schedule_start']} to {schedule['schedule_end']})")
    print("\nTask counts:")
    for teamspace, counts in inventory["task_counts"].items():
        rendered = ", ".join(f"{status}={count}" for status, count in sorted(counts.items())) or "none"
        print(f"  - {teamspace}: {rendered}")
    for status in ROUTING_TASK_STATUSES:
        print(f"\nTasks {status}:")
        tasks = inventory["tasks"][status]
        if not tasks:
            print("  - none")
        for task in tasks:
            print(f"  - {task['title']} [{task['teamspace']}] -> {task['path']}")
    print("\nBacklog counts:")
    for teamspace, count in inventory["backlog_counts"].items():
        print(f"  - {teamspace}: {count}")
    print_grouped("Epics", inventory["epics"])
    print_grouped("Projects", inventory["projects"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print live vault periods, routing sources, tasks, projects, and epics.")
    parser.add_argument("--root", default=None, help="Vault root. Defaults to auto-discovery.")
    parser.add_argument("--active-only", action="store_true", help="Show active teamspace folders only.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    root = resolve_vault_root(args.root, __file__)
    inventory = build_inventory(root, args.active_only)
    if args.json:
        print(json.dumps(inventory, indent=2))
        return 0
    print_inventory(inventory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
