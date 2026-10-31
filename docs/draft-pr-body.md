This experiment adds a Python standard-library API/CLI that coalesces integers into sorted maximal inclusive ranges. It exercises Spec → implementation → real test failure → bounded Codex repair → independent review, with a `pull_request` GitHub Actions workflow on standard `ubuntu-latest` / Python 3.12.

Validation:
- Seeded defect commit: `b06f68f149dd744b6b2ea04918cf62054c4e2b8e`. Actual run: 16 tests, 593 failure records including exhaustive subtests, exit 1.
- Codex repair: `a1a32811713f789a8a6907a447a9d3d602e1b4af`. Only the adjacency comparison changed; test SHA-256 stayed identical. Repair attempts: **1/3**.
- Actual local re-run: **16 tests pass**, including 781 exhaustive input sequences and four CLI tests, exit 0. No skipped/removed/weakened tests or expected-failure conversion.
- A separate Codex context reviewed an independent Git archive without the implementation conversation: **no blocking findings**; 16 tests plus 3,050 valid API, 11 invalid-type, and seven CLI checks pass.
- CI runs on PR opened/synchronize/reopened/ready_for_review, pins official actions to full SHAs, uses read-only contents permission, and needs no application secrets or Python packages.

Evidence is committed in `docs/execution-report.md` and `docs/evidence/`, including the compressed complete failing log, passing log, test hash, exact commit IDs, reviewer commands, and independent review.

Actual remote validation: [Draft PR #1](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/1) created, and [pull_request Actions run 41200564988](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41200564988) **passed** for head `27d763df1ab201d640d947a487e79ab0adb7dedd`. The GitHub-hosted ubuntu-latest runner executed all 16 tests and the CLI assertion successfully. Final documentation-update head/run and independent post-CI verification are added to the live PR description after its synchronize run completes.

Human involvement after the original execution request: three follow-up user messages observed, at least one environment publication reported by the user, and zero manual code repairs observed. Exact environment UI actions are not directly observable. API access is now verified in the newly published environment. No permission changes, paid services, merge, deployment, or custom orchestrator.

This is one Codex-directed seeded-defect experiment, not an agent running inside Actions or proof of unattended future tasks. Keep this PR in draft and unmerged.
