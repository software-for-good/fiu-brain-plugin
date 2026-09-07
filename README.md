# FIU Brain plugin

The skills of the FIU Brain. This repository is the single place they live; a merged pull request reaches
every session because both clients keep the plugin in sync:

- Cowork: Plugins → Add marketplace → `software-for-good/fiu-brain-plugin`, install `fiu`, turn auto-sync on.
- Claude Code: `/plugin marketplace add software-for-good/fiu-brain-plugin`, `/plugin install fiu@fiu-brain`,
  then enable auto-update for the marketplace under `/plugin` → Marketplaces.

One plugin for everyone, two session commands: `/fiu:start` opens every session and `/fiu:stop` closes it.
`/fiu:start` is a router: it takes the identity the server hands over at connect (the `whoami:` line of its
instructions), establishes the goal (from its argument, or with one fixed question that offers only the goals fitting
the role) and hands over to the skill for that path: `process` and `process-proposals` for founders, `meeting` for
preparing a client meeting, `work` for questions and everything else. Each path renders the `guardrails` into its own
text, so they apply from the moment the goal is known and never delay the opening question; `work-folder` (where files
belong, when a project folder is made) is loaded only by a path that is about to create a file. All of those carry
`user-invocable: false`: hidden from the command menu and not runnable by hand, loadable only by the AI. This is
convenience, not security: the server checks each token's role and abilities on every tool call, whatever the skills say.

The two sweeps, `/fiu:mail-sweep` and `/fiu:transcript-sweep`, stay direct commands: they run once per person,
locally, and never touch the brain.

`/fiu:optimise` is Claude Code housekeeping, once per person and machine: it writes the permission rules for the
brain tools the account may use, so no call waits for Claude Code's safety judge (one to three seconds per call
that the server's own role and ability checks make redundant). Run it again after a plugin update adds tools.

The plugin contains no hooks, executables, agents or MCP server configuration; the skills only call the
FIU Brain connector the person already has (a custom connector or `claude mcp add` with a personal bearer
token from `php artisan brain:token`). Nothing sensitive is stored here.
