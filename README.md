# Agent workflow lab

A public, synthetic experiment in Spec → implementation → tests → bounded Codex
repair → Draft PR → GitHub Actions → independent Codex review.

Python 3.12, standard library only. No install step, application secrets,
private data, deployment, or paid services are required.

```sh
python3 -m unittest discover -s tests -v
python3 -m range_summary 3 1 2 2 6
# [[1, 3], [6, 6]]
```

- Contract and measurable completion criteria: [Spec](docs/spec.md).
- CI: [pull_request workflow](.github/workflows/ci.yml), standard Ubuntu runner.
- Execution evidence and independent review will be recorded under `docs/`.

This is one supervised Codex execution, not a new orchestration framework or
an autonomous agent running inside GitHub Actions. CI runs the tests; Codex
performs the implementation, diagnosis, repair, and review in its own contexts.
Repair attempts are limited to three. A Draft PR stays unmerged.
