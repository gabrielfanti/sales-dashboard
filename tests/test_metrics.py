from pathlib import Path
import unittest

from sales_automation.data import load_sales_data
from sales_automation.metrics import compute_kpis, revenue_by_city


DATA_PATH = Path("relatorio_vendas.csv")


class TestMetrics(unittest.TestCase):
    def test_compute_kpis_returns_positive_values(self) -> None:
        df = load_sales_data(DATA_PATH)
        kpis = compute_kpis(df)

        self.assertGreater(kpis["revenue"], 0)
        self.assertGreater(kpis["orders"], 0)
        self.assertGreater(kpis["avg_ticket"], 0)
        self.assertGreater(kpis["gross_income"], 0)

    def test_revenue_by_city_is_sorted_desc(self) -> None:
        df = load_sales_data(DATA_PATH)
        city_revenue = revenue_by_city(df)

        self.assertFalse(city_revenue.empty)
        totals = city_revenue["Total"].tolist()
        self.assertEqual(totals, sorted(totals, reverse=True))


if __name__ == "__main__":
    unittest.main()
