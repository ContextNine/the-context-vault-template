<%*
const date = tp.date.now("YYYY-MM-DD");
const context = tp.file.folder(true).split("/")[0];
-%>
---
context: "[[<% context %>]]"
record_type: person
name: "<% tp.file.title %>"
crm:
- commercial
commercial_stage: possible
relationship_roles:
- contact
company:
email:
phone:
linkedin:
source:
last_contact:
follow_up:
next_action:
date: <% date %>
---

## Context

## Conversations
