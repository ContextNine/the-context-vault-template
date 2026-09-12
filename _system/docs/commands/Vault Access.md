---
type: agent-reference
status: enabled
---

## Vault access

`vault access` checks whether a registered machine can safely use its Vault worktree. The command has no editing session, lock, handoff, or completion workflow.

### Commands

```bash
vault access status [--json]
vault access doctor [--json]
vault access mount
vault access unmount
```

`mount` and `unmount` operate SSHFS only on a registered `remote-sshfs` Linux client. A Mac reports its local iCloud worktree instead.

### Linux editing gate

Before reading or editing the Vault on Linux, run:

```bash
vault access status
```

Continue only when the command exits successfully and reports `"ok": true`. Otherwise do not edit.

Status proves that SSH works, the exact registered SSHFS source is mounted read-write, the Vault sentinel exists, the source host identity matches, and the source iCloud worktree is fully downloaded, current, conflict-free, and not paused. Pending outbound upload and a container that is still uploading do not make the mounted worktree stale.

Macs edit their local iCloud worktrees normally and do not run an access gate. Linux writes land directly in the configured Mac host's worktree through SSHFS. That Mac's iCloud client distributes them to the other Macs. Only the registered Git owner commits and pushes the Vault.

Setup, systemd, SSHFS options, acceptance, and recovery belong to [[linux-remote-vault-access|Linux Remote Vault Access]] under `$infra-i-onboard-machine`. Machine roles and Git ownership are documented in [[README-primary-worker-vault-sync|Primary and Worker Vault Coordination]] and [[Vault Git Sync]].
