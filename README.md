# Ayyappan Thirukkannan | Engineering Portfolio

[![Python tests](https://github.com/tayyadev/engineering-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/tayyadev/engineering-portfolio/actions/workflows/ci.yml)

A public software-engineering portfolio with a small, **independently written and runnable** Python project. It is intended for hiring reviews and technical discussions, not as a mirror of commercial or private projects.

## Engineering focus

- **Backend and integrations:** Python, C#/.NET, REST APIs, data validation, automation
- **Full stack:** TypeScript, React, Node.js, SQL-based applications
- **Applied AI:** LLM/API integrations, retrieval-augmented applications, workflow orchestration
- **Quality:** unit testing, error handling, observable behavior, secure-by-default design

## Featured public sample: CSV Quality Audit

The [CSV Quality Audit](src/quality_audit.py) is a command-line tool that validates generic task records and emits a structured JSON report.

**What it demonstrates**

- Schema and required-field validation
- Duplicate-ID and invalid-value detection
- Decimal-based numeric handling and deterministic summary output
- Row-level error messages, predictable exit codes and automated tests
- Standard-library-only Python (no API keys, infrastructure or dependencies required)

**Run with Python 3.10+**

```bash
python -m src.quality_audit sample_data/tasks.csv
python -m unittest discover -s tests -v
```

Sample successful output:

```json
{
  "ok": true,
  "total_rows": 4,
  "accepted_rows": 4,
  "status_counts": {
    "backlog": 1,
    "done": 2,
    "in_progress": 1
  },
  "total_hours": "8.25",
  "errors": []
}
```

The command exits with `0` for a valid file, `1` for validation findings and `2` if the input cannot be opened or read. Tests run automatically through [GitHub Actions](.github/workflows/ci.yml).

## Project structure

```text
.github/workflows/ci.yml   Continuous integration
sample_data/tasks.csv      Synthetic example data
src/quality_audit.py       Validation and CLI
tests/test_quality_audit.py Unit tests
```

## What this repository does *not* contain

This is a standalone public sample. It does **not** contain code or data from private repositories, commercial or customer projects, unpublished implementation details, credentials, production configuration, or proprietary trading strategies. Other work may remain private for legitimate confidentiality reasons.

## License

This independent example is made available under the [MIT License](LICENSE).
