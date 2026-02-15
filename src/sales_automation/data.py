from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path("relatorio_vendas.csv")

COLUMN_RENAME_MAP = {
    "Costumer type": "Customer type",
    "gross income": "Gross income",
    "Unit price": "Unit price",
}


def _read_csv_flexible(data_path: Path | str) -> pd.DataFrame:
    """Read CSV supporting legacy and modern delimiters/encodings."""
    read_attempts = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "decimal": ",", "encoding": "latin1"},
    ]
    last_error: Exception | None = None

    for kwargs in read_attempts:
        try:
            return pd.read_csv(data_path, **kwargs)
        except Exception as exc:  # pragma: no cover
            last_error = exc

    raise RuntimeError(f"Unable to read CSV file at {data_path}") from last_error


def load_sales_data(data_path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Load and normalize the source sales dataset."""
    df = _read_csv_flexible(data_path)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    df = df.rename(columns=COLUMN_RENAME_MAP)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    numeric_columns = [
        "Total",
        "Gross income",
        "Quantity",
        "Rating",
        "Unit price",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["Total", "Gross income", "Quantity", "Rating"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    return df.sort_values("Date").reset_index(drop=True)


def filter_sales_data(
    df: pd.DataFrame,
    months: list[str] | None = None,
    cities: list[str] | None = None,
    product_lines: list[str] | None = None,
) -> pd.DataFrame:
    """Filter dataset by month, city and product line."""
    filtered_df = df

    if months:
        filtered_df = filtered_df[filtered_df["Month"].isin(months)]
    if cities:
        filtered_df = filtered_df[filtered_df["City"].isin(cities)]
    if product_lines:
        filtered_df = filtered_df[filtered_df["Product line"].isin(product_lines)]

    return filtered_df.copy()
