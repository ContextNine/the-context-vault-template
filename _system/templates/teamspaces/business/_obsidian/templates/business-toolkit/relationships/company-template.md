<%*
const date = tp.date.now("YYYY-MM-DD");
const context = tp.file.folder(true).split("/")[0];
-%>
---
context: "[[<% context %>]]"
record_type: company
name: "<% tp.file.title %>"
domain:
crm:
- commercial
commercial_stage: possible
relationship_roles:
- contact
contacts:
source:
last_contact:
follow_up:
next_action:
date: <% date %>
---

## Context

## Conversations
