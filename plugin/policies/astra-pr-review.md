# Project policy: Astra High PR review

This owner-selected profile applies to PR-bound changes in hStack. It is an
explicit project addition to pstack, not an upstream default.
It is currently suspended: this repository's AGENTS.md does not activate it, and
it applies only after an owner explicitly re-activates or opts into it. Installing
hStack in another project does not activate this profile. Consumer projects use their own policy
and the pinned core defaults unless their owner explicitly opts into this one.

Before publication, obtain two fresh independent GPT-Astra reviewers at High effort
against the exact final candidate commit. Give both seats the same intent, diff,
rubric and supporting source. Each seat returns findings before the coordinator
adjudicates them. A same-model panel provides process independence, not model
family diversity. Generic interrogate keeps its three-seat `inherit-parent` defaults
or the explicitly configured list; this profile does not rewrite that list.

Record base/head, actual invocation, requested and host-confirmed model/effort,
verdict, findings, adjudications, checks and access limits. A tool accepting a
launch is not evidence that review completed or backend settings were attested.
If Astra High is unavailable, report the required review blocked. Do not silently
substitute another model. After fixes, run affected and package checks, commit,
then obtain fresh review of the new exact head. Older review cannot cover edits.

Opening a PR retains the pinned ready-PR contract. Publication, push, merge and
release each require current owner authority. Prepare a PR-ready body locally
when publication is outside scope. Do not create a draft as an implicit fallback.
