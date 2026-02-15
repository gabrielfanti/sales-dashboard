from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sales_automation.data import load_sales_data


OUTPUT_DIR = PROJECT_ROOT / "artifacts"
OUTPUT_FILE = OUTPUT_DIR / "monthly_summary.csv"



def generate_monthly_summary() -> Path:
    df = load_sales_data(PROJECT_ROOT / "relatorio_vendas.csv")

    summary = (
        df.groupby("Month", as_index=False)
        .agg(
            revenue=("Total", "sum"),
            orders=("Invoice ID", "nunique"),
            avg_rating=("Rating", "mean"),
            gross_income=("Gross income", "sum"),
        )
        .sort_values("Month")
    )
    summary["avg_ticket"] = summary["revenue"] / summary["orders"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_FILE, index=False)

    return OUTPUT_FILE


if __name__ == "__main__":
    file_path = generate_monthly_summary()
    print(f"Monthly summary generated at: {file_path}")
