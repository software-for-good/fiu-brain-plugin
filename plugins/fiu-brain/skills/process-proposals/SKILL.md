---
description: Founders only. Work through the proposed company-wide atoms in one conversation, with the context to decide each one. Reached from /start when a founder chooses to approve company-wide atoms; not a session entry point of its own.
user-invocable: false
---

# Approve company-wide atoms

This flow is reached from `/start`, which has loaded `fiu:guardrails` and called `whoami`; reuse both. If this session did not run `/start`, load `fiu:guardrails` and call `whoami` now, before anything else.

A company-wide atom applies to everyone, so it enters as `proposed` and becomes company truth only here. Scoped atoms never pass through this flow; they are live from the moment they are accepted.

## 1. Gate

If the connector is missing, say so and stop. If `can_approve` is false, say kindly that company-wide atoms are approved by founders, that everything else in the brain works as normal for this account, and that `/start` offers the goals that fit; stop.

If the `approve`, `decline` and `update_atom` tools are not on the connector, say up front which are missing and that this session can only prepare a decision list, then ask whether that is still wanted.

## 2. Load

`search` with `statuses: ["proposed"]`. Group by label rather than by date; a founder decides better on ten related claims than on ten unrelated ones. Within a group, most certain first.

## 3. Verify product claims against the code

Proposed atoms about how the product or the tech works (what a feature does, how an integration behaves, a limit, a rule the software applies) are checked against the FIU codebase before a founder approves them; the process flow does not check them, because approval is where company truth is minted and where a founder with code access is present.

- When the FIU codebase is among the session's working folders, send an agent over those atoms and mark each one verified, contradicted or not checkable. Show the founder what the code says next to each claim. A contradicted claim is approved with an edit or declined, never approved as it stands.
- When the codebase is not available, say so once and ask whether the founder wants to add it before deciding. If they cannot or will not, leave the product claims open and continue with the rest; they wait for a founder who has code access.
- Never approve a product claim that was neither verified nor explicitly waived by the founder.

## 4. Context per atom

Show title, body, source date, labels and origin. When the atom carries `proposes_to_supersede`, `get` the target and show both claims side by side. When one `search` on the title's key terms surfaces directly related atoms, mention them in one line; do not go hunting further.

## 5. Decide, per group

The founder may rule on a whole group in one word; walk the items one by one only where they ask. Per item the founder can:

- approve
- approve with an edit: call `update_atom` with the corrected title, body, labels or clearance (a proposed atom is editable until it is decided; its filename stays), then approve it
- decline, always with a reason; the reason is what stops the claim coming back
- leave it open

Before approving anything that contradicts an existing company-wide atom, show both and ask which supersedes which; never resolve a contradiction yourself. Where clearance can be lowered, offer it: knowledge that arrived as founders material but is useful to the team should not stay locked up by accident.

## 6. Write

Call `update_atom`, `approve` and `decline`, one atom per call. Until those exist on the connector, produce the decisions as a clean list and say explicitly that nothing was written to the brain yet.

## 7. Report

Approved, declined with reasons, left open, and how many proposed atoms remain.
