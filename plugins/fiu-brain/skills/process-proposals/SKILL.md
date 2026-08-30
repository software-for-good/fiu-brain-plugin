---
description: Founders only. Work through the FIU Brain proposal backlog in one conversation.
disable-model-invocation: true
---

1. Call `whoami`; if `can_approve` is false, tell the user this is founders only and stop.
2. Call `search` with `statuses: ["proposal"]` and list the open proposals, sorted by how certain they read.
3. The approve and decline tools arrive in increment two; until then, stop after the list.

This is a short stub; the full skill follows.
