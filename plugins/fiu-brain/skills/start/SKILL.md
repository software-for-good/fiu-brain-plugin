---
description: Start an FIU Brain session. Run this at the beginning of every session, optionally with the goal of the session as argument.
disable-model-invocation: true
---

Call the FIU Brain MCP tool `get_skill` with the argument `name: "start"` and follow the instructions it returns, exactly and completely.

The goal of this session, if the user gave one: $ARGUMENTS

If the `get_skill` tool is not available, the FIU Brain connector is not connected. Say so, point the user to the FIU Brain setup notes, and stop.
