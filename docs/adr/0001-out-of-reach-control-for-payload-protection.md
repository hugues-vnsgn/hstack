# An out-of-reach control, not the Bash sandbox, protects a mobile program's payload

Claude Code's Bash sandbox kept narrowing mobile tools in the field: no Mach registration for the emulator, the XcodeBuildMCP command-line tool, `git merge` over the built-in protected `.mcp.json`. It also never covered the writers that run outside it: file tools, MCP servers, hooks. So payload protection now accepts an **out-of-reach control** as the enforcing control, judged by property: the agent's OS user can't remove it, and it can't rename away the payload or any ancestor. For Claude the recipe is a root-owned plugin seed selected by `CLAUDE_CODE_PLUGIN_SEED_DIR` in the root-owned managed settings, and it is the recommended route for mobile programs. The sandbox becomes an optional layer outside payload readiness. Codex keeps its permission-profile route, because it has no read-only plugin location. Decided in [Which enforcement a mobile program uses for payload protection (#66)](https://github.com/hugues-vnsgn/hstack/issues/66).

## Considered options

- **Sandbox only** (the pre-#66 route plus the `--macos-mobile` recipe): every mobile round found another tool it blocks, and MCP servers and hooks stay unprotected.
- **Sandbox and an out-of-reach control together**: keeps every mobile friction and adds the admin step.
- **The user-immutable flag or an ACL on agent-owned files**: the owner can lift both, which is why the earlier lock was ruled out as evidence.

## Consequences

- Installing and updating hStack becomes an owner-run admin step, done between programs. The seed turns host auto-update off.
- The managed settings file reaches every Claude configuration on the machine.
- A user-scope reinstall can still override the seed. Startup and recheck detection catch it; nothing prevents it.
