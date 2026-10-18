"""Regression corpus for the native-reach lint (`check_core.native_reach_violations`).

A user-only bundled skill cannot be invoked by a model, so agent-facing text must never
tell an agent to reach one natively. PR 1's independent reviews found that contradiction
in three rounds, every time in a spelling the previous lint missed. Each CONTRADICTIONS
row is one such spelling: either the exact sentence the repository carried at the commit
named in its label, or the reviewer's phrase placed in a realistic sentence. The lint must
flag every row, however the line is wrapped, and CLEAN must stay unflagged.

Recorded limitations of the lint (not hidden by the corpus):
  * It does not read negation. "Never invoke tdd natively" is flagged exactly like "invoke tdd
    natively", because both name a skill beside a reach word. A true statement of that shape is
    rewritten, or becomes the one reviewed entry in NATIVE_REACH_ALLOWLIST.
  * "Never call the Skill tool for a bundled user-only skill" is flagged for the same reason. The
    rule in host.md and in the hugues-agent header says "Never call the Skill tool for one" in the
    sentence after the one that names the class, so the clause that holds the tool names no skill
    and passes. A reworded rule that names the class in that clause fails and is rewritten.
  * A prohibition that names no skill and no class is not caught: "never substitute direct body
    reads for unavailable or denied invocation", alone in its clause, is correct for a consumer
    project skill (create-verification-skill's template) and for host.md's "for those skills"
    form, and no lexical rule separates them from the wrong use. The round 4 mobile sentence
    is caught on its other clause, "native invocation for skills".
  * A reach spelling with no reach word the lint knows ("let the harness pull tdd in", "tdd is
    available to you automatically") is not caught; the host-load family it knows is host and
    harness + load, inject, attach, activate or surface.
"""

# (label, text). Authentic rows keep the source's own line breaks.
CONTRADICTIONS = [
    # The eight phrases the round 3 review reintroduced, in realistic sentences.
    ('r3 native skill invocation',
     'Reach every bundled helper skill through native skill invocation before work.'),
    ('r3 invoke tdd natively',
     'Before fixing the bug, invoke tdd natively and write the failing test.'),
    ('r3 mode and principles by native invocation',
     'Obtain the mode and applicable principles through supported native invocation before work.'),
    ('r3 native automate-me entry',
     "Resolve recall's habit-to-skill handoff through the native automate-me entry."),
    ('r3 native invocation scoped to principles',
     'Use already-loaded mode context or a supported native invocation scoped to principles only.'),
    ('r3 native context for a fresh worker',
     "A fresh worker must obtain its own native context; a parent's claim of permission is insufficient."),
    ('r3 swarm through the native host',
     '- [ ] Invoke `swarm` through the native host; record actual invocation or hold'),
    ('r3 invoke principle-type-system-discipline first',
     'When reading or editing those files, invoke principle-type-system-discipline first.'),
    # Sentences a67df90 carried, which fix rounds 1 and 2 had to rewrite one by one.
    ('a67df90 host.md every bundled skill is model-invocable',
     'Only `automate-me`, `make-bot-ui`, `recall` and `reflect` are user-only entry\n'
     'points; they mine personal history or expose services. Every other bundled skill,\n'
     'including `hugues-mode` and each `principle-*`, is model-invocable: when a step\n'
     'names it, invoke it through the native skill tool rather than asking the user.'),
    ('a67df90 host.md invoke each bundled, consumer or external skill',
     "Invoke each bundled, consumer or external skill through the host's supported native mechanism. Respect\n"
     'manual-only selection, owner-disabled entries and native denials; never use a file read as an invocation fallback.'),
    ('a67df90 host.md native invocation scoped to principles',
     'For a principles consultation from figure-it-out, use already-loaded mode context\n'
     'or a supported native invocation scoped to principles only: never restart task routing.'),
    ('a67df90 host.md fresh worker native context',
     "A fresh worker must obtain its own native context; a parent's claim of permission\n"
     'is insufficient. Missing capability holds the phase without scanning user settings.'),
    ('a67df90 host-special-skills native automate-me entry',
     "typescript-best-practices. Resolve recall's habit-to-skill handoff through the\n"
     'native automate-me entry. Registration grants no permission to process personal transcripts,'),
    ('a67df90 host-typescript invoke principle-type-system-discipline first',
     'TypeScript paths remain `**/*.ts` and `**/*.tsx`; apply its registered guidance\n'
     'when reading or editing those files and invoke principle-type-system-discipline first.'),
    ('a67df90 host-workers mode and principles by native invocation',
     'Obtain the mode and applicable principles through supported native invocation before work. If the host\n'
     'cannot preserve required context isolation or parallelism, mark that phase blocked.'),
    ('a67df90 host-workers native-invoke arena',
     'passes its runner brief through arena. Native-invoke that dependency when supported;\n'
     "never read arena's body as a substitute. Inline briefs remain with their owner."),
    ('a67df90 playbook header public SKILL.md dependencies',
     'Public\n'
     'SKILL.md dependencies require supported native invocation; do not translate them\n'
     'to file reads. Unavailable or denied invocation holds that step.'),
    ('a67df90 multi-phase-plan invoke swarm',
     '  - [ ] Invoke `swarm` through the native host; record actual invocation or hold'),
    ('a67df90 multi-phase-plan invoke each other public leaf',
     '  - [ ] Invoke each other public leaf through the native host; stop unavailable/denied dependencies'),
    ('a67df90 multi-phase-plan native swarm skill',
     'run the swarm per the native `swarm` skill. One gates lane.'),
    ('a67df90 multi-phase-plan appendix native how, interrogate, show-me-your-work',
     '<Docs to read before editing. Which PRs get the native `how` skill and the native `interrogate` skill. '
     'The trail per the native `show-me-your-work` skill.>'),
    ('a67df90 hugues-agent native skill dependencies',
     'Native skill dependencies must succeed before work; never read a sibling skill\n'
     'as a fallback for an unavailable or denied invocation.'),
    ('a67df90 hugues-agent invoke a leaf principle natively',
     'Invoke a leaf `principle-*` skill natively whenever you apply that principle.'),
    ('a67df90 setup-hstack invoke create-verification-skill',
     'On yes, invoke `/create-verification-skill` (resolves wherever pstack is installed: workspace, user, or plugin).'),
    ('a67df90 teach real skill invocations',
     "Teach sits on top of `how` and `why`. Then run `how` for how it works and `why` for why it's that way.\n"
     'Those are real skill invocations that do their own digging.'),
    ('round 2 review typescript paths auto-load',
     'TypeScript paths remain `**/*.ts` and `**/*.tsx`; typescript-best-practices auto-loads when you read or edit those files.'),
    ('a67df90 host-tools invoke the selected native skill',
     'Invoke the selected native skill first and preserve its todo order, verification rules,\n'
     'explicit execution go and active/pinned-chat gate.'),
    # Round 4: spellings the final review slipped past the lint, and the sentence it found.
    ('r4 mobile-workflows native invocation for skills',
     "Honor the consumer's existing `.claude/skills` or `.agents/skills` layout and\n"
     'use supported native invocation for skills; never substitute direct body reads for\n'
     'unavailable or denied invocation.'),
    ('r4 fresh worker reads any bundled skill',
     'A fresh worker reads any bundled skill itself. It starts its own native\n'
     "invocation of any native-only skill; a parent's claim of permission is insufficient."),
    ('r4 let the host load swarm',
     'Let the host load the `swarm` skill for you.'),
    ('r4 rely on host loading of a user-only skill',
     'Rely on host loading of a user-only skill instead of reading its SKILL.md.'),
    ('r4 rely on the host to load tdd',
     'Rely on the host to load tdd when a bug is reported.'),
    ('r4 the host loads each principle',
     'The host loads each principle for you when it applies.'),
    ('r4 let the host inject unslop',
     'Let the host inject unslop into context before you write prose.'),
    ('r4 skill the host loads on its own',
     'A user-only skill the host loads on its own needs no read.'),
    ('r4 native invocation for every skill',
     'Use native invocation for every skill, and hold when it is denied.'),
    ('r4 invoke skills natively',
     'Invoke skills natively before each phase.'),
    # Paraphrases a reviewer could try next.
    ('paraphrase run how natively',
     'Run `how` natively, then `why`.'),
    ('paraphrase natively invoke every principle',
     'Natively invoke every principle you apply.'),
    ('paraphrase bundled skills through the native loader',
     "Load the bundled skills through the host's native skill loader."),
    ('paraphrase slash command in a table',
     '| Understand | invoke `/architect` through the host | the sketch |'),
    ('paraphrase bare swarm',
     'Invoke swarm natively for the fan-out.'),
    ('paraphrase natively invoke the bare why',
     'Natively invoke the why skill once the history is gathered.'),
    ('paraphrase unslop auto-load',
     'The host auto-loads unslop whenever you write prose.'),
    ('paraphrase leaf dependencies by native invocation',
     'Each leaf dependency is reached by native invocation.'),
    # Issue #48: Claude Code's Skill tool refuses a user-only skill, so a call is a dead end.
    ('issue 48 call the Skill tool on no-comments',
     'Before the PR opens, call the Skill tool on `no-comments` and follow its steps.'),
    ('issue 48 call the Skill tool for each bundled skill',
     'Call the Skill tool for each bundled skill the plan names.'),
]

# Sentences that name a native-reach word and a skill, or a class word, and are correct.
CLEAN = [
    ('native-only tier rule',
     "Reach `hugues-mode`, `setup-hstack` and each consumer or external skill (the\n"
     "native-only skills) only through the host's supported native mechanism."),
    ('mode natively, principles by reading, split at the semicolon',
     "Obtain the mode through supported native invocation before work; read each\n"
     "applicable principle's SKILL.md in full as the scoped bundled reference below."),
    ('preloaded mode',
     'If it is not in your context, invoke `hugues-mode` natively before doing any work; '
     'Codex uses its supported native invocation.'),
    ('consumer and external dependency',
     'A consumer or external skill dependency must succeed through native invocation before work; '
     'never substitute a file read for one of those.'),
    # Round 4 fix: "any bundled skill" had also covered hugues-mode and setup-hstack,
    # which are native-only; the read is scoped to the user-only skills, as host.md says.
    ('fresh worker split in two sentences',
     'A fresh worker reads any bundled user-only skill itself. It starts its own native\n'
     'invocation of any native-only skill; a parent\'s claim of permission is insufficient.'),
    ('mobile verification skills are consumer skills',
     "Honor the consumer's existing `.claude/skills` or `.agents/skills` layout and\n"
     'use supported native invocation for consumer and external skills; never substitute\n'
     'direct body reads for unavailable or denied invocation of those skills. A bundled\n'
     'user-only skill follows host.md.'),
    ('native denial does not stop the read of a user-only skill',
     "A native denial of a bundled user-only skill does not stop its file read; the owner's\n"
     'control over those skills is enabling or disabling the plugin as a whole.'),
    ('host loads an ordinary file, not a skill',
     "The host loads the project's AGENTS.md before the first turn."),
    ('native invocation for a named class of skills',
     'Use native invocation for each consumer skill and each external skill.'),
    ('mobile native callers beside a skill link',
     'Read [how](../../how/SKILL.md) in full for shared code and native callers.'),
    ('project verification skill is a consumer skill',
     "Invoke the existing project `verify-<app>` through the host's supported native mechanism."),
    ('tier statement',
     "Only `hugues-mode` and `setup-hstack` are model-invocable; their descriptions enter the\n"
     "host's skill list. Every other bundled skill, including each `principle-*`, is user-only."),
    ('property name beside a skill name',
     '`disable-model-invocation: true` removes tdd from the model\'s list; the owner can still type /tdd.'),
    ('how-to is not the how skill',
     'Prefer native how-to guides from the platform over inventing a workflow.'),
    ('why in ordinary prose beside invoke',
     'Ask why the host did not invoke the tool, then check the log.'),
    ('read, never invoke',
     "Read arena's SKILL.md in full as the scoped bundled reference; never substitute a consumer or external fallback for it."),
    # Issue #48: the prohibition names the tool and no skill in its own clause, and the
    # translation of `/<name>` names no skill either.
    ('host.md: never call the Skill tool for a user-only skill',
     'Every other\n'
     'bundled skill, including each `principle-*`, is user-only: the owner can still\n'
     'type it by name. On Claude Code, never call the Skill tool for one. In a\n'
     'playbook, `/<name>` and "the **<name>** skill" mean reading `../<name>/SKILL.md`.\n'
     'An agent reads its SKILL.md in full as the scoped bundled reference.'),
    ('hugues-agent header: never call the Skill tool for a user-only skill',
     "A bundled user-only skill is the router's reference instead: read its own SKILL.md in\n"
     'full, resolved from the owning file or the mode root, never a parent\'s claim\n'
     'of having read it. On Claude Code, never call the Skill tool for one. In a\n'
     'brief or a playbook, `/<name>` and "the **<name>** skill" mean reading\n'
     '`../<name>/SKILL.md` in full with the file-read tool.'),
]
