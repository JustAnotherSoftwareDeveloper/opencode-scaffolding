# Dependency Direction and Non-Transitivity

## Purpose

State the approved direction for passive context and the boundary against authority
leaks between skill classes.

## Applicability

Applies to operation-to-documentation context, delegated workers, ordinary planning
separation, and inline exact-declaration semantics.

## Non-goals

This document does not load dependencies, inspect a graph, enforce runtime behavior,
or authorize procedures, tools, writes, delegation, or completion.

## Authority source

The authority is the local [class boundary and loading matrix](class-boundary-loading-matrix.md)
and [class boundary rules](class-boundary-rules.md).

## Scope

Documentation is passive context, not an executable dependency. Any further reference
is explicit rather than an automatic recursive or transitive authority chain.
Planning remains separate from ordinary execution, except for passive context in the
scoped planning collector. Inline execution keeps its exact declaration contract.
Passive references cannot authorize another skill, add imperative steps, or transfer
ownership of effects and validation.

## Evidence status

The dependency direction and non-transitive contract are approved. Runtime recursion,
duplicate-load, passive-enforcement, and class-mismatch behavior are not asserted
beyond the repository evidence described by the architecture decision.

## Shared passive-contract verification

This concern is coupled to the indexed scope and contains reference context only.
It grants no execution authority, implicit loading, tool use, file change, delegation,
or completion authority.
