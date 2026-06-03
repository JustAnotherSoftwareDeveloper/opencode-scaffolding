# Provider Concurrency Plugin

`provider-concurrency.ts` limits concurrent `task` tool calls per model provider inside the current OpenCode process. It is intended to keep delegated subagents from overloading a local model server or a paid remote provider.

## Use

This directory is the global OpenCode plugin directory for this machine. OpenCode auto-discovers `*.ts` and `*.js` files under `~/.config/opencode/plugins/`, so `plugins/provider-concurrency.ts` does not need an `opencode.json` plugin entry.

Restart OpenCode after changing this plugin or `opencode.concurrency.json`. Plugin and config files are loaded at startup.

## Configuration

The plugin reads `opencode.concurrency.json` from the same config directory:

```json
{
  "enabled": true,
  "debug": false,
  "mode": "reject",
  "providerLimits": {
    "openrouter": null,
    "ollama": 1
  },
  "agentProviderOverrides": {},
  "agentModelOverrides": {},
  "queueTimeoutMs": null,
  "staleLeaseMs": 600000
}
```

Fields:

- `enabled`: disables all limits when set to `false`.
- `debug`: logs missing or stale lease details with `console.warn`.
- `mode`: `reject` throws immediately when a provider is full; `queue` waits for a slot.
- `providerLimits`: provider to max concurrent `task` calls. Set a provider value to `null` to make that provider explicitly unlimited, for example `{ "openrouter": null }`.
- `agentProviderOverrides`: agent name to provider, for example `{ "worker-xs": "ollama" }`.
- `agentModelOverrides`: agent name to model string with provider prefix, for example `{ "worker-md": "ollama/worker-md-local" }`.
- `queueTimeoutMs`: max queue wait before throwing in `queue` mode. Set to `null` for no queue timeout.
- `staleLeaseMs`: age after which a lease can be cleaned up before another same-provider acquire. Set to `0` to disable stale cleanup.

## Provider Resolution

The plugin only intercepts OpenCode's `task` tool. Provider resolution order is:

1. `args.model` or `args.subagent_model` when it has a `provider/model` prefix.
2. The task agent name from `subagent_type`, `agent`, `subagent`, or `agentName`.
3. `agentModelOverrides[agent]`, parsed as `provider/model`.
4. `agentProviderOverrides[agent]`.

If no provider is found, the provider has no configured limit, or the provider limit is `null`, the task runs without throttling.

## Local Examples

Current worker examples in this config:

- `worker-xs`: `ollama/worker-xs-local`, so it resolves to `ollama`.
- `worker-sm`: `ollama/worker-sm-local`, so it resolves to `ollama`.
- `worker-md`: `ollama/worker-md-local`, so it resolves to `ollama`.

Equivalent explicit overrides:

```json
{
  "agentModelOverrides": {
    "worker-xs": "ollama/worker-xs-local",
    "worker-sm": "ollama/worker-sm-local",
    "worker-md": "ollama/worker-md-local"
  }
}
```

## Limitations

- Limits are process-local. They do not coordinate across multiple OpenCode processes or terminals.
- This does not intercept direct provider API calls; it only gates OpenCode `task` tool execution.
- OpenCode currently exposes `tool.execute.before` and `tool.execute.after` for this use. If a task starts but no `after` hook runs, `staleLeaseMs` is the recovery mechanism.
- This is a concurrency guard, not a token, billing, health-check, or provider rate-limit scheduler. Provider limits are defense-in-depth; they complement orchestrator-level lifecycle policies like one-worker-at-a-time execution but do not replace them.
