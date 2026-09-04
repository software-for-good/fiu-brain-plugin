---
description: Founders only. Work through the proposed company-wide atoms in one conversation, with the context to decide each one. Reached from /start when a founder chooses to approve company-wide atoms; not a session entry point of its own.
user-invocable: false
---

# Approve company-wide atoms

This flow is reached from `/start`, which has loaded `fiu:guardrails` and called `whoami`; reuse both. If this session did not run `/start`, load `fiu:guardrails` and call `whoami` now, before anything else.

A company-wide atom applies to everyone, so it enters as `proposed` and becomes company truth only here. Scoped atoms never pass through this flow; they are live from the moment they are accepted.

## 1. Gate

If the connector is missing, say so and stop. If `can_approve` is false, say kindly that company-wide atoms are approved by founders, that everything else in the brain works as normal for this account, and that `/start` offers the goals that fit; stop.

If the approve and decline tools are not on the connector, say up front that the server side has not shipped yet and that this session can only prepare a decision list, then ask whether that is still wanted.

## 2. Load

`search` with `statuses: ["proposed"]`. Group by label rather than by date; a founder decides better on ten related claims than on ten unrelated ones. Within a group, most certain first.

## 3. Context per atom

Show title, body, source date, labels and origin. When the atom carries `proposes_to_supersede`, `get` the target and show both claims side by side. When one `search` on the title's key terms surfaces directly related atoms, mention them in one line; do not go hunting further.

## 4. Decide, per group

The founder may rule on a whole group in one word; walk the items one by one only where they ask. Per item the founder can:

- approve
- approve with an edit: the body is immutable, so submit the corrected wording as a new company-wide atom citing the original in its body, decline the original with reason "replaced by the corrected version", then approve the corrected one
- decline, always with a reason; the reason is what stops the claim coming back
- leave it open

Before approving anything that contradicts an existing company-wide atom, show both and ask which supersedes which; never resolve a contradiction yourself. Where clearance can be lowered, offer it: knowledge that arrived as founders material but is useful to the team should not stay locked up by accident.

## 5. Write

Call the approve and decline tools. Until those exist on the connector, produce the decisions as a clean list and say explicitly that nothing was written to the brain yet.

## 6. Report

Approved, declined with reasons, left open, and how many proposed atoms remain.
