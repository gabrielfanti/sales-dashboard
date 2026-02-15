from __future__ import annotations

from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sales_automation.data import load_sales_data

OUTPUT_DIR = PROJECT_ROOT / "artifacts"
JSON_OUTPUT = OUTPUT_DIR / "business_snapshot.json"
MD_OUTPUT = OUTPUT_DIR / "business_snapshot.md"


def generate_business_snapshot() -> tuple[Path, Path]:
    df = load_sales_data(PROJECT_ROOT / "relatorio_vendas.csv")

    revenue = float(df["Total"].sum())
    orders = int(df["Invoice ID"].nunique())
    avg_ticket = revenue / orders if orders else 0.0

    city_rev = (
        df.groupby("City", as_index=False)["Total"]
        .sum()
        .sort_values("Total", ascending=False)
    )
    top_city = city_rev.iloc[0]
    top_city_share = float(top_city["Total"] / revenue * 100) if revenue else 0.0

    product_rev = (
        df.groupby("Product line", as_index=False)["Total"]
        .sum()
        .sort_values("Total", ascending=False)
    )
    top_product = product_rev.iloc[0]
    top_product_share = float(top_product["Total"] / revenue * 100) if revenue else 0.0

    payment_rev = (
        df.groupby("Payment", as_index=False)["Total"]
        .sum()
        .sort_values("Total", ascending=False)
    )
    cashless_share = (
        float(
            payment_rev[payment_rev["Payment"].isin(["Credit Card", "Mobile Wallet"])]["Total"].sum()
            / revenue
            * 100
        )
        if revenue
        else 0.0
    )

    monthly = (
        df.groupby("Month", as_index=False)["Total"]
        .sum()
        .sort_values("Month")
    )
    month_growth = 0.0
    if len(monthly) >= 2 and float(monthly.iloc[0]["Total"]) != 0:
        month_growth = float((monthly.iloc[-1]["Total"] - monthly.iloc[0]["Total"]) / monthly.iloc[0]["Total"] * 100)

    payload = {
        "period": {
            "start_month": str(monthly.iloc[0]["Month"]),
            "end_month": str(monthly.iloc[-1]["Month"]),
        },
        "kpis": {
            "revenue": round(revenue, 2),
            "orders": orders,
            "avg_ticket": round(avg_ticket, 2),
            "avg_rating": round(float(df["Rating"].mean()), 2),
            "cashless_share_pct": round(cashless_share, 2),
            "growth_pct_first_to_last_month": round(month_growth, 2),
        },
        "leaders": {
            "top_city": {
                "name": str(top_city["City"]),
                "revenue": round(float(top_city["Total"]), 2),
                "share_pct": round(top_city_share, 2),
            },
            "top_product_line": {
                "name": str(top_product["Product line"]),
                "revenue": round(float(top_product["Total"]), 2),
                "share_pct": round(top_product_share, 2),
            },
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    markdown = f"""## Executive Snapshot ({payload['period']['start_month']} to {payload['period']['end_month']})

- Revenue: ${payload['kpis']['revenue']:,.2f}
- Orders: {payload['kpis']['orders']:,}
- Average ticket: ${payload['kpis']['avg_ticket']:,.2f}
- Average rating: {payload['kpis']['avg_rating']:.2f}/10
- Cashless share: {payload['kpis']['cashless_share_pct']:.2f}%
- Revenue growth (first month vs last month): {payload['kpis']['growth_pct_first_to_last_month']:.2f}%
- Top city: {payload['leaders']['top_city']['name']} ({payload['leaders']['top_city']['share_pct']:.2f}% of revenue)
- Top product line: {payload['leaders']['top_product_line']['name']} ({payload['leaders']['top_product_line']['share_pct']:.2f}% of revenue)
"""
    MD_OUTPUT.write_text(markdown, encoding="utf-8")

    return JSON_OUTPUT, MD_OUTPUT


if __name__ == "__main__":
    json_path, md_path = generate_business_snapshot()
    print(f"Business snapshot JSON generated at: {json_path}")
    print(f"Business snapshot Markdown generated at: {md_path}")
