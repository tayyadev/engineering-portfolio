"""Audit generic task-record CSV files with no third-party dependencies.

This module is an independent public example. It does not use private projects,
private data, client-specific rules, or production credentials.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, TextIO

REQUIRED_COLUMNS = ("task_id", "team", "status", "hours")
VALID_STATUSES = frozenset(("backlog", "in_progress", "done"))


@dataclass(frozen=True)
class Finding:
    row: int
    field: str
    code: str
    message: str


@dataclass(frozen=True)
class AuditReport:
    total_rows: int
    accepted_rows: int
    status_counts: dict[str, int]
    total_hours: str
    errors: list[Finding]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, **asdict(self)}


def _required_text(value: str | None, field: str, row: int, errors: list[Finding]) -> str | None:
    cleaned = (value or "").strip()
    if not cleaned:
        errors.append(Finding(row, field, "required", f"{field} must not be blank"))
        return None
    return cleaned


def audit_csv(stream: TextIO) -> AuditReport:
    """Validate CSV records and return an audit report without side effects."""
    reader = csv.DictReader(stream)
    present_columns = set(reader.fieldnames or [])
    missing = [name for name in REQUIRED_COLUMNS if name not in present_columns]
    if missing:
        return AuditReport(
            total_rows=0,
            accepted_rows=0,
            status_counts={},
            total_hours="0",
            errors=[Finding(1, name, "missing_column", f"missing required column: {name}") for name in missing],
        )

    errors: list[Finding] = []
    seen_ids: set[str] = set()
    statuses: Counter[str] = Counter()
    total_hours = Decimal("0")
    accepted = 0
    total = 0

    for row_number, record in enumerate(reader, start=2):
        total += 1
        start_errors = len(errors)
        if None in record:
            errors.append(Finding(row_number, "row", "extra_columns", "row has more values than columns"))

        task_id = _required_text(record.get("task_id"), "task_id", row_number, errors)
        _required_text(record.get("team"), "team", row_number, errors)
        status = _required_text(record.get("status"), "status", row_number, errors)
        raw_hours = _required_text(record.get("hours"), "hours", row_number, errors)

        if task_id is not None:
            if task_id in seen_ids:
                errors.append(Finding(row_number, "task_id", "duplicate", "task_id must be unique"))
            seen_ids.add(task_id)

        if status is not None and status not in VALID_STATUSES:
            errors.append(Finding(row_number, "status", "invalid_choice", "status must be backlog, in_progress, or done"))

        parsed_hours: Decimal | None = None
        if raw_hours is not None:
            try:
                parsed_hours = Decimal(raw_hours)
                if not parsed_hours.is_finite() or parsed_hours < 0:
                    raise InvalidOperation
            except InvalidOperation:
                errors.append(Finding(row_number, "hours", "invalid_number", "hours must be a finite, nonnegative number"))

        if len(errors) == start_errors and status is not None and parsed_hours is not None:
            accepted += 1
            statuses[status] += 1
            total_hours += parsed_hours

    return AuditReport(
        total_rows=total,
        accepted_rows=accepted,
        status_counts=dict(sorted(statuses.items())),
        total_hours=str(total_hours),
        errors=errors,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a CSV file of generic task records")
    parser.add_argument("csv_file", type=Path, help="CSV file to validate")
    args = parser.parse_args(argv)
    try:
        with args.csv_file.open("r", encoding="utf-8-sig", newline="") as handle:
            report = audit_csv(handle)
    except (OSError, UnicodeError, csv.Error) as exc:
        print(json.dumps({"ok": False, "error": f"cannot read CSV input: {exc}"}), file=sys.stderr)
        return 2
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
