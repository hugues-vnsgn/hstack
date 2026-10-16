---
name: mobile-proof
description: Select build, target-test, and runtime evidence when the active mobile Stack Pack requires proof of a changed mobile artifact.
---

# Mobile proof

1. Identify the changed platform and read [platform discovery](../../references/platforms.md).
2. Select repository commands and evidence using [mobile evidence](../../references/evidence.md).
3. Run the applicable checks within the Work Unit's authority. Record blocked checks with their missing prerequisite.
4. Return command outcomes and artifact paths in the Work Unit result. Distinguish compilation, target tests, and runtime behavior.

Finish when every applicable evidence requirement has an observed result or an
explicit blocked reason. Do not infer evidence from another platform's pass.
