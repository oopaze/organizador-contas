from django.test import SimpleTestCase

from modules.ai.mcp.dates import parse_month, validate_date
from modules.ai.mcp.exceptions import InvalidDateError


class TestParseMonth(SimpleTestCase):
    def test_parses(self):
        self.assertEqual(parse_month("2026-10"), (2026, 10))

    def test_invalid_raises(self):
        with self.assertRaises(InvalidDateError) as ctx:
            parse_month("2026-13")
        self.assertEqual(ctx.exception.code, "INVALID_DATE")
        self.assertIn("YYYY-MM", str(ctx.exception))


class TestValidateDate(SimpleTestCase):
    def test_normalizes(self):
        self.assertEqual(validate_date("2026-10-01", "due_start"), "2026-10-01")

    def test_invalid_raises(self):
        with self.assertRaises(InvalidDateError) as ctx:
            validate_date("01/10/2026", "due_start")
        self.assertIn("due_start", str(ctx.exception))
