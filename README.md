# Sales Analytics Automation Case

An end-to-end analytics automation project built with Python, Streamlit, Pandas and Plotly.

This repository demonstrates how to turn raw retail transactions into a decision-ready dashboard with automated quality checks, tested transformations and CI-generated reporting artifacts.
The dataset is fully in English and tailored to a North American retail context (cities, product labels and customer names).

## Why this project

This case focuses on production-minded analytics work:
- reliable data ingestion and normalization;
- reusable transformation and KPI modules;
- tested behavior for critical data paths;
- CI automation for validation and report generation.

## Why automation exists

The automation layer is a business reliability guardrail, not just a technical extra.
- prevents silent data/schema breaks before they reach stakeholders;
- protects KPI logic from regressions after code changes;
- guarantees a monthly report artifact is generated in CI;
- provides non-technical proof of quality through a visual report.

## Business scenario

A retail operation needs a fast way to monitor revenue performance by month, city, product line and payment method.
The solution provides:
- executive KPIs (Revenue, Orders, Average Ticket, Gross Income, Average Rating);
- segmentation filters for commercial analysis;
- downloadable filtered data for stakeholder follow-up.

## Executive metrics snapshot (2023 dataset)

- Revenue: `$2,774,084.05`
- Orders: `1,000`
- Average ticket: `$2,774.08`
- Average rating: `7.46/10`
- Cashless share (Credit Card + Mobile Wallet): `66.45%`
- Revenue growth (Jan vs Dec 2023): `+22.78%`
- Top city contribution: `Toronto (36.60% of revenue)`
- Top product line contribution: `Health & Wellness (30.86% of revenue)`

These values are generated from source data using `scripts/generate_business_snapshot.py`.

## Architecture

```text
relatorio_vendas.csv
  -> src/sales_automation/data.py        (load + normalize + filter)
  -> src/sales_automation/metrics.py     (KPIs + aggregations)
  -> src/sales_automation/dashboard.py   (Streamlit UI)
  -> scripts/generate_monthly_report.py  (automation artifact)
  -> scripts/generate_business_snapshot.py (executive KPI snapshot)
  -> scripts/run_quality_checks.py       (visual quality report)
```

## Project structure

```text
.
├── .github/workflows/ci.yml
├── dashboards.py
├── Makefile
├── README.md
├── relatorio_vendas.csv
├── requirements.txt
├── scripts/
│   ├── generate_business_snapshot.py
│   ├── generate_monthly_report.py
│   └── run_quality_checks.py
├── src/
│   └── sales_automation/
│       ├── __init__.py
│       ├── dashboard.py
│       ├── data.py
│       └── metrics.py
└── tests/
    ├── fixtures/golden_sales.csv
    ├── test_contracts.py
    ├── test_data.py
    ├── test_metrics.py
    ├── test_regression_golden.py
    └── test_report_script.py
```

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run dashboard:

```bash
streamlit run dashboards.py
```

## Automation commands

```bash
make install    # install dependencies in local venv
make quality    # run tests and generate all artifacts (quality report, monthly summary, business snapshot)
make ci         # run full quality workflow locally
```

## CI pipeline (GitHub Actions)

The workflow in `.github/workflows/ci.yml` runs on push and pull requests:
1. install dependencies;
2. run automated quality checks;
3. generate monthly summary + business snapshot + test report JSON + visual HTML quality report;
4. upload all artifacts for review.

Quality checks include:
- data contract tests (required schema + valid ranges);
- regression tests with a fixed golden dataset;
- explicit quality gate (minimum pass rate in CI).

## Project highlights

- Clean modular Python code with clear separation of concerns.
- Reproducible analytics flow with automated checks.
- CI/CD mindset applied to data projects.
- Documentation designed for fast technical review.

## Next improvements (roadmap)

- Add containerized deployment (Docker + Streamlit Cloud).
- Add time-series forecasting module for planning scenarios.

## License

MIT
