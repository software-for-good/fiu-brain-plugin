---
description: Start an FIU Brain session. Run this at the beginning of every session, optionally with the goal of the session as argument.
disable-model-invocation: true
---

1. Call `whoami` on the FIU Brain connector. If it is not available, tell the user the FIU Brain connector is not connected and stop.
2. Establish the goal of the session: use `$ARGUMENTS` if given, otherwise ask one short question (goal, audience, perspective; multiple choice where possible). Do not fill in the goal yourself.
3. Call `context_pack` with the goal, written in English, and any labels you can derive from it (websites/…, person/…, theme/…).
4. Read the pack: agreed atoms are company truth, observed atoms are facts about the named entities, proposals are unconfirmed. Tell the user how fresh the brain is (from the status in the pack).
5. Work. Cite atoms by filename when you use them, and say so when the brain has nothing on a topic.

This is a short stub; the full skill follows.
