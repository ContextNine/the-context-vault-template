Use this guide when the user asks to add, find, or update one person, company, lead, opportunity, or follow-up in a company teamspace. See [[README-gtm-and-relationships]] for the folder model.

## Choose the destination

Use the company the user names. Confirm it with `vault inventory`, then read its teamspace note, `relationships/relationships.md` if present, and any lead-source mapping note. Do not route a CRM contact to the default personal teamspace.

Find the company's current working CRM source before writing. If it is a workbook or CSV, update that source through the spreadsheet workflow when the requested destination is clear. If several live files could be the write target, ask which one; do not pick one by filename or silently create a relationship note instead. If an app owns the record, use its approved write workflow only when the request authorizes that app. A relationship note never updates a separate lead sheet or app.

The remaining instructions apply when the requested destination is the company's note-based `relationships/` CRM, or the user explicitly asks for a curated relationship note. Keep any external CRM or lead sheet authoritative until its owner has approved a reviewed migration.

## Where a record goes

- Store people in `<context>/relationships/people/`, companies in `companies/`, and a qualified commercial pursuit in `opportunities/`. Do not put contacts inside `gtm/`. Company teamspaces keep separate relationship folders even when they know the same person.
- Before writing, search that teamspace's relationship notes and any current CRM source files for the name, email, company, and profile URL the user supplied. Use `$witan-xlsx` if checking a workbook is necessary. Never merge people on name alone.
- If a matching note exists, update that note without removing its existing fields or history. If a source sheet contains a possible match but no relationship note exists, create a note only when note capture was the selected destination, and preserve the source sheet unchanged. If two identities remain plausible, report the matches and ask for the one fact needed to distinguish them.

## Create a person quickly

Use the current person field contract in `_system/templates/teamspaces/business/_obsidian/templates/business-toolkit/relationships/person-template.md`. Write a normal Markdown note with resolved frontmatter values, not literal Templater tags.

For a name-only commercial contact, the minimum useful record is `context`, `record_type: person`, `name`, `crm: [commercial]`, `commercial_stage: possible`, and the current `date`. Put the user's actual information in the Context or Conversations section. Leave email, company, profile, last contact, next action, and follow-up empty or absent until known. A note created today does not imply the user contacted the person today. Preserve the user's wording when it might matter.

For example, replace the teamspace, name, and date below with the actual values:

```yaml
---
context: "[[company-slug]]"
record_type: person
name: "Jane Doe"
crm:
  - commercial
commercial_stage: possible
date: YYYY-MM-DD
---
```

Name the file so it is recognisable and unique across the Vault. If a same-named note already exists elsewhere, append a short company qualifier to the new filename so unqualified `[[Name]]` links remain clear. Add a company link only when the company record exists or the user asked to create it. A company record follows the same pattern using the current company template. Create an opportunity only when a need and commercial path are actually known.

If a teamspace uses both `commercial` and `talent` lanes, preserve them. For a candidate or talent connection, inspect its `relationships/relationships.md` and relevant notes, then use `crm: [talent]` and the existing `talent_stage` fields. Do not relabel talent as commercial without evidence. Follow-up dates and last-contact dates must come from actual information, not note modification time.

After saving, check that the note appears in the owning teamspace and the relevant teamspace-filtered CRM Base. Return a link to the created or updated note and mention any missing detail only if it changes the next action. Do not create a TaskNotes task merely because a person was captured; create one when the user gives an executable action to schedule.

## Boundaries

An individual capture request does not authorize importing a whole CSV, converting a workbook, moving old notes, deleting duplicates, or changing subscriptions. A request to update one row in a clearly selected working lead sheet is different from converting the sheet. Do not write to a production app unless the user explicitly requests that destination. Preserve source statuses and follow a reviewed migration plan before changing their source of truth.

When an app CRM becomes operational, change this guide's destination and verify the agent's write path before retiring note-based capture. The `vault-i-use-crm` skill keeps pointing here, so capture requests can use the same wording.
