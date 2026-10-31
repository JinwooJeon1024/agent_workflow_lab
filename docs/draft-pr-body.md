This experiment adds a Python standard-library API/CLI that coalesces integers into sorted maximal inclusive ranges. It exercises Spec → implementation → real test failure → bounded Codex repair → independent review, with a `pull_request` GitHub Actions workflow on standard `ubuntu-latest` / Python 3.12.

Validation:
- Seeded defect commit: `b06f68f149dd744b6b2ea04918cf62054c4e2b8e`. Actual run: 16 tests, 593 failure records including exhaustive subtests, exit 1.
- Codex repair: `a1a32811713f789a8a6907a447a9d3d602e1b4af`. Only the adjacency comparison changed; test SHA-256 stayed identical. Repair attempts: **1/3**.
- Actual local re-run: **16 tests pass**, including 781 exhaustive input sequences and four CLI tests, exit 0. No skipped/removed/weakened tests or expected-failure conversion.
- A separate Codex context reviewed an independent Git archive without the implementation conversation: **no blocking findings**; 16 tests plus 3,050 valid API, 11 invalid-type, and seven CLI checks pass.
- CI runs on PR opened/synchronize/reopened/ready_for_review, pins official actions to full SHAs, uses read-only contents permission, and needs no application secrets or Python packages.

Evidence is committed in `docs/execution-report.md` and `docs/evidence/`, including the compressed complete failing log, passing log, test hash, exact commit IDs, reviewer commands, and independent review.

Remote validation is a separate completion gate: actual Actions run URL, tested head SHA, event, job/step results, and conclusion must be confirmed after this Draft PR is created. Local results are not a claim of CI success.

Human interventions after the execution request: zero additional chat instructions or manual code repairs observed. Environment UI changes are not directly observable; GitHub API access initially required an environment network-policy action. No permission changes, paid services, merge, deployment, or custom orchestrator.

This is one Codex-directed seeded-defect experiment, not an agent running inside Actions or proof of unattended future tasks. Keep this PR in draft and unmerged.
