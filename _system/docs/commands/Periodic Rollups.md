---
type: agent-reference
status: enabled
---
# Periodic Rollups

## Source Notes

Teamspace folder periodic notes are editable source of truth:

```text
<teamspace-folder>/_obsidian/periodic/daily/YYYY-MM-DD.md
<teamspace-folder>/_obsidian/periodic/weekly/YYYY-Www.md
<teamspace-folder>/_obsidian/periodic/monthly/YYYY-MM.md
<teamspace-folder>/_obsidian/periodic/quarterly/YYYY-Qn.md
<teamspace-folder>/_obsidian/periodic/yearly/YYYY.md
```

Root Periodic Notes defaults to `personal`. Opening today's daily note creates or opens `personal/_obsidian/periodic/daily/YYYY-MM-DD.md`.

Missing source notes are created from each teamspace folder's local `_obsidian/templates/periodic/<period>-template.md`. `personal` has filled starter templates; other folders may intentionally use blank templates.

Periodic notes are enabled by default for active teamspaces. Add `periodic_notes_enabled: false` to a teamspace control note to prevent future source-note generation and omit that teamspace from vault rollups. The opt-out also applies to `--all` and explicit `--teamspace-folders` runs. Existing source notes remain untouched.

Existing daily notes are append-only during generation: they are never replaced from the template. Refresh carries the most recent earlier note's daily task section forward by appending unchecked checklist items, ordinary text, and nested headings while omitting checked checklist lines and preserving everything already present in the destination note.

## Generated Rollups

Vault rollups use Sync Embeds and live under:

```text
_system/_obsidian/periodic/<period>/<period-id>.md
```

Teamspace source notes remain editable. Generated vault rollups are read-only derived views. Dashboard links current daily, weekly, monthly, quarterly, and yearly vault rollups.

The filename is the rollup title. Generated rollups start with the teamspace sections and do not repeat the period ID as a heading in the note body.

## Generate

Generate current source notes and vault periodic rollups:

```bash
vault periodic
```

Useful variants:

```bash
vault periodic --all
vault periodic --teamspace-folders dev,business
```

Teamspace folder periodic notes remain editable source of truth. Vault rollups live under `_system/_obsidian/periodic/<period>/` and use Sync Embeds. `vault refresh` calls periodic generator automatically.

Dashboard unfinished monthly-SOP reminders inspect source monthly notes directly, using historic vault monthly rollups as period indexes. No copied agent-periodic notes are generated.

Periodic templates may include `{{current_content_schedule_sync_embed}}`. Generator replaces it with Sync Embed pointing at active four-week content schedule when teamspace has enabled cadence config.

Implementation script: `_system/commands/periodic.py`.
