from __future__ import annotations

from pathlib import Path

import plotly.express as px
import streamlit as st

from .data import load_sales_data, filter_sales_data
from .metrics import (
    compute_kpis,
    payment_mix,
    revenue_by_city,
    revenue_by_day,
    revenue_by_product_line,
)


@st.cache_data(show_spinner=False)
def get_data(data_path: str) -> object:
    return load_sales_data(Path(data_path))



def run_dashboard() -> None:
    st.set_page_config(page_title="Sales Automation Dashboard", layout="wide")

    st.title("Sales Analytics Automation Case")
    st.caption(
        "End-to-end analytics workflow: data ingestion, KPI tracking, segmentation and export-ready insights."
    )

    df = get_data("relatorio_vendas.csv")

    months = sorted(df["Month"].unique().tolist())
    cities = sorted(df["City"].unique().tolist())
    product_lines = sorted(df["Product line"].unique().tolist())

    with st.sidebar:
        st.header("Filters")

        selected_months = st.multiselect(
            "Month",
            options=months,
            default=[months[-1]] if months else [],
        )
        selected_cities = st.multiselect("City", options=cities, default=cities)
        selected_product_lines = st.multiselect(
            "Product line",
            options=product_lines,
            default=product_lines,
        )

    filtered_df = filter_sales_data(
        df,
        months=selected_months,
        cities=selected_cities,
        product_lines=selected_product_lines,
    )

    kpis = compute_kpis(filtered_df)

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    metric_col1.metric("Revenue", f"${kpis['revenue']:,.2f}")
    metric_col2.metric("Orders", f"{int(kpis['orders']):,}")
    metric_col3.metric("Average Ticket", f"${kpis['avg_ticket']:,.2f}")
    metric_col4.metric("Gross Income", f"${kpis['gross_income']:,.2f}")
    metric_col5.metric("Average Rating", f"{kpis['avg_rating']:.2f}")

    if filtered_df.empty:
        st.warning("No rows match the current filters. Adjust the selections to continue.")
        return

    trend_col, product_col = st.columns(2)
    city_col, payment_col = st.columns(2)

    fig_trend = px.line(
        revenue_by_day(filtered_df),
        x="Date",
        y="Total",
        markers=True,
        title="Revenue by Day",
    )
    trend_col.plotly_chart(fig_trend, use_container_width=True)

    fig_product = px.bar(
        revenue_by_product_line(filtered_df),
        x="Total",
        y="Product line",
        orientation="h",
        title="Revenue by Product Line",
    )
    product_col.plotly_chart(fig_product, use_container_width=True)

    fig_city = px.bar(
        revenue_by_city(filtered_df),
        x="City",
        y="Total",
        title="Revenue by City",
    )
    city_col.plotly_chart(fig_city, use_container_width=True)

    fig_payment = px.pie(
        payment_mix(filtered_df),
        values="Total",
        names="Payment",
        title="Payment Mix",
    )
    payment_col.plotly_chart(fig_payment, use_container_width=True)

    st.download_button(
        label="Download filtered dataset (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales_data.csv",
        mime="text/csv",
    )
