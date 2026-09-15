---
type: agent-reference
status: enabled
---
# Attachments

Dry-run attachment routing and cleanup:

```bash
vault attachments --dry-run
```

Apply the planned cleanup:

```bash
vault attachments
```

Verify after cleanup:

```bash
vault attachments --verify-only
```

Reconcile a fresh Notion Learning export against current vault notes. This is
read-only by default and writes an auditable manifest before any changes:

```bash
vault attachments --reconcile-learning-export "/path/to/LEARNINGRECON" --repair-deterministic-global
vault attachments --reconcile-learning-export "/path/to/LEARNINGRECON" --repair-deterministic-global
```

Reconciliation preserves current note prose and frontmatter, restores missing
export embeds, renames generic media to globally unique note-derived basenames,
and refuses ambiguous note or attachment mappings.

Only files embedded from Markdown notes belong in `_obsidian/attachments`. Route them under the top-level folder that owns the note, such as `_library/_obsidian/attachments` or `business/_obsidian/attachments`. Store standalone files beside the owning content, never under `_obsidian`. Obsidian's built-in paste destination is the temporary inbox `_system/_obsidian/attachments/_inbox`.

Dry-run/apply reports and recoverable quarantined import files are written under ignored `_system/local/state/attachments/`. Learning reconciliation uses the same local state root. Attachment commands never create generated output in `~/Downloads`. After each cleanup dry run or apply run, Finder opens the local state folder.

Implementation script: `_system/commands/attachments.py`.
