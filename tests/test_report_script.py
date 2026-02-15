import unittest

from scripts.generate_monthly_report import generate_monthly_summary


class TestReportScript(unittest.TestCase):
    def test_generate_monthly_summary_creates_csv(self) -> None:
        output_file = generate_monthly_summary()

        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.name, "monthly_summary.csv")
        self.assertGreater(output_file.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
