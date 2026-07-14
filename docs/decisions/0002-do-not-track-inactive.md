# ADR-0002 — Time in INACTIVE is not tracked

**Status:** Accepted
**Date:** 2026-07-13

## Context

The project thesis is "measure what actually happened". Taken literally, that would mean
recording idle time too. However idle time is not what we are concerned with here.

## Options

- Gap-free recording of the whole day
- Active phases only

## Decision

Active phases only. INACTIVE produces no data.

## Consequences

Inactive times can only be induced by being the negative of active times. However with the Schema C from ADR-0004 the quetion is sufficiently resolved.
