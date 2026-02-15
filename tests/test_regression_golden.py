from pathlib import Path
import unittest

from sales_automation.data import load_sales_data
from sales_automation.metrics import compute_kpis, revenue_by_city


FIXTURE_PATH = Path("tests/fixtures/golden_sales.csv")


class TestRegressionGoldenDataset(unittest.TestCase):
    def test_kpis_match_expected_values(self) -> None:
        df = load_sales_data(FIXTURE_PATH)
        kpis = compute_kpis(df)

        self.assertAlmostEqual(kpis["revenue"], 189.0, places=4)
        self.assertEqual(kpis["orders"], 4.0)
        self.assertAlmostEqual(kpis["avg_ticket"], 47.25, places=4)
        self.assertAlmostEqual(kpis["gross_income"], 180.0, places=4)
        self.assertAlmostEqual(kpis["avg_rating"], 8.175, places=4)

    def test_city_ranking_is_stable(self) -> None:
        df = load_sales_data(FIXTURE_PATH)
        ranked = revenue_by_city(df)

        self.assertEqual(ranked.iloc[0]["City"], "Toronto")
        self.assertAlmostEqual(float(ranked.iloc[0]["Total"]), 94.5, places=4)
        self.assertEqual(ranked.iloc[1]["City"], "Chicago")
        self.assertAlmostEqual(float(ranked.iloc[1]["Total"]), 63.0, places=4)
        self.assertEqual(ranked.iloc[2]["City"], "Vancouver")
        self.assertAlmostEqual(float(ranked.iloc[2]["Total"]), 31.5, places=4)


if __name__ == "__main__":
    unittest.main()
