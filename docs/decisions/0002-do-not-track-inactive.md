# ADR-0002 — Time in INACTIVE is not tracked

**Status:** Accepted
**Date:** 2026-07-13

## Context

The project thesis is "measure what actually happened". Taken literally, that would mean
recording idle time too. *(TODO: name the apparent contradiction explicitly and resolve
it — why is not tracking idle time still honest?)*

## Options

- Gap-free recording of the whole day
- Active phases only

## Decision

Active phases only. INACTIVE produces no data.

## Consequences

- *(TODO)*
