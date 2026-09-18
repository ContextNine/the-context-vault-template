---
type: agent-reference
status: enabled
---

# Business Toolkit

This note is the navigation home for the business toolkit. The business teamspace pack lives under `_system/templates/teamspaces/business/` and composes the GTM tree from `_system/templates/gtm/scaffold/`. Selecting `--folder-template business` for a new teamspace installs the full folder tree and managed templates. A teamspace is considered configured only when `_obsidian/business-toolkit.json` exists; there is no business teamspace type.

## Interactive installer

```bash
vault business-toolkit
```

The wizard lists registered teamspaces, accepts a multi-selection, and allows component or group exclusions.

## Preview and apply

```bash
vault business-toolkit sync --teamspace-folders business,studio
vault business-toolkit sync --teamspace-folders business,studio --apply
vault business-toolkit sync --teamspace-folders studio --include company,gtm --apply
vault business-toolkit sync --configured
vault business-toolkit status --configured
vault business-toolkit unconfigure --teamspace-folders studio
```

Available groups are `company`, `meetings`, `product`, `gtm`, `relationships`,
`operations`, and `skills`. Company identity research, including audience and
competitors, lives under `company/`. Campaigns, offers, market sizing, and the
funnel live under `gtm/`. The single shared marketing stack is [[README-marketing-stack]], outside
every teamspace. Curated CRM records and raw imports live under `relationships/`.
Component ids are listed in the canonical pack manifest.

Use [[README-gtm-and-relationships]] for the shared company GTM and relationship
model and for retrofitting an existing teamspace.

Explicit targets may be any registered teamspace. Normal sync never creates, deletes, or restructures ordinary folders. It protects locally changed installed templates and changed managed icons. Apply mode preflights all selected teamspaces: a terminal asks once before overwriting all conflicts, a non-interactive run aborts without mutation, and `--force` explicitly replaces them.

Excluding a previously installed component removes its managed Templater rule, unchanged installed template, and unchanged managed icon. Operating folders and business notes are never deleted.

Each configured teamspace stores its selection, installed hashes, icon ownership, and pack version in `_obsidian/business-toolkit.json`. Desktop and mobile Iconize files are reconciled when present; unrelated settings and custom icons are preserved.

`unconfigure` safely removes unchanged managed templates, rules, icons, and the marker. Use `--force` only when intentionally discarding locally changed managed files.

Periodic templates, TaskNotes templates, generated Bases, teamspace notes, and Excalidraw setup remain owned by the core bootstrap generator.
