---
name: why
description: "Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Returns a cited read on decisions and tradeoffs. Use how for runtime behavior."
disable-model-invocation: true
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Why

Answer from the record, not the code: read the commits and PR discussions that introduced the target and each later change, and other sources if the trail is thin. Cite what the authors wrote, mark your own inferences as inferences, and say what the record does not answer.
