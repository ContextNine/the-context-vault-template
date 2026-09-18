This is the reusable GTM component. `scaffold/gtm/` is copied into a company teamspace's `gtm/` on setup. [[README-crm]] and [[README-marketing-stack]] are shared operating rules that stay here. Do not copy this `README.md`, `README-crm.md`, or `marketing-stack/` into any teamspace.

The business teamspace pack at `_system/templates/teamspaces/business/` composes this GTM component for new teamspaces. `$marketing-i-setup-gtm-workspace` adds missing files to existing teamspaces without replacing their edits. The personal-brand pack keeps its marketing work under `brand/` and does not copy the company GTM scaffold.

GTM setup does not require converting lead sheets or adopting Markdown CRM records. Keep each company's working lead sources and relationship history intact until a separate reviewed migration.
