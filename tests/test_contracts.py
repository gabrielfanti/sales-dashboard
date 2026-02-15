from datetime import datetime, timezone
from pathlib import Path
import unittest

from sales_automation.data import load_sales_data


DATA_PATH = Path("relatorio_vendas.csv")
REQUIRED_COLUMNS = {
    "Invoice ID",
    "Branch",
    "City",
    "Customer type",
    "Customer Name",
    "Gender",
    "Product line",
    "Unit price",
    "Quantity",
    "Tax 5%",
    "Total",
    "Date",
    "Time",
    "Payment",
    "cogs",
    "gross margin percentage",
    "Gross income",
    "Rating",
    "Month",
}


class TestDataContracts(unittest.TestCase):
    def test_required_columns_exist(self) -> None:
        df = load_sales_data(DATA_PATH)
        missing = REQUIRED_COLUMNS - set(df.columns)
        self.assertEqual(missing, set(), f"Missing required columns: {missing}")

    def test_numeric_ranges_are_valid(self) -> None:
        df = load_sales_data(DATA_PATH)

        self.assertTrue((df["Total"] > 0).all())
        self.assertTrue((df["Quantity"] > 0).all())
        self.assertTrue((df["Gross income"] > 0).all())
        self.assertTrue(df["Rating"].between(0, 10).all())

    def test_dates_are_not_in_the_future(self) -> None:
        df = load_sales_data(DATA_PATH)
        today = datetime.now(timezone.utc).date()
        self.assertTrue((df["Date"].dt.date <= today).all())


if __name__ == "__main__":
    unittest.main()
