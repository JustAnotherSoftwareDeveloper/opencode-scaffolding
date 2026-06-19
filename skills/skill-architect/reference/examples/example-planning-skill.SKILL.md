<!-- This is a worked example for demonstration. It follows the single-domain template — no Architecture Overview, Test Strategy, External Services, or Framework & Conventions sections. See ../planning-reference.md for authoring guidance. -->
---
name: example-payment-domain-planning
description: "Use when planning or architecting the payment processing domain."
class: planning
---

# Example Payment Domain — Domain Planning Reference

This example demonstrates the single-domain template structure for the payment processing bounded context.
See the template at `../../../skill-writer/templates/planning.SKILL.template.md` and the reference at `../planning-reference.md`.

## When to Use

- Load during a new payment method integration (e.g., adding a new processor or payment scheme) to map domain boundaries, event contracts, and data ownership.
- Load when reviewing a pull request that touches payment domain types (`pkg/domain/payment/`), settlement logic, or refund flows.
- Load during onboarding to understand how the payment domain relates to adjacent domains (order, billing, fraud) without needing the full platform picture.
- Load before writing a payment-domain ADR to ensure consistency with existing decisions around idempotency, retry, and reconciliation.

## Decision Records

- `docs/adr/001-event-bus.md`: Chose RabbitMQ over Kafka for payment events. Rationale: lower operational complexity for sub-10k msg/s throughput. Trade-off: replay and retention are harder, but payment events are short-lived and do not require long-term replay.
- `docs/adr/002-payment-idempotency.md`: Every payment mutation (capture, refund, void) uses an idempotency key derived from the order ID and operation type. Rationale: at-least-once message delivery means duplicate events are guaranteed; idempotency prevents double-charges. Trade-off: every payment handler must check the idempotency store before executing.
- `docs/adr/005-settlement-model.md`: Adopted a capture-on-shipment model (authorize at checkout, capture when inventory confirms shipment). Rationale: avoids charging the customer before the order is fulfilled. Trade-off: introduces a window where authorized funds are held but not yet captured; requires a nightly reconciliation job to release stale authorizations.
- `docs/adr/006-refund-workflow.md`: Refunds are processed asynchronously via a dedicated `RefundRequested` event rather than a synchronous API call. Rationale: decouples the storefront from processor availability and allows retry with backoff. Trade-off: refund confirmation is eventual (typically sub-30s).

## Constraints & Assumptions

- Payment domain owns the full payment lifecycle — authorization, capture, refund, void, and settlement reconciliation — but does **not** own invoicing, billing, or subscription management. Those are separate domains with their own planning references.
- All payment mutations must be idempotent. The idempotency store (`pkg/domain/payment/idempotency.go`) uses PostgreSQL with a TTL of 24 hours. Callers that do not supply an idempotency key are rejected.
- Stripe is the sole payment processor in production. Processor-specific logic is isolated behind the `PaymentProcessor` interface in `pkg/domain/payment/gateway.go`. Adding a new processor requires implementing that interface and adding a gateway test, but does not change domain event contracts.
- Refunds are limited to 120 days from the original charge date (Stripe constraint). The domain enforces this at the API layer and returns a business-error response for out-of-window requests.
- Message delivery is at-least-once. All payment event consumers (including the refund handler and the reconciliation job) must be idempotent on the event `id` field.
- Cross-domain sagas (e.g., cancel-order → void-payment) are coordinated by the Order domain via compensating events. The payment domain does not initiate sagas.

## Verification Criteria

- Every payment method type listed in the domain model has a corresponding processor test in `pkg/domain/payment/gateway_test.go`.
- Each payment event type (`PaymentAuthorized`, `PaymentCaptured`, `PaymentRefunded`, `PaymentVoided`) has a protobuf schema in `pkg/events/` and a consumer idempotency test.
- The reconciliation job (`cmd/payment-reconciliation/`) runs successfully against a staging Stripe account with test-mode transaction data before each release.
- No planning document, ADR, or test fixture references a live Stripe API key, database credential, or internal hostname verbatim.