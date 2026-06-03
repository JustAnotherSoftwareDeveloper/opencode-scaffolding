import { readFile } from "node:fs/promises"
import { join } from "node:path"
import type { Plugin } from "@opencode-ai/plugin"

type Mode = "reject" | "queue"

export type ProviderConcurrencyConfig = {
  enabled: boolean
  debug: boolean
  mode: Mode
  providerLimits: Record<string, number | null>
  agentProviderOverrides: Record<string, string>
  agentModelOverrides: Record<string, string>
  queueTimeoutMs: number | null
  staleLeaseMs: number
}

type Lease = {
  key: string
  provider: string
  acquiredAt: number
}

type Waiter = {
  key: string
  provider: string
  resolve: () => void
  reject: (error: Error) => void
  timeout: ReturnType<typeof setTimeout> | null
}

type State = {
  config: ProviderConcurrencyConfig
  leases: Map<string, Lease>
  activeByProvider: Map<string, Set<string>>
  queues: Map<string, Waiter[]>
}

export const DEFAULT_CONFIG: ProviderConcurrencyConfig = {
  enabled: true,
  debug: false,
  mode: "reject",
  providerLimits: {},
  agentProviderOverrides: {},
  agentModelOverrides: {},
  queueTimeoutMs: null,
  staleLeaseMs: 10 * 60 * 1000,
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value)
}

function stringRecord(value: unknown, field: string): Record<string, string> {
  if (value === undefined) return {}
  if (!isRecord(value)) throw new Error(`${field} must be an object`)

  const result: Record<string, string> = {}
  for (const [key, item] of Object.entries(value)) {
    if (typeof item !== "string" || item.trim() === "") {
      throw new Error(`${field}.${key} must be a non-empty string`)
    }
    result[key] = item
  }
  return result
}

function limitsRecord(value: unknown): Record<string, number | null> {
  if (value === undefined) return {}
  if (!isRecord(value)) throw new Error("providerLimits must be an object")

  const result: Record<string, number | null> = {}
  for (const [provider, limit] of Object.entries(value)) {
    if (limit === null) {
      result[normalizeProvider(provider)] = null
      continue
    }
    if (!Number.isInteger(limit) || limit < 1) {
      throw new Error(`providerLimits.${provider} must be a positive integer or null`)
    }
    result[normalizeProvider(provider)] = limit
  }
  return result
}

function nonNegativeInteger(value: unknown, field: string, fallback: number): number {
  if (value === undefined) return fallback
  if (!Number.isInteger(value) || value < 0) throw new Error(`${field} must be a non-negative integer`)
  return value
}

function nullableNonNegativeInteger(value: unknown, field: string, fallback: number | null): number | null {
  if (value === undefined) return fallback
  if (value === null) return null
  if (!Number.isInteger(value) || value < 0) throw new Error(`${field} must be a non-negative integer or null`)
  return value
}

export function normalizeProvider(provider: string): string {
  return provider.trim().toLowerCase()
}

export function parseConfig(input: unknown): ProviderConcurrencyConfig {
  if (input === undefined) return { ...DEFAULT_CONFIG }
  if (!isRecord(input)) throw new Error("opencode.concurrency.json must contain a JSON object")

  const mode = input.mode === undefined ? DEFAULT_CONFIG.mode : input.mode
  if (mode !== "reject" && mode !== "queue") throw new Error("mode must be \"reject\" or \"queue\"")
  if ("defaultProvider" in input) throw new Error("defaultProvider is not supported")

  return {
    enabled: input.enabled === undefined ? DEFAULT_CONFIG.enabled : input.enabled === true,
    debug: input.debug === undefined ? DEFAULT_CONFIG.debug : input.debug === true,
    mode,
    providerLimits: limitsRecord(input.providerLimits),
    agentProviderOverrides: stringRecord(input.agentProviderOverrides, "agentProviderOverrides"),
    agentModelOverrides: stringRecord(input.agentModelOverrides, "agentModelOverrides"),
    queueTimeoutMs: nullableNonNegativeInteger(input.queueTimeoutMs, "queueTimeoutMs", DEFAULT_CONFIG.queueTimeoutMs),
    staleLeaseMs: nonNegativeInteger(input.staleLeaseMs, "staleLeaseMs", DEFAULT_CONFIG.staleLeaseMs),
  }
}

export async function loadConfig(directory: string): Promise<ProviderConcurrencyConfig> {
  const path = join(directory, "opencode.concurrency.json")
  let raw: string
  try {
    raw = await readFile(path, "utf8")
  } catch (error) {
    if (isRecord(error) && error.code === "ENOENT") return { ...DEFAULT_CONFIG }
    throw error
  }

  try {
    return parseConfig(JSON.parse(raw))
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    throw new Error(`Invalid ${path}: ${message}`)
  }
}

function taskAgent(args: unknown): string | null {
  if (!isRecord(args)) return null
  for (const field of ["subagent_type", "agent", "subagent", "agentName"]) {
    const value = args[field]
    if (typeof value === "string" && value.trim() !== "") return value.trim()
  }
  return null
}

function providerFromModel(model: string): string | null {
  const trimmed = model.trim()
  const slash = trimmed.indexOf("/")
  if (slash <= 0) return null
  return normalizeProvider(trimmed.slice(0, slash))
}

export function resolveProvider(args: unknown, config: ProviderConcurrencyConfig): string | null {
  if (!isRecord(args)) return null

  for (const field of ["model", "subagent_model"]) {
    const value = args[field]
    if (typeof value === "string") {
      const provider = providerFromModel(value)
      if (provider) return provider
    }
  }

  const agent = taskAgent(args)
  if (agent) {
    const modelOverride = config.agentModelOverrides[agent]
    const providerFromOverride = modelOverride ? providerFromModel(modelOverride) : null
    if (providerFromOverride) return providerFromOverride

    const providerOverride = config.agentProviderOverrides[agent]
    if (providerOverride) return normalizeProvider(providerOverride)
  }

  return null
}

function leaseKey(input: { sessionID: string; callID: string }): string {
  return `${input.sessionID}:${input.callID}`
}

function activeSet(state: State, provider: string): Set<string> {
  let active = state.activeByProvider.get(provider)
  if (!active) {
    active = new Set()
    state.activeByProvider.set(provider, active)
  }
  return active
}

function queue(state: State, provider: string): Waiter[] {
  let waiters = state.queues.get(provider)
  if (!waiters) {
    waiters = []
    state.queues.set(provider, waiters)
  }
  return waiters
}

function cleanupStaleLeases(state: State, provider: string, now = Date.now()): void {
  if (state.config.staleLeaseMs === 0) return
  const active = state.activeByProvider.get(provider)
  if (!active) return

  for (const key of active) {
    const lease = state.leases.get(key)
    if (lease && now - lease.acquiredAt > state.config.staleLeaseMs) {
      active.delete(key)
      state.leases.delete(key)
      debug(state.config, `released stale lease ${key} for ${provider}`)
    }
  }
}

function acquireNow(state: State, provider: string, key: string): void {
  activeSet(state, provider).add(key)
  state.leases.set(key, { key, provider, acquiredAt: Date.now() })
}

function drainQueue(state: State, provider: string): void {
  const limit = state.config.providerLimits?.[provider]
  if (!limit) return

  cleanupStaleLeases(state, provider)
  const active = activeSet(state, provider)
  const waiters = queue(state, provider)
  while (active.size < limit && waiters.length > 0) {
    const waiter = waiters.shift()!
    if (waiter.timeout) clearTimeout(waiter.timeout)
    acquireNow(state, provider, waiter.key)
    waiter.resolve()
  }
}

export async function acquireLease(state: State, provider: string, key: string): Promise<void> {
  const limit = state.config.providerLimits?.[provider]
  if (!state.config.enabled || !limit) return

  cleanupStaleLeases(state, provider)
  if (activeSet(state, provider).size < limit) {
    acquireNow(state, provider, key)
    return
  }

  if (state.config.mode === "reject") {
    throw new Error(`Provider ${provider} concurrency limit reached (${limit})`)
  }

  await new Promise<void>((resolve, reject) => {
    const waiters = queue(state, provider)
    const waiter: Waiter = { key, provider, resolve, reject, timeout: null }
    if (state.config.queueTimeoutMs !== null && state.config.queueTimeoutMs > 0) {
      waiter.timeout = setTimeout(() => {
        const index = waiters.indexOf(waiter)
        if (index >= 0) waiters.splice(index, 1)
        reject(new Error(`Timed out waiting for provider ${provider} concurrency slot`))
      }, state.config.queueTimeoutMs)
    }
    waiters.push(waiter)
  })
}

export function releaseLease(state: State, key: string): void {
  const lease = state.leases.get(key)
  if (!lease) {
    debug(state.config, `missing lease for ${key}`)
    return
  }

  state.leases.delete(key)
  state.activeByProvider.get(lease.provider)?.delete(key)
  drainQueue(state, lease.provider)
}

export function createState(config: ProviderConcurrencyConfig): State {
  return {
    config,
    leases: new Map(),
    activeByProvider: new Map(),
    queues: new Map(),
  }
}

function debug(config: ProviderConcurrencyConfig, message: string): void {
  if (config.debug) console.warn(`[provider-concurrency] ${message}`)
}

export default (async ({ directory }) => {
  const state = createState(await loadConfig(directory))

  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "task") return
      const provider = resolveProvider(output.args, state.config)
      if (!provider) return
      await acquireLease(state, provider, leaseKey(input))
    },
    "tool.execute.after": async (input) => {
      if (input.tool !== "task") return
      releaseLease(state, leaseKey(input))
    },
  }
}) satisfies Plugin
