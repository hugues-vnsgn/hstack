> Historical 0.1.0 implementation record. Its rewritten workflows and deferrals are superseded on the unreleased restoration branch. Read the [development guide](../DEVELOPER-GUIDE.md) for current source contracts and evidence limits.

# WP2 source record

WP2 reads pstack 0.15.9 from `cursor/plugins` at commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Its extracted 161 pstack files matched the pinned Git blob SHA-1 values before adaptation. See [the pinned source](https://github.com/cursor/plugins/tree/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack).
The pstack 0.15.25 merge rebound the receipt fingerprints to `6ce45c59b9301a638c1fe1a7b8dc2a82b650898f`, and the 0.15.32 merge to `e73df471cd4bd918367e99f3dd9c51bd53ddf5f0`; this record still describes the original import.

[wp2-provenance.json](wp2-provenance.json) records the source path, destination, upstream blob SHA-1 and upstream byte SHA-256 for the mode, worker, interrogate, ten adapted playbooks and all 24 principles. Source checksums describe upstream bytes, not adapted output. The principles and interrogate reference files are copied byte-for-byte. Attribution stays here so adding frontmatter does not alter those files. The inline principles index follows the upstream mode and links to the copied leaves.

The ten adapted playbooks derive from the matching files under `pstack/skills/poteto-mode/playbooks/` at the same pin. Their body `source:` lines record source paths. Four mobile playbooks and mobile lane guidance adapt the current project plan; their authored status does not imply observed consumer support.

The adaptation replaces Cursor rules and model slugs with host-native fresh subagents and inherit-parent defaults. It bounds worker assignments, makes mobile domain and target proof explicit, limits remote actions to user authority and supports read-only route previews. `interrogate` labels process and cross-host independence without contacting external reviewers automatically.

`principle-explain-the-number` retains its upstream link to `benchmark-checklist`, which the current plan defers to 0.2. The exact absent link is recorded in `deferred_links` and bound to the pinned source checksum. The package checker reports this known gap visibly and still rejects other broken links. No benchmark leaf is shipped. The mode requires a manual explanation of measured numbers and labels the deferred workflow.

Keep the [pstack MIT notice](../../PSTACK-LICENSE). The broader upstream ledger and reproducible delta are now recorded in the [WP5 sync package](README.md). This record covers imported WP2 source; the full ledger distinguishes present files from planned and deferred responsibilities.
