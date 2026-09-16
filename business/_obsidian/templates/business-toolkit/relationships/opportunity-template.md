<%*
const date = tp.date.now("YYYY-MM-DD");
const context = tp.file.folder(true).split("/")[0];
-%>
---
context: "[[<% context %>]]"
record_type: opportunity
name: "<% tp.file.title %>"
crm:
- commercial
commercial_stage: qualified
company:
contacts:
offer:
campaign:
value:
expected_close:
source:
last_contact:
follow_up:
next_action:
date: <% date %>
---

## Need

## Commercial path

## Evidence
