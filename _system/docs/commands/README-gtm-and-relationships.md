# GTM and relationship workspace

Use one structure for every company context. The business context pack under
`_system/bootstrap/templates/context-folders/business/` is the canonical source.
`$marketing-i-setup-gtm-workspace` applies the relevant part of that pack to an
existing context without replacing files.

## Folder model

```text
<context>/
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
└── relationships/
    ├── relationships.md
    ├── people/
    ├── companies/
    ├── opportunities/
    └── imports/
```

`company/` describes the business and market. `gtm/` contains acquisition and
conversion work. `relationships/` is the CRM memory shared by sales,
partnerships, customer research, delivery, and talent.

The shared tool inventory and rules live once in [[README-marketing-stack]] and
[[stack]] under `_system/docs/marketing-stack/`. Neither the business nor the
personal-brand pack copies a `marketing-stack/` folder into a context.

## CRM boundary

Each company has its own `relationships/` tree and context-filtered Base. Both
use the same record fields and templates. A lead is a person or company at an
early commercial stage; it does not need a separate `leads/` folder or an
opportunity note.

Keep one note per actionable lead, relationship, researched account, or
qualified opportunity. Store unchanged CSV and workbook sources in
`relationships/imports/` during migration. A large, unselected prospect list
can remain a source file. Do not confuse such a list with a smaller working
lead sheet that needs follow-up.

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

Preserve the original source row and status during a conversion. A source label
such as `Follow up` is an action queue, not proof of a `qualified` stage or a
real `last_contact` date. Migrate in a reviewable batch, check counts and
duplicates, then switch the Base to the converted records. Do not erase the
source sheet.

Use `possible`, `connected`, `qualified`, `proposed`, `engagement-planned`,
`client`, and `dormant` for `commercial_stage`. A person or company may stay
`connected` while a linked opportunity moves through its own pipeline.

## Attio boundary

The Vault remains the durable narrative and source archive. Attio may become the
operational CRM when email/calendar sync, team workflows, automation, or large
list management outweigh the cost of another system.

The model maps without redesign:

- `people/` to Attio People, keyed by email;
- `companies/` to Attio Companies, keyed by domain;
- `opportunities/` to Attio Deals;
- campaign-specific fields to Attio Lists;
- `imports/` to retained source exports and migration files.

Do not make Attio the only copy of relationship notes. Export it periodically if
it becomes operational.

## Existing contexts

Run the setup skill rather than copying files by memory:

```text
$marketing-i-setup-gtm-workspace
```

The setup is additive. Existing `crm/`, CSV, workbook, and relationship folders
remain untouched until a separate conversion is approved. For Impression, read
[[Lead sources and mapping]] before that conversion. Outsource Think's existing
people and company notes remain in its own CRM.
