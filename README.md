# FIU Brain plugin marketplace

One plugin, three commands, no code: `/fiu-brain:start`, `/fiu-brain:stop`, `/fiu-brain:process-proposals`.
Each command asks the FIU Brain MCP server for its current instructions (`get_skill`) and follows them,
so the instructions are maintained in one place (the API repository) and this plugin never needs an update.

The plugin contains no hooks, no executables, no agents and no MCP server configuration; it can do nothing
without the FIU Brain connector the person already has.

## Install

Claude Code:

    /plugin marketplace add software-for-good/fiu-brain-plugin
    /plugin install fiu-brain@fiu-brain

Cowork: Plugins, upload this repository's `plugins/fiu-brain` folder (or the marketplace once private
marketplaces are supported in Cowork).

## Connector

The commands need the FIU Brain connector: Claude Code `claude mcp add --transport http fiu-brain
https://<api-host>/mcp/brain --header "Authorization: Bearer <your token>"`; Cowork and claude.ai: add a
custom connector with the same URL and the same header. Tokens come from `php artisan brain:token`.
