---
description: Start an FIU Brain session. Run this at the beginning of every session, optionally with the goal of the session as argument.
disable-model-invocation: true
---

# /start

You open a session on the FIU Brain. This skill does one thing: it establishes who you work with and what the session is for, then hands over to the skill for that work. It makes no tool call and reads nothing from the brain. The first thing the human reads is the question of step 2, or, when the goal came as argument, the first words of the work itself.

## 1. Identify

The FIU Brain server hands its instructions to every session at connect, and for a connected account they end with a `whoami:` line: name, slug, role, clearance, `can_write`, `can_approve`. Read it from your context. If there is no such line, the connector is not connected (Settings, Connectors, or `claude mcp add` with a personal token): say so and stop.

## 2. Establish the goal

With `$ARGUMENTS`: `process` selects path 1 and `approve` selects path 2, under the same conditions as the options below; any other text is the goal as given and takes path 3 when it is about preparing a meeting with a client, otherwise path 4. An ambiguous argument gets exactly one clarifying question. A goal this account is not allowed gets the one-line reason from the option below, then the question.

Without arguments, ask this single-select question, name and role from step 1, and nothing before it:

> `<name>, <role>. What is this session for?`
>
> 1. **Process the source queue**: turn ingested sources into atoms.
> 2. **Approve company-wide atoms**: decide the proposed company-wide atoms.
> 3. **Prepare a client meeting**: pull what the brain holds on a client, then think it through together.
> 4. **Ask the brain**: what do we know about a client, a person, a service, a topic.

Drop option 1 unless the role is `founder`: the server lets only founders mark a source processed. Drop option 2 unless `can_approve` is true. The question tool adds "Other" by itself; "Other" or a typed line is the goal as given. Never fill the goal in yourself.

## 3. Hand over

Load the skill of the path and follow it. Each path carries the guardrails and reuses the identity from step 1; nothing else is loaded here.

| Path | Skill |
|---|---|
| 1. Process the source queue | `fiu:process` |
| 2. Approve company-wide atoms | `fiu:process-proposals` |
| 3. Prepare a client meeting | `fiu:meeting` |
| 4. Ask the brain, and every other goal | `fiu:work` |
