# Changelog

All notable changes to this project are documented in this file.

## [v1.0.0] - 2026-02-15

### Added
- Modular architecture under `src/sales_automation` for data loading, KPI metrics and dashboard rendering.
- Automated quality workflow with visual report generation:
  - `artifacts/quality_report.html`
  - `artifacts/test_report.json`
- Monthly automation artifact generation:
  - `artifacts/monthly_summary.csv`
- Executive business snapshot generation:
  - `artifacts/business_snapshot.json`
  - `artifacts/business_snapshot.md`
- Comprehensive tests:
  - data contract checks
  - regression tests using a fixed golden dataset
  - KPI and filtering validations
- CI pipeline via GitHub Actions to run quality checks and upload artifacts.

### Changed
- Dataset translated to English and adapted to a North American retail context.
- README upgraded to a complete case-study format with architecture, metrics and execution workflow.
- Makefile simplified to essential commands: `install`, `run`, `quality`, `ci`.
