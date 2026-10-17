"""Unit tests for the independent CSV audit example."""

import io
import unittest

from src.quality_audit import audit_csv


class CsvAuditTests(unittest.TestCase):
    def test_valid_rows_are_counted(self) -> None:
        data = "task_id,team,status,hours\n1,api,done,2.50\n2,qa,backlog,1.25\n"
        report = audit_csv(io.StringIO(data))
        self.assertTrue(report.ok)
        self.assertEqual(report.total_rows, 2)
        self.assertEqual(report.accepted_rows, 2)
        self.assertEqual(report.total_hours, "3.75")
        self.assertEqual(report.status_counts, {"backlog": 1, "done": 1})

    def test_missing_schema_column_fails(self) -> None:
        report = audit_csv(io.StringIO("task_id,team,status\n1,api,done\n"))
        self.assertFalse(report.ok)
        self.assertEqual(report.errors[0].code, "missing_column")
        self.assertEqual(report.total_rows, 0)

    def test_duplicate_id_is_rejected(self) -> None:
        data = "task_id,team,status,hours\na,api,done,1\na,api,done,1\n"
        report = audit_csv(io.StringIO(data))
        self.assertEqual(report.accepted_rows, 1)
        self.assertIn("duplicate", [error.code for error in report.errors])

    def test_invalid_fields_are_rejected(self) -> None:
        data = "task_id,team,status,hours\n1,,active,-5\n"
        report = audit_csv(io.StringIO(data))
        self.assertFalse(report.ok)
        self.assertEqual(report.accepted_rows, 0)
        self.assertEqual({x.code for x in report.errors}, {"required", "invalid_choice", "invalid_number"})

    def test_extra_values_are_rejected(self) -> None:
        data = "task_id,team,status,hours\n1,api,done,2,extra\n"
        report = audit_csv(io.StringIO(data))
        self.assertEqual(report.accepted_rows, 0)
        self.assertEqual(report.errors[0].code, "extra_columns")

    def test_blank_input_is_rejected(self) -> None:
        report = audit_csv(io.StringIO(""))
        self.assertFalse(report.ok)
        self.assertEqual(len(report.errors), 4)

    def test_empty_valid_csv_is_allowed(self) -> None:
        report = audit_csv(io.StringIO("task_id,team,status,hours\n"))
        self.assertTrue(report.ok)
        self.assertEqual(report.total_rows, 0)


if __name__ == "__main__":
    unittest.main()
