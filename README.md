# FIU Brain plugin

The skills of the FIU Brain: `/fiu-brain:start`, `/fiu-brain:stop`, `/fiu-brain:process-proposals`, and the
`extraction-rules` every extracting path follows. This repository is the single place they live; a merged
pull request reaches every session because both clients keep the plugin in sync:

- Cowork: Plugins → Add marketplace → `software-for-good/fiu-brain-plugin`, install `fiu-brain`, turn auto-sync on.
- Claude Code: `/plugin marketplace add software-for-good/fiu-brain-plugin`, `/plugin install fiu-brain@fiu-brain`,
  then enable auto-update for the marketplace under `/plugin` → Marketplaces.

The plugin contains no hooks, executables, agents or MCP server configuration; the skills only call the
FIU Brain connector the person already has (a custom connector or `claude mcp add` with a personal bearer
token from `php artisan brain:token`). Nothing sensitive is stored here.
