`business/` and `personal-brand/` are the physical packs used by `vault folder create --folder-template`. They do not create a context type. Bootstrap and public export use the same packs.

The business pack holds company, relationship, and operating folders plus managed business-toolkit templates. Its GTM tree comes from `_system/templates/gtm/scaffold/` rather than a second editable copy. The personal-brand pack stores identity and marketing files under `brand/`. Existing context edits are never replaced during setup.

The pack READMEs and [[README-crm]] remain under `_system/templates/`; they are not copied into contexts.
