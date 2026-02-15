from pathlib import Path
import unittest

from sales_automation.data import filter_sales_data, load_sales_data


DATA_PATH = Path("relatorio_vendas.csv")
EXPECTED_CITIES = {"Toronto", "Chicago", "Vancouver"}
EXPECTED_PRODUCT_LINES = {
    "Health & Wellness",
    "Electronics Accessories",
    "Home & Lifestyle",
    "Food & Beverages",
    "Sports & Travel",
}


class TestData(unittest.TestCase):
    def test_load_sales_data_has_expected_schema(self) -> None:
        df = load_sales_data(DATA_PATH)

        self.assertFalse(df.empty)
        self.assertIn("Month", df.columns)
        self.assertIn("Customer type", df.columns)
        self.assertNotIn("Costumer type", df.columns)
        self.assertTrue(df["Date"].is_monotonic_increasing)

    def test_filter_sales_data_by_month_city(self) -> None:
        df = load_sales_data(DATA_PATH)

        sample_month = df["Month"].iloc[0]
        sample_city = df["City"].iloc[0]

        filtered = filter_sales_data(df, months=[sample_month], cities=[sample_city])

        self.assertFalse(filtered.empty)
        self.assertEqual(set(filtered["Month"].unique()), {sample_month})
        self.assertEqual(set(filtered["City"].unique()), {sample_city})

    def test_dataset_uses_north_america_business_labels(self) -> None:
        df = load_sales_data(DATA_PATH)

        self.assertTrue(set(df["City"].unique()).issubset(EXPECTED_CITIES))
        self.assertTrue(set(df["Product line"].unique()).issubset(EXPECTED_PRODUCT_LINES))
        self.assertIn("Customer Name", df.columns)
        self.assertGreater(df["Customer Name"].str.contains(" ").mean(), 0.95)


if __name__ == "__main__":
    unittest.main()
