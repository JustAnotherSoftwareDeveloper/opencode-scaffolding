# Current linter boundary

The Markdown linter accepts one file and reports deterministic syntax diagnostics.
Proposal source identity and relative workspace links require directory context. The
migration must preserve generic-file rules, diagnostic order, and exit codes.
