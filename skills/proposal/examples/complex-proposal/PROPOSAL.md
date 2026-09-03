---
title: "Rotate service signing keys without downtime"
slug: "rotate-service-signing-keys-without-downtime"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: "responsible engineer"
source-documents:
  - "design/current-key-lifecycle.md"
---

# Rotate service signing keys without downtime

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Security and Reliability](#security-and-reliability)
  - [Security boundary](#security-boundary)
  - [Performance and capacity](#performance-and-capacity)
  - [Migration and rollback](#migration-and-rollback)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

The authentication service will support two active public verification keys during a
bounded rotation window while signing new tokens with one primary private key. The
change affects key storage, token headers, verifier caches, rollout sequencing, and
rotation observability without changing token claims.

## Technical Rationale

Immediate replacement creates a failure window for tokens signed before cache refresh.
A bounded overlap preserves verification during propagation while keeping one signing
authority. The invariant is that private keys never leave the signing service and every
accepted token identifies a configured public key by `kid`.

The overlap increases the number of verification keys and extends exposure if an old
key is compromised. The service therefore limits overlap duration, records key state,
and supports immediate revocation independent of normal rotation.

## Questions

- Assumption: Verifier caches can refresh within the configured 15-minute overlap.
- Evidence Gap: Peak refresh latency across every regional verifier has not been
  measured; rollout remains reviewable because a canary observation gates promotion.
- Open Question: None.

## Security and Reliability

### Security boundary

Only the signing service reads private key material. Verifiers receive public keys and
reject unknown, revoked, expired, or algorithm-mismatched `kid` values. Audit records
must identify key state changes without logging private material.

### Performance and capacity

Verifier lookup remains constant-time by `kid`. The public-key set is bounded to the
primary key, one retiring key, and emergency recovery material; unbounded history is
not served. Cache refresh must not block requests using an already cached valid key.

### Migration and rollback

Rollout proceeds through dual-verification, primary-signing switch, old-key retirement,
and deletion after token expiry. Rollback restores the prior primary while both public
keys remain available. Emergency revocation overrides overlap and may invalidate
outstanding tokens; operators must observe that consequence explicitly.

### Failure modes

- **Unknown `kid`:** Reject the token and increment a regional diagnostic counter.
- **Refresh failure:** Continue verifying cached valid keys, alert, and block retirement.
- **Primary signing failure:** Stop issuance rather than sign with an untracked key.
- **Premature retirement:** Restore the retiring public key before retrying rollout.

## Options Considered

### Replace the key immediately

- **Differentiator:** Only one public key exists at a time.
- **Consequence:** Tokens issued before verifier refresh can fail across regions.
- **Disposition:** Rejected because it violates continuous verification.

### Use a bounded dual-key window

- **Differentiator:** One key signs while two public keys verify temporarily.
- **Consequence:** Rotation tolerates propagation delay at the cost of bounded overlap.
- **Disposition:** Selected because controls limit exposure and preserve availability.

### Serve every historical public key

- **Differentiator:** Old tokens remain verifiable indefinitely.
- **Consequence:** Key-set growth and exposure are unbounded.
- **Disposition:** Rejected because retention exceeds token lifetime and rollback needs.

## Implementation Details

### Key registry — model primary, retiring, and revoked states

- **Change:** Persist key identity, algorithm, public material, state, activation time,
  and retirement deadline.
- **Invariant:** At most one private key is primary and private material remains inside
  the signing boundary.
- **Compatibility and migration:** Existing key becomes primary; the new state fields
  are populated before dual-key serving begins.
- **Failure behavior:** Invalid transitions are rejected atomically.
- **Verification dependency:** State-transition and persistence tests cover rollback.

### Token issuer — emit the primary key identity

- **Change:** Sign with the primary key and emit its `kid` in every token header.
- **Invariant:** Claims and token lifetime remain compatible.
- **Failure behavior:** Missing primary material stops issuance and emits an alert.
- **Verification dependency:** Golden-token tests assert headers and signatures.

### Verifier cache — accept the bounded public-key set

- **Change:** Refresh key states asynchronously and select public keys by `kid`.
- **Invariant:** Unknown or revoked identities fail closed.
- **Compatibility and migration:** Previously issued tokens verify during bounded
  overlap.
- **Failure behavior:** Refresh failure preserves cached valid keys but blocks key
  retirement.
- **Verification dependency:** Regional latency, stale-cache, revocation, and load tests
  cover the path.

### Rotation controller — gate retirement on observations

- **Change:** Advance key state only after verifier refresh and issuance metrics meet
  the rollout thresholds.
- **Invariant:** Retirement never precedes maximum token expiry plus safety margin.
- **Compatibility and migration:** Rollback restores the previous primary before
  deleting any key.
- **Failure behavior:** Missing telemetry pauses the transition.
- **Verification dependency:** A staged integration test injects refresh and telemetry
  failures.

## Verification Criteria

- Tokens issued before and after the signing switch verify throughout normal rotation.
- Unknown, revoked, expired, and algorithm-mismatched keys fail closed with stable
  diagnostics.
- Peak verification latency remains within the existing service budget under two keys.
- A failed cache refresh blocks retirement while cached valid tokens continue to verify.
- Rollback restores the previous primary without deleting required public material.
- Audit inspection shows every state transition and no private key material.

## Sources

- [Current key lifecycle](./design/current-key-lifecycle.md)
