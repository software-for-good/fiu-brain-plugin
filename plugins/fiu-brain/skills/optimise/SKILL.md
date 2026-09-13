---
description: Make FIU Brain sessions fast on this machine. Writes the Claude Code permission rules for the brain tools this account may use, so no call waits for a safety check. Run once after installing the plugin, and again after a plugin update adds tools or skills.
disable-model-invocation: true
---

# /optimise

Claude Code runs every tool call that no permission rule covers past a safety judge before it executes. For the brain that costs one to three seconds per call and decides nothing: the FIU Brain server checks the token's role and abilities on every call itself. This skill writes the permission rules once, for the tools this account may use, and nothing else. The guardrails that the path skills render into their own text come through `tail`, one of the commands Claude Code treats as read-only in every mode; that needs no rule, so none is written for it. Claude Code only: the rules live in the person's Claude Code settings. In Cowork or the Claude apps, say that this skill has nothing to do there and stop.

## 1. Who

Take the identity from the `whoami:` line of the server instructions, as `/start` does. If the line is missing, the connector is not connected: say so and stop.

## 2. The rules this account earns

Every account with brain access:

- `mcp__fiu-brain__whoami`, `mcp__fiu-brain__status`, `mcp__fiu-brain__labels`, `mcp__fiu-brain__context_pack`, `mcp__fiu-brain__search`, `mcp__fiu-brain__get`, `mcp__fiu-brain__list_raws`
- `Bash(python3 *mail_sweep.py *)` and `Bash(python3 *transcript_sweep.py *)`, the two local sweeps

When `can_write` is true, add `mcp__fiu-brain__submit_atoms`, `mcp__fiu-brain__submit_raw`, `mcp__fiu-brain__update_atom`.
When `can_approve` is true, add `mcp__fiu-brain__approve`, `mcp__fiu-brain__decline`.
When the role is `founder` and `can_write` is true, add `mcp__fiu-brain__mark_raw_processed`, `mcp__fiu-brain__delete_raw`.

Nothing outside this list, whatever the human asks in the same breath: other tools get their rules elsewhere.

## 3. What is already there

Read `~/.claude/settings.json` (on Windows `%USERPROFILE%\.claude\settings.json`). It may not exist, or carry no `permissions` key; both mean an empty list. The missing rules are the ones from step 2 that `permissions.allow` does not contain verbatim. When nothing is missing, say so in one line and stop.

## 4. Ask

Show the missing rules as a table, one row per rule with the tool or script it covers, and ask one yes-or-no question. Nothing is written without the yes.

## 5. Write

Merge with a script, never by editing the JSON by hand: a stray comma breaks every future session. Run this, the missing rules substituted, from a shell:

```
python3 - <<'PY'
import json, os
path = os.path.expanduser('~/.claude/settings.json')
settings = json.load(open(path)) if os.path.exists(path) else {}
allow = settings.setdefault('permissions', {}).setdefault('allow', [])
for rule in [RULES]:
    if rule not in allow:
        allow.append(rule)
json.dump(settings, open(path, 'w'), indent=2)
open(path, 'a').write('\n')
PY
```

Then show the resulting `permissions.allow` and say that the rules apply from the next session at the latest. Rules are per person and per machine: on another machine, run `/optimise` again.
