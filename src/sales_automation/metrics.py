from __future__ import annotations

import pandas as pd



def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Compute executive KPIs from the filtered dataset."""
    if df.empty:
        return {
            "revenue": 0.0,
            "orders": 0.0,
            "avg_ticket": 0.0,
            "avg_rating": 0.0,
            "gross_income": 0.0,
        }

    revenue = float(df["Total"].sum())
    orders = float(df["Invoice ID"].nunique())
    avg_ticket = revenue / orders if orders else 0.0

    return {
        "revenue": revenue,
        "orders": orders,
        "avg_ticket": avg_ticket,
        "avg_rating": float(df["Rating"].mean()),
        "gross_income": float(df["Gross income"].sum()),
    }



def revenue_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by date for trend analysis."""
    return (
        df.groupby("Date", as_index=False)["Total"]
        .sum()
        .sort_values("Date")
    )



def revenue_by_product_line(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by product line."""
    return (
        df.groupby("Product line", as_index=False)["Total"]
        .sum()
        .sort_values("Total", ascending=False)
    )



def revenue_by_city(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by city."""
    return (
        df.groupby("City", as_index=False)["Total"]
        .sum()
        .sort_values("Total", ascending=False)
    )



def payment_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by payment method."""
    return (
        df.groupby("Payment", as_index=False)["Total"]
        .sum()
        .sort_values("Total", ascending=False)
    )
