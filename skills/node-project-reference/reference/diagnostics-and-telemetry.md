# Diagnostics And Telemetry

## Scope

This page answers which diagnostic surface produced an output, what that surface contains, and whether the output is sensitive or part of a telemetry pipeline. It covers TypeScript source, configuration, declarations, tests, quality diagnostics, and package artifacts in Node.js or Bun projects. Node.js and Bun runtime mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer.

The scope is TypeScript-only. A JavaScript-only request is out of scope, and `allowJs`, `checkJs`, and JSDoc typing of `.js` files are excluded from this reference. The page describes passive mechanics and interpretation; it chooses no logging stack, log schema, telemetry vendor, or observability requirement, and it does not read, configure, instrument, or validate a project.

Node.js claims below come from the released v26.13.0 Console, Diagnostics Channel, Asynchronous Context Tracking, and Diagnostic Report API pages. Bun documentation is rolling and its compatibility page targets Node.js v26. OpenTelemetry claims name their specification, language-status, release-tagged package, or release-note source. Each claim stays with the runtime, version, mode, and evidence type that supports it; Node findings are not generalized to Bun without separate evidence.

## Six Surfaces, Not Synonyms

The words "log," "diagnostic," "context," and "telemetry" cover separate mechanisms. Keep these surfaces distinct before interpreting an output:

- **Console output** is a general output and debugging interface. It routes text to output streams; it does not define a structured log record.
- **Diagnostic channels** are named in-process publish and subscribe topics. A producer publishes a message shape on a channel; a subscriber observes it during publication.
- **Runtime reports** are process-state snapshots, commonly JSON. They answer "what did the process look like when this happened," not "which log record was exported."
- **Async context** is in-process state associated with asynchronous work, such as a request identifier. It is not a wire format or a cross-process contract.
- **Propagation** serializes context into a carrier and extracts it elsewhere, typically across a process or service boundary.
- **Telemetry instrumentation and export** create signal records through an API and SDK and send them to a backend. Instrumentation coverage, context management, and export are separate layers.

A message can appear in more than one surface only when a bridge explicitly copies it. Similar words do not make the surfaces interchangeable.

## Console Output

### Node.js Console

Node's `node:console` is a stable output and debugging API ([Node.js v26.13.0 Console](https://nodejs.org/api/console.html)). The global console routes ordinary log and info calls to `stdout` and error and warning calls to `stderr`; a custom `Console` instance can target supplied writable streams. Node warns that global console calls are not consistently synchronous or asynchronous: behavior depends on the backing stream and process configuration.

The API does not define a structured logging schema. It supplies no stable field set, severity level contract, serialization format, backend contract, or retention rule. A console line is output, not a log record with stable fields.

### Bun Console

Bun documents materially different output mechanics. Its console writes directly to the `stdout` and `stderr` file descriptors and uses its own inspector and formatting, so replacing `process.stdout.write` does not capture console output ([Bun Node.js compatibility](https://bun.com/docs/runtime/nodejs-compat); [Bun Console](https://bun.com/docs/runtime/console)). The compatibility page also states that `console.trace()` writes to `stdout` and the `console.time*()` family writes to `stderr`. That differs from Node's routing, where error and warning output such as `console.error` and `console.trace` goes to `stderr` and ordinary output such as `console.log` and `console.time` goes to `stdout`.

Bun's pages are rolling, and its green and yellow compatibility labels are Bun's own compatibility markers, not Node API stability labels. A Node console capture technique is therefore not evidence about Bun console output, and a Bun capture result is not evidence about Node.

## Diagnostic Channels

### Node.js Channels

`node:diagnostics_channel` is a stable module that provides named in-process publish and subscribe channels ([Node.js v26.13.0 Diagnostics Channel](https://nodejs.org/api/diagnostics_channel.html)). Producers are expected to document channel names and message shapes. Subscribers run synchronously during publication, and a subscriber that throws triggers `uncaughtException` rather than being isolated by the channel.

Stability is not uniform across every API exposed by the module. In the inspected v26.13 documentation, `tracingChannel()` is stable, `boundedChannel()` is experimental, and the built-in channel section is experimental. The module's stable label therefore does not make every built-in channel or every helper stable. A channel is also an in-process surface: it does not serialize a message for another process or service.

### Bun Channels

Bun's compatibility page reports a partial `node:diagnostics_channel` implementation. It lists `channel()`, `subscribe()`, `tracingChannel()`, and some HTTP client, HTTP/2, and datagram channels as implemented, while `boundedChannel()` and several built-in channel families, including `console` and `http.server.*`, are missing. It also says subscribers do not keep a `Channel` alive, so callers should retain a reference ([Bun Node.js compatibility](https://bun.com/docs/runtime/nodejs-compat)).

The page does not establish that every Node subscriber timing or error semantic is identical in Bun, and Bun's compatibility marks are not Node stability labels. A channel name that exists in both runtimes is not, by itself, evidence that the message shape, publication timing, or built-in publisher is the same.

## Runtime Reports And Crash Output

### Node.js Diagnostic Reports

Node diagnostic reports are stable JSON runtime snapshots ([Node.js v26.13.0 Diagnostic Report](https://nodejs.org/api/report.html)). They can be triggered by an unhandled exception, a fatal error, a signal, or a programmatic request. Documented content includes JavaScript and native stacks, heap, runtime, and resource details, and platform information. Environment variables and network-interface details are included by default in the documented report configuration; `--report-exclude-env` and `--report-exclude-network` provide exclusions.

Report content and exclusion controls are runtime-specific. The report page includes a historical sample generated by Node v12, so do not treat that sample's exact shape as the v26 schema. A diagnostic report is sensitive diagnostic output, not an ordinary log record, and it is not by itself a telemetry-export pipeline.

### Bun Reports And Crash Output

Bun's Node.js compatibility page says `process.report.writeReport()` writes nothing ([Bun Node.js compatibility](https://bun.com/docs/runtime/nodejs-compat)). Separately, Bun's compiled-program debugging page describes a crash report printed to `stderr` for a process that crashes, including the program's active functions and source locations ([Bun Test And Debug A Compiled Program](https://bun.com/docs/compiler/debugging)).

These are different mechanisms. A no-op `process.report` compatibility method does not prove that Bun lacks every diagnostic or report surface, and the compiled-program crash report is not documented as Node's JSON report format. Bun's page scopes the crash report to compiled programs and calls ahead-of-time compilation experimental. Do not treat Node report content, exclusions, or JSON shape as a Bun contract.

## Async Context, Context Management, And Propagation

### In-Process Context

Node's asynchronous context tracking and `AsyncLocalStorage` are stable ([Node.js v26.13.0 Asynchronous Context Tracking](https://nodejs.org/api/async_context.html)). `run()` scopes a store to the callback and the asynchronous work created within it. Node labels `enterWith()` and `disable()` experimental and warns that `enterWith()` can affect later handlers in the same synchronous execution; `run()` is the documented scoped form. The documentation describes rare context-loss situations, especially around callback-based APIs and custom thenables, and identifies `AsyncResource` as a context-association tool for such cases.

Bun reports `AsyncLocalStorage` and `AsyncResource` as implemented, but several lower-level `async_hooks` APIs are stubs and async IDs are always zero. Bun's compatibility page explicitly says `AsyncLocalStorage` context is not propagated into `MessagePort`, `BroadcastChannel`, or `Worker` events ([Bun Node.js compatibility](https://bun.com/docs/runtime/nodejs-compat)). This is a runtime-specific boundary, not evidence that all Bun async context is absent.

### OpenTelemetry Layers

OpenTelemetry separates an in-process context manager from propagation. A configured context manager makes active context available to code across supported asynchronous work; without a configured manager, the JavaScript Context page says `context.active()` returns `ROOT_CONTEXT` ([OpenTelemetry JavaScript Context](https://opentelemetry.io/docs/languages/js/context/)). Propagation serializes context into a carrier and extracts it elsewhere, such as request headers crossing a process or service boundary ([OpenTelemetry JavaScript Propagation](https://opentelemetry.io/docs/languages/js/propagation/)). Applicable instrumentation can propagate context automatically; manual `inject` and `extract` operate on carriers where automatic support does not apply.

The current upstream context-manager README describes `AsyncLocalStorageContextManager`, whose implementation uses `AsyncLocalStorage` ([OpenTelemetry Context Async Hooks README](https://raw.githubusercontent.com/open-telemetry/opentelemetry-js/main/packages/opentelemetry-context-async-hooks/README.md)). The OpenTelemetry API, the SDK, the context manager, propagation, instrumentation packages, and exporters are separate layers with separate versions and coverage.

### Instrumentation And Logs

The OpenTelemetry JavaScript instrumentation guide distinguishes application instrumentation, where the application initializes an SDK and uses the API, from library instrumentation, where a library depends on the API and emits only when the application supplies an SDK ([OpenTelemetry JavaScript Instrumentation](https://opentelemetry.io/docs/languages/js/instrumentation/)). SDK initialization must occur before other modules load for libraries to receive the configured provider; late or missing initialization leaves no-op API behavior. Instrumentation packages cover particular libraries and runtimes, not every library or transport. Traces, metrics, and logs are separate signals with separate package and status scopes; a package version or maturity label for one does not transfer to another.

The Logs SDK supports manual log-record creation and export but does not automatically instrument known libraries or host-environment logs out of the box ([OpenTelemetry Logs SDK README](https://raw.githubusercontent.com/open-telemetry/opentelemetry-js/main/packages/sdk-logs/README.md)). A separate maintained contrib package documents Node.js console instrumentation that turns selected console calls into OpenTelemetry log records and associates them with an active span; it documents Node.js `>=22.15.0` and guards against console and exporter recursion, and it cautions against combining console instrumentation with console exporters in production ([OpenTelemetry Console Instrumentation README](https://raw.githubusercontent.com/open-telemetry/opentelemetry-js-contrib/main/packages/instrumentation-console/README.md)). That is a specific Node.js package's documented scope, not evidence of Bun support or a required logging stack.

## Two Documented Disagreements Kept Visible

Two documented disagreements remain visible: the OpenTelemetry JavaScript Logs maturity scope mismatch remains unresolved, while the context-manager class name has a bounded, release-tagged resolution.

### OpenTelemetry JavaScript Logs Maturity

The OpenTelemetry Logs API specification and the Logs data model each state **Stable** ([OpenTelemetry Logs API](https://opentelemetry.io/docs/specs/otel/logs/api/); [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)). The OpenTelemetry JavaScript language status page states Traces and Metrics **Stable** and Logs **Development** ([OpenTelemetry JavaScript](https://opentelemetry.io/docs/languages/js/)).

These are genuinely different scopes. The specification status describes the cross-language API and data model; the language page describes JavaScript implementation maturity. The mismatch is not resolved by choosing one label for both.

The October 2026 JavaScript SDK 3.x release and migration material adds package-level facts: published `@opentelemetry/sdk-logs@3.0.0` is a stable SDK package, while logs exporters and other listed experimental packages are `0.300.0`; `@opentelemetry/api` `1.10.0` is independently versioned; and the `@opentelemetry/api-logs` API was folded into the core API ([OpenTelemetry JavaScript SDK 3.0](https://opentelemetry.io/blog/2026/otel-js-sdk-3-0/); [OpenTelemetry JavaScript 3.x Migration Guide](https://github.com/open-telemetry/opentelemetry-js/blob/v3.0.0/doc/3.x/migration-guide.md)). Those released package and export facts do not erase the specification-versus-JavaScript-language-status mismatch. A stable data model, a stable SDK package, and an experimental exporter are different claims; no settled maturity label is asserted here for every OpenTelemetry JavaScript logs component.

### Context-Manager Class And Node.js Floor

The OpenTelemetry JavaScript Context website page still shows an `AsyncHooksContextManager` example. That name was a real public export in the bounded `@opentelemetry/context-async-hooks@2.12.0` example: its `src/index.ts` exports both `AsyncHooksContextManager` and `AsyncLocalStorageContextManager`, and its package metadata supports Node `^18.19.0 || >=20.6.0` ([v2.12.0 entrypoint](https://github.com/open-telemetry/opentelemetry-js/blob/v2.12.0/packages/opentelemetry-context-async-hooks/src/index.ts); [v2.12.0 package metadata](https://github.com/open-telemetry/opentelemetry-js/blob/v2.12.0/packages/opentelemetry-context-async-hooks/package.json)).

In the release-tagged `v3.0.0` package, the entrypoint exports only `AsyncLocalStorageContextManager`, and the package metadata requires Node `>=22.15.0` ([v3.0.0 entrypoint](https://github.com/open-telemetry/opentelemetry-js/blob/v3.0.0/packages/opentelemetry-context-async-hooks/src/index.ts); [v3.0.0 package metadata](https://github.com/open-telemetry/opentelemetry-js/blob/v3.0.0/packages/opentelemetry-context-async-hooks/package.json)). The v3.0.0 release notes explicitly remove `AsyncHooksContextManager` ([OpenTelemetry JavaScript v3.0.0 release notes](https://github.com/open-telemetry/opentelemetry-js/releases/tag/v3.0.0)). A merged maintainer change record states that `AsyncLocalStorageContextManager` was already NodeSDK's default in the v2 generation and that the older class was deprecated before removal ([OpenTelemetry JavaScript PR #6298](https://github.com/open-telemetry/opentelemetry-js/pull/6298)).

The bounded outcome is that the old name was a real public export, not a fabricated one, and it was removed in v3. For SDK 3.x, the current usable name is `AsyncLocalStorageContextManager`, qualified to Node `>=22.15.0`. Do not present the removed class as current guidance, and do not treat the website's older example as evidence that the removed class remains available in current 3.x packages.

Do not imply that every consumer explicitly configures a manager. NodeSDK used `AsyncLocalStorageContextManager` by default in the v2 generation. A standalone setup that configures no context manager is a different case; the Context page says `context.active()` returns `ROOT_CONTEXT` without one.

## Worked Contrasts

### Capture Console Output For One Case

The following Node.js helper captures console output for a single case by supplying a custom `Console` with in-memory writable streams. It is scoped to Node v26.13.0 and to the calls routed through that `Console` instance.

```ts
import { Console } from "node:console";
import { Writable } from "node:stream";

function captureConsole(
  run: (console: Console) => void,
): { stdout: string; stderr: string } {
  let stdout = "";
  let stderr = "";
  const sink = (append: (chunk: string) => void): Writable =>
    new Writable({
      write(chunk: Buffer | string, _encoding, callback) {
        append(chunk.toString());
        callback();
      },
    });

  const console = new Console({
    stdout: sink((chunk) => {
      stdout += chunk;
    }),
    stderr: sink((chunk) => {
      stderr += chunk;
    }),
  });

  run(console);
  return { stdout, stderr };
}

const captured = captureConsole((console) => {
  console.log("ready");
  console.error("failed");
});
```

In this Node-scoped case, `console.log` writes to the supplied stdout stream and `console.error` writes to stderr, so the two channels are separated in the result. The helper is illustrative, not a tested cross-runtime utility. It does not capture direct `process.stdout` writes, other `Console` instances, or output produced outside the supplied streams, and Node's sync and async behavior still depends on the backing stream and process configuration.

Do not reuse it as a Bun capture technique. Bun's console writes directly to the file descriptors and uses its own inspector, so replacing `process.stdout.write` does not capture it. Bun also routes `console.trace()` and the `console.time*()` family differently from Node. A Bun capture result must be established for the Bun version and route under test.

### Trace Diagnostic Data Versus Telemetry Export

A diagnostic report and a telemetry event answer different questions. The report is a runtime snapshot; the telemetry event is a selected record sent to a backend. The report can contain environment variables and network-interface details before any export, so identify sensitive content first and forward an allowlist rather than the whole snapshot.

```ts
interface NodeReportSubset {
  header?: { nodejsVersion?: string };
  resourceUsage?: unknown;
  environmentVariables?: Record<string, string>;
  networkInterfaces?: unknown;
}

declare function sendToCollector(payload: string): void;

function reportSummary(report: NodeReportSubset): Record<string, unknown> {
  return {
    event: "diagnostic-report",
    nodeVersion: report.header?.nodejsVersion,
    resourceUsage: report.resourceUsage,
  };
}

// Forwards the whole snapshot, including environment and network data by default.
sendToCollector(JSON.stringify(process.report.getReport()));

// Safer: send an allowlisted summary rather than the whole snapshot.
const report = process.report.getReport() as unknown as NodeReportSubset;
sendToCollector(JSON.stringify(reportSummary(report)));
```

This example is Node-scoped and abbreviates the report shape; report fields and exclusion behavior are version-specific. Node's `--report-exclude-env` and `--report-exclude-network` controls can omit those categories at report generation, and the allowlist is a second, separate choice at export. The example is not a universal sanitization policy: choose the fields the reader's purpose requires, and treat the raw report as sensitive.

The diagnostic report is not itself a telemetry-export pipeline. Sending a summary does not prove that a backend received it, and nothing here promises delivery or a completed flush. Bun's `process.report.writeReport()` writes nothing, while a compiled Bun program's crash report goes to `stderr` in a form that is not Node's JSON; do not route a Bun crash report through a Node report exporter by assumption.

### Propagation With An Instrumented Library Versus A Custom Transport

An instrumented library can carry context across a supported call boundary. A custom transport has no instrumentation, so it needs an explicit injection, and the receiver must still extract the carrier.

```ts
import { context, propagation } from "@opentelemetry/api";

type Carrier = Record<string, string | string[] | undefined>;

interface InstrumentedClient {
  post(path: string, body: string): Promise<void>;
}

interface CustomTransport {
  send(carrier: Carrier, body: string): Promise<void>;
}

async function sendWithInstrumentedClient(
  client: InstrumentedClient,
  body: string,
): Promise<void> {
  // The client's instrumentation decides whether context is carried.
  await client.post("/orders", body);
}

async function sendWithCustomTransport(
  transport: CustomTransport,
  body: string,
): Promise<void> {
  const carrier: Carrier = {};
  propagation.inject(context.active(), carrier);
  await transport.send(carrier, body);
}
```

The instrumented client carries context only where the installed instrumentation supports that client and transport and the configured propagator is active. The custom transport has no automatic support, so `propagation.inject` is required; the receiving side must extract the carrier, and the API package alone does not establish that an SDK, context manager, or propagator is installed. A trace can therefore show context on one hop and not another.

This is not a universal propagation promise. Node documents rare context loss, and Bun documents gaps for `MessagePort`, `BroadcastChannel`, and `Worker` events. Propagation across a process or service boundary is separate from in-process context management, and no instrumentation covers every library or transport.

## Diagnose Unexpected Or Sensitive Output

When an output is missing, duplicated, or unexpectedly sensitive, identify the surface before changing code:

- **Console output.** Record the runtime, version, and capture method. A Node console helper captures only the streams it was given; a Bun console call may bypass a replaced `process.stdout.write` and may route `console.trace()` or `console.time*()` to a different stream.
- **Diagnostic channel.** Record the channel name and the runtime's support for it. Node's built-in channel section and `boundedChannel()` carry experimental labels, and Bun's compatibility page lists missing channels and channel families. Subscribers run synchronously during publication in Node, so a slow or throwing subscriber changes the publishing path.
- **Runtime report or crash output.** Inspect the report before sharing it. Node reports include environment and network-interface data by default and offer exclusion controls; report content is runtime- and version-specific. Bun's `process.report.writeReport()` writes nothing, and a compiled Bun crash report is a different mechanism from Node's JSON report.
- **Telemetry output.** Check each layer: the instrumentation package and its runtime coverage, the context manager, the propagator, the SDK, and the exporter. The Logs SDK alone does not instrument host logs or known libraries. An installed API package does not prove that an SDK or propagator is configured.
- **Context-dependent output.** Check whether the work crosses a callback-based API, a custom thenable, a worker or message event, or a custom transport. A missing context value can come from a documented context-loss case or from a boundary that was never instrumented.

The observable consequence is that a diagnostic report can include sensitive content before any export, and a trace can carry context on one hop while a custom transport carries none. Neither result identifies the other surface's behavior.

## Limits And Version Boundaries

- Node.js claims are bounded to the released v26.13.0 API pages named above. Diagnostic report fields and exclusions are runtime- and version-specific, and the report page's historical v12 sample is not the current schema.
- Bun documentation is rolling and exposes no release baseline on the inspected pages. The compatibility page targets Node.js v26; Bun's compatibility labels are not Node stability labels. Documented Bun behavior is a publisher claim, not an independent runtime test or a compatibility matrix for an uninspected version.
- OpenTelemetry website pages, language status, release-tagged package sources, and release notes update on different schedules. Package versions name their own bounds: `@opentelemetry/context-async-hooks@2.12.0` supports Node `^18.19.0 || >=20.6.0`; `v3.0.0` requires Node `>=22.15.0`; `@opentelemetry/api` `1.10.0` is independently versioned; `@opentelemetry/sdk-logs@3.0.0` is a stable SDK package while listed logs exporters and other experimental packages are `0.300.0`.
- The OpenTelemetry JavaScript Logs maturity scope mismatch remains visible: the Logs API specification and data model say Stable, while the JavaScript language status page says Logs Development. No settled maturity claim is made for every package, exporter, or generation.
- The context-manager class is resolved only within the stated bounds: `AsyncHooksContextManager` was a public export in the bounded 2.12.0 example and was removed in v3; `AsyncLocalStorageContextManager` is the current name for SDK 3.x with its Node `>=22.15.0` floor. This is not a claim that every consumer configures a manager explicitly or that every older package version exports the same symbol.
- No console API here defines a structured log schema. No diagnostic report is a telemetry-export pipeline. No universal propagation or flush guarantee follows: context may be lost at documented boundaries, a transport may be uninstrumented, and an export call does not prove delivery.
- OpenTelemetry sources document Node.js and browser paths; they do not establish supported Bun runtime behavior. Absence of a Bun support statement is not proof of incompatibility.
- No universal security, logging, or observability policy is stated. This page selects no telemetry vendor and prescribes no stack.
- Nothing here selects, prescribes, or assumes Vite; an incidental dependency edge is neither evidence of direct selection nor proof of its absence. Nothing on this page forms an implicit pipeline, and no compatibility promise follows for another runtime, package, or version.
- The repository's deterministic utilities under `scripts/node/` have their own Bun and repository conventions. Those conventions are not ordinary project defaults.

## Ownership And Routing

This page is passive interpretation. Logging and diagnostic design changes that alter production behavior go to `node-project-writer -> reference/change-design-and-validation.md`. Adding, removing, or upgrading telemetry packages and their dependency or environment effects goes to `node-project-dependencies -> reference/evaluation-and-environment-changes.md`. Telemetry backend selection, deployment, retention, and organizational policy are outside this family's owners.

Configuration sources, parsing, validation, and exposure controls are covered in [Configuration Loading And Validation](configuration-loading-and-validation.md). Concurrency, cancellation, and lifecycle behavior is covered in [Concurrency And Lifecycle](concurrency-and-lifecycle.md). No approval, configuration change, instrumentation change, or completion evidence follows from this page.
