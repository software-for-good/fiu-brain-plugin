# FIU Brain plugin

The skills of the FIU Brain. This repository is the single place they live; a merged pull request reaches
every session because both clients keep the plugin in sync:

- Cowork: Plugins → Add marketplace → `software-for-good/fiu-brain-plugin`, install `fiu`, turn auto-sync on.
- Claude Code: `/plugin marketplace add software-for-good/fiu-brain-plugin`, `/plugin install fiu@fiu-brain`,
  then enable auto-update for the marketplace under `/plugin` → Marketplaces.

One plugin for everyone, two session commands: `/fiu:start` opens every session and `/fiu:stop` closes it.
`/fiu:start` takes the role from `whoami` and offers only the goals that fit it; founders additionally get
"process the source queue" and "decide proposals", which hand off to the `process` and `process-proposals`
skills. Those two, like `guardrails` and `extraction-rules`, carry `user-invocable: false`: hidden from the
command menu and not runnable by hand, loadable only by the AI, so every path starts with the guardrails and
the identity check in place. This is convenience, not security: the server checks each token's role and
abilities on every tool call, whatever the skills say.

The two sweeps, `/fiu:mail-sweep` and `/fiu:transcript-sweep`, stay direct commands: they run once per person,
locally, and never touch the brain.

The plugin contains no hooks, executables, agents or MCP server configuration; the skills only call the
FIU Brain connector the person already has (a custom connector or `claude mcp add` with a personal bearer
token from `php artisan brain:token`). Nothing sensitive is stored here.
