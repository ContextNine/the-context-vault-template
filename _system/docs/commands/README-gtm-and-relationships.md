# GTM and relationship workspace

Use one company and GTM structure for every company teamspace. The business pack lives under
`_system/templates/teamspaces/business/` and composes the GTM tree from
`_system/templates/gtm/scaffold/`. `$marketing-i-setup-gtm-workspace` applies
the relevant files to an existing teamspace without replacing edits.

For an individual contact or relationship update, use `$vault-i-use-crm` and
[[README-crm]]. The CRM guide lives under `_system/templates/gtm/` and is not
part of a teamspace's copied `gtm/` tree.

## Folder model

```text
<teamspace>/
├── company/
│   ├── audience/
│   └── competitors/
├── gtm/
│   ├── campaigns/
│   ├── offers/
│   ├── tam-to-som/
│   ├── funnel.excalidraw
│   ├── assets.md
│   └── learnings.md
└── relationships/                 # optional note-based CRM
    ├── relationships.md
    ├── people/
    ├── companies/
    ├── opportunities/
    └── imports/
```

`company/` describes the business and market. `gtm/` contains acquisition and
conversion work. When selected, `relationships/` holds curated notes shared by
sales, partnerships, customer research, delivery, and talent. GTM setup does
not require it.

Shared tool rules live once in [[README-marketing-stack]] under
`_system/templates/gtm/marketing-stack/`. There is no separate live inventory
in the Vault, and neither teamspace pack copies a `marketing-stack/` folder.

## CRM boundary

Companies that adopt the note-based CRM each have their own `relationships/`
tree and teamspace-filtered Base. They use the same record fields and templates.
A lead is a person or company at an early commercial stage; it does not need a
separate `leads/` folder or an opportunity note.

For a company using relationship notes as its CRM, keep one note per selected
actionable lead, relationship, researched account, or qualified opportunity.
New retained import and export files belong in `relationships/imports/`. Do not
move an existing working lead sheet or convert its rows merely because the
folder exists. A large, unselected prospect list can remain a source file.

Use email as the preferred identifier for people and domain for companies when
present. When identifiers are absent, compare name, company, profile URL, and
notes, then review potential matches manually. Never merge on name alone. Keep
source files unchanged so imports can be repeated or audited.

The shared record fields are:

- every record: `context`, `record_type`, `name`, `crm`, `commercial_stage`,
  `source`, `last_contact`, `follow_up`, and `next_action`;
- people: `company`, `email`, `phone`, `linkedin`, and `relationship_roles`;
- companies: `domain`, `contacts`, and `relationship_roles`;
- opportunities: `company`, `contacts`, `offer`, `campaign`, `value`, and
  `expected_close`.

In an approved conversion, preserve the original source row and status. A
source label such as `Follow up` is an action queue, not proof of a `qualified`
stage or a real `last_contact` date. Migrate in a reviewable batch, check counts
and duplicates, then switch the Base to the converted records. Do not erase the
source sheet.

Use `possible`, `connected`, `qualified`, `proposed`, `engagement-planned`,
`client`, and `dormant` for `commercial_stage`. A person or company may stay
`connected` while a linked opportunity moves through its own pipeline.

## Operational CRM boundary

The folder template does not choose an operational CRM app. A company may keep
an existing lead sheet or app as its working source while using relationship
notes for selected narrative teamspace. Any change of source of truth needs its
own reviewed migration. Do not stage a full lead-sheet conversion into notes
as a temporary step toward an app CRM.

## Existing teamspaces

Run the setup skill rather than copying files by memory:

```text
$marketing-i-setup-gtm-workspace
```

The setup is additive. Existing `crm/`, CSV, workbook, and relationship folders
remain untouched until a separate conversion is approved. Read the selected
teamspace's source mapping and relationship home note before changing records.

When applying GTM to an existing teamspace, the setup script adds `company/` and
`gtm/` by default. Pass `--relationships` only when adopting the optional
relationship-note CRM. New `business` teamspaces use the full business pack.
