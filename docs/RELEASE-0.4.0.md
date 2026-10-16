# hStack 0.4.0

Version 0.4.0 renames the project from huguesStack to hStack. The display name in prose is hStack. Identifiers, paths, slugs and package names are `hstack`. The rename is breaking: the plugin, its command prefix, the setup skill, the project config folder and the Codex permission profile all change name, so a 0.3.x install, its project config and its program bindings do not carry over as they are. Versions 0.1.0, 0.2.0 and 0.3.0 and their evidence remain unchanged, and keep the old name.

The `hugues-*` skill names (`hugues-mode`, `hugues-agent`, `hugues-help`, `hugues-comment-sicko`) and the GitHub owner `hugues-vnsgn` keep their names. A separate change handles the skill names.

## Breaking renames

| Surface | 0.3.x | 0.4.0 |
|---|---|---|
| Plugin and marketplace name | `hugues-stack` | `hstack` |
| Install id | `hugues-stack@hugues-stack` | `hstack@hstack` |
| Claude Code command prefix | `/hugues-stack:<skill>` | `/hstack:<skill>` |
| Setup skill | `setup-huguesstack` | `setup-hstack` |
| Project config folder | `.huguesstack/` (`models.md`) | `.hstack/` (`models.md`) |
| Codex permission profile | `huguesstack-program` | `hstack-program` |
| Installed payload revision | `huguesstack-native-v1` | `hstack-native-v1` |
| Upstream ledger files | `docs/upstream/huguesStack-dispositions.{csv,json}` | `docs/upstream/hstack-dispositions.{csv,json}` |
| Suggested evidence folder | `~/huguesstack-evidence/<date>-<task>/` | `~/hstack-evidence/<date>-<task>/` |
| Self-hosted proof runner label | `huguesstack-proof` | `hstack-proof` |
| Repository URL | `github.com/hugues-vnsgn/huguesStack` | `github.com/hugues-vnsgn/hstack` |

Temp-dir prefixes, simulator names and bundle ids in the checks follow the same rename. The repository rename happens on GitHub after the merge, and GitHub redirects the old URL.

## Migrate from 0.3.x

1. **Reinstall as `hstack@hstack`.** The old `hugues-stack@hugues-stack` entry does not update in place. Install the renamed plugin, then open a fresh host session. For a one-session check, load the new checkout with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.
2. **Run `/hstack:setup-hstack`** in Claude Code, or `$setup-hstack` in Codex. It writes `.hstack/models.md` and writes only `.hstack/`.
3. **Move `.huguesstack/` to `.hstack/`** in each project that has it, for example `mv .huguesstack .hstack`. Until you move it, a skill or adapter that finds no `.hstack/models.md` but finds `.huguesstack/models.md` reads the legacy file and tells you to move it. Setup never writes or deletes `.huguesstack/`.
4. **Rename the Codex permission profile.** Generate the fragment again with `payload-policy --host codex`, as [payload protection](../plugin/adapters/payload-protection.md#codex) describes, so it creates `hstack-program`, and change launch lines that name `huguesstack-program` (`-P huguesstack-program`, `-c permissions.huguesstack-program=...`). A profile already named `hstack-program` needs an owner-reviewed merge, as that page says. Name your bounded profile with `--parent`: `payload-policy` refuses both `hstack-program` and the legacy `huguesstack-program`, so a generated profile never extends a generated one.
5. **Rebind program bindings.** A binding records the payload revision and hash, so bindings made on 0.3.x are rejected. Pause a live program, review the change, then bind it again.
6. **Update owner-disabled skill settings** that name the setup skill's old path (`skills/setup-huguesstack`) or the old command prefix.
7. **Maintainers of the setup-proof workflow:** relabel the self-hosted macOS runner `hstack-proof`. The workflow now requires that label.

## Also in this release

0.4.0 is the next release after 0.3.0, so it also carries what merged to main since then. The rename does not change these:

- **pstack 0.15.25 (#57).** The upstream pin moves to 0.15.25 with four new user-only skills (`hugues-help`, `in-your-own-words`, `ketchup`, `sharpen`), for 54 skills. Only `hugues-mode` and `setup-hstack` stay model-invocable. See the [upstream pin and ledger](upstream/README.md).
- **Payload protection and verification gates.** Installed payload protection during autopilot runs (issue #36, PRs #47 and #54), the verification plan comparison and operator-ruling gates (#37), the mobile setup and verification prerequisites (#35) and the plan-translation allow-list fix (#26). The [payload protection proof](payload-protection-proof.md) and the [test accounting](TEST-COVERAGE.md) record what each proves.

## Repository changes

- **hstack-alpha (retired predecessor).** The GitHub repository `osxsystem/hstack`, a different project, was deleted on 2026-10-16. The files this repository cites from it are retained byte for byte under `provenance/upstream/hstack-alpha-99cc612/`, with the 13 files they link to. The [source receipts](wp3-source-receipts.json) carry a note about the deletion, and each receipted input hashes to its retained copy.
- **KMP/CMP practice app.** `tests/fixtures/kmp-compose-ios-pilot/` is hstack-alpha's disposable Kotlin Multiplatform and Compose Multiplatform app with a planted boundary defect, copied in full. No repository check rejected a file, so nothing was left out and no check was changed. The [glossary](GLOSSARY.md) points there.

## Validation and limits

The package validation baseline is 448 Python tests: 131 frozen 0.1.0 contracts, 27 current-checker cases with historical fixtures, one driver that runs the 50 frozen 0.2.0 restoration cases from a hash-bound archive, 48 source and provenance cases, 97 installed adapter and regression cases, 51 native-layout cases, 13 progressive-disclosure cases, 45 installed-tolerance cases, 19 verification-contract cases, six setup-to-proof cases, eight payload-policy cases and two native-runner CLI cases. The release adds six tests over the 442 on main: two guard the `.hstack/` rules (every reader of the models file carries the legacy-read instruction, and setup writes only `.hstack/`) and four bind the retained hstack-alpha bytes to their receipts. The package, core, upstream and whitespace checks pass. See the [test accounting](TEST-COVERAGE.md) for the roots and what each one proves.

These are static source checks. They prove the files, names and wiring agree. One host observation was recorded on 2026-10-16 with Claude Code 2.1.300: `claude -p --plugin-dir plugin --output-format stream-json` from this branch reported the plugin as `hstack` in its init event, with 54 skills under the `/hstack:` prefix, `/hstack:setup-hstack` and `/hstack:hugues-mode` among them. `claude plugin validate --strict` passed on `plugin` and on the repository marketplace. That is session-local loading, not an installed marketplace plugin, and no skill was invoked. The rest is a gap, not an observation:

- Not observed: Codex loading the plugin as `hstack`; a Claude Code session invoking `/hstack:hugues-mode` or `/hstack:setup-hstack`; installing `hstack@hstack` from the renamed repository; the GitHub redirect from the old repository URL; a live session reading `.huguesstack/models.md` through the legacy-read instruction and telling the user to move it; setup writing `.hstack/models.md`; a Codex run under the `hstack-program` profile; the setup-proof workflow on a runner labeled `hstack-proof`.
- Not run for this release: the native setup-to-proof check, the payload-boundary native regression, and the offline Bun tests. The earlier host receipts ([skill-list host validation](skill-list-host-validation.md), [router eval](hugues-mode-router-eval.md), [router interactive check](router-interactive-check.md)) observed the plugin under its 0.3.x names and stay unchanged. They do not establish the renamed plugin's behavior.
- Frozen archives and dated evidence keep the old name on purpose: the 0.1.0 and 0.2.0 release archives, the context baselines, the release notes of 0.1.0 to 0.3.0 and the validation and evidence records. Seven historical test modules keep the old names where they read the frozen 0.1.0 tree.
- The Astra High review policy is suspended for this repository, so no Astra review was run.

## Downloads

Release assets are attached when the owner publishes. If a `SHA256SUMS` file is attached, verify the downloaded assets from the folder that holds all of them:

```sh
shasum -a 256 -c SHA256SUMS
```

The hashes detect download changes; they are not a separate signing or trust service.
