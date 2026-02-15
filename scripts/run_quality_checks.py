from __future__ import annotations

import html
import json
from pathlib import Path
import sys
import time
import unittest
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from scripts.generate_monthly_report import generate_monthly_summary

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
JSON_REPORT = ARTIFACTS_DIR / "test_report.json"
HTML_REPORT = ARTIFACTS_DIR / "quality_report.html"
MIN_PASS_RATE = 100.0

TEST_PURPOSES = {
    "test_required_columns_exist": "Confirms required business columns are present in incoming data.",
    "test_numeric_ranges_are_valid": "Confirms numeric values stay within valid business ranges.",
    "test_dates_are_not_in_the_future": "Confirms transaction dates are realistic and not future-dated.",
    "test_dataset_uses_north_america_business_labels": "Confirms dataset labels match a North America business context.",
    "test_filter_sales_data_by_month_city": "Confirms dashboard filters return only selected month and city.",
    "test_load_sales_data_has_expected_schema": "Confirms data schema is stable and dates are sorted for analytics.",
    "test_compute_kpis_returns_positive_values": "Confirms core business KPIs are computed correctly.",
    "test_revenue_by_city_is_sorted_desc": "Confirms city ranking logic is valid for executive reporting.",
    "test_kpis_match_expected_values": "Confirms KPI calculations remain stable on a fixed regression dataset.",
    "test_city_ranking_is_stable": "Confirms city ordering stays stable on a fixed regression dataset.",
    "test_generate_monthly_summary_creates_csv": "Confirms monthly automated report artifact is generated.",
}


class TimedTestResult(unittest.TextTestResult):
    def startTest(self, test: unittest.TestCase) -> None:
        self._start_time = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test: unittest.TestCase) -> None:
        elapsed = time.perf_counter() - self._start_time
        if not hasattr(self, "timings"):
            self.timings = {}
        self.timings[str(test)] = elapsed
        super().stopTest(test)


class TimedTextTestRunner(unittest.TextTestRunner):
    resultclass = TimedTestResult


def _test_status(result: TimedTestResult, test_name: str) -> str:
    for test, _ in result.failures:
        if str(test) == test_name:
            return "FAILED"
    for test, _ in result.errors:
        if str(test) == test_name:
            return "ERROR"
    for test, _ in result.skipped:
        if str(test) == test_name:
            return "SKIPPED"
    return "PASSED"


def _extract_method_name(test_id: str) -> str:
    # Example input: test_fn (module.Class.test_fn)
    method_part = test_id.split(" ", 1)[0]
    return method_part.strip()


def _risk_level(pass_rate: float, failures: int, errors: int) -> str:
    if errors > 0 or failures > 0:
        if pass_rate < 0.8:
            return "High"
        return "Medium"
    return "Low"


def run_quality_checks() -> int:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(PROJECT_ROOT / "tests"), pattern="test_*.py")

    runner = TimedTextTestRunner(verbosity=2)
    result: TimedTestResult = runner.run(suite)

    monthly_report = generate_monthly_summary()

    rows = []
    for test_name in sorted(result.timings.keys()):
        method_name = _extract_method_name(test_name)
        rows.append(
            {
                "test": test_name,
                "method": method_name,
                "status": _test_status(result, test_name),
                "duration_seconds": round(result.timings[test_name], 4),
                "purpose": TEST_PURPOSES.get(method_name, "Automated validation for data and reporting behavior."),
            }
        )

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors) - len(result.skipped)
    pass_rate = (passed / total * 100.0) if total else 0.0
    failed_count = len(result.failures)
    error_count = len(result.errors)
    skipped_count = len(result.skipped)
    meets_gate = (
        failed_count == 0
        and error_count == 0
        and skipped_count == 0
        and pass_rate >= MIN_PASS_RATE
    )
    risk = _risk_level(pass_rate / 100.0, failed_count, error_count)

    payload = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed_count,
            "errors": error_count,
            "skipped": skipped_count,
            "success": meets_gate,
            "pass_rate": round(pass_rate, 2),
            "quality_gate": {
                "min_pass_rate": MIN_PASS_RATE,
                "met": meets_gate,
            },
            "risk_level": risk,
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "generated_at_unix": int(time.time()),
        },
        "tests": rows,
        "artifacts": {
            "monthly_summary_csv": str(monthly_report.relative_to(PROJECT_ROOT)),
        },
    }

    JSON_REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    success = payload["summary"]["success"]
    status_color = "#0f766e" if success else "#b91c1c"
    accent = "#1d4ed8"

    html_rows = "\n".join(
        [
            "<tr>"
            f"<td><code>{html.escape(row['method'])}</code><div class='purpose'>{html.escape(row['purpose'])}</div></td>"
            f"<td><span class='pill {row['status'].lower()}'>{row['status']}</span></td>"
            f"<td>{row['duration_seconds']:.4f}s</td>"
            "</tr>"
            for row in payload["tests"]
        ]
    )

    html_content = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Quality Report</title>
  <style>
    :root {{
      --bg: #f3f7fb;
      --panel: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --border: #dbe3ef;
      --accent: {accent};
      --status: {status_color};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: var(--text); background: radial-gradient(circle at top right, #dbeafe, transparent 40%), var(--bg); }}
    .container {{ max-width: 1080px; margin: 0 auto; padding: 28px 18px 36px; }}
    .hero {{ background: linear-gradient(130deg, #0b3b66, #0f172a 60%); color: #fff; border-radius: 18px; padding: 22px; box-shadow: 0 18px 40px rgba(15, 23, 42, 0.25); }}
    .hero-top {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; }}
    .hero h1 {{ margin: 0; font-size: 28px; letter-spacing: 0.2px; }}
    .hero p {{ margin: 8px 0 0; color: #dbeafe; max-width: 780px; line-height: 1.4; }}
    .badge {{ background: {status_color}; border: 1px solid rgba(255,255,255,0.3); border-radius: 999px; padding: 8px 14px; font-weight: 700; min-width: 130px; text-align: center; }}
    .meta {{ margin-top: 10px; font-size: 13px; color: #cbd5e1; }}

    .summary {{ margin-top: 16px; display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }}
    .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 14px; box-shadow: 0 4px 12px rgba(15,23,42,0.05); }}
    .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .value {{ margin-top: 6px; font-size: 30px; font-weight: 800; line-height: 1; }}
    .sub {{ margin-top: 4px; font-size: 12px; color: var(--muted); }}
    .artifact-path {{ margin-top: 6px; font-size: 12px; color: #334155; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; overflow-wrap: anywhere; word-break: break-word; }}

    .score-wrap {{ margin-top: 16px; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }}
    .score-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
    .score-label {{ font-weight: 700; }}
    .score-value {{ font-weight: 800; color: var(--accent); }}
    .bar {{ width: 100%; height: 12px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, #22c55e, #16a34a); width: {payload['summary']['pass_rate']}%; transition: width .35s ease; }}

    .plain {{ margin-top: 16px; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }}
    .plain h2 {{ margin: 0 0 10px; font-size: 20px; }}
    .plain ul {{ margin: 0; padding-left: 18px; color: #1e293b; line-height: 1.5; }}

    .table-wrap {{ margin-top: 16px; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; padding: 12px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    th {{ background: #f8fafc; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: #334155; }}
    tr:last-child td {{ border-bottom: none; }}
    .purpose {{ margin-top: 6px; font-size: 12px; color: #475569; max-width: 760px; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-weight: 700; font-size: 12px; border: 1px solid; }}
    .pill.passed {{ color: #166534; background: #dcfce7; border-color: #86efac; }}
    .pill.failed, .pill.error {{ color: #991b1b; background: #fee2e2; border-color: #fca5a5; }}
    .pill.skipped {{ color: #92400e; background: #fef3c7; border-color: #fcd34d; }}

    @media (max-width: 720px) {{
      .hero h1 {{ font-size: 22px; }}
      .value {{ font-size: 26px; }}
      th, td {{ padding: 10px; }}
    }}
  </style>
</head>
<body>
  <main class=\"container\">
    <section class=\"hero\">
      <div class=\"hero-top\">
        <h1>Automation Quality Report</h1>
        <div class=\"badge\">{'PASS' if success else 'REVIEW NEEDED'}</div>
      </div>
      <p>This report shows whether the sales analytics pipeline is reliable for business decisions. It is designed for both technical and non-technical reviewers.</p>
      <div class=\"meta\">Generated: {payload['summary']['generated_at_utc']}</div>
    </section>

    <section class=\"summary\">
      <div class=\"card"><div class=\"label\">Total tests</div><div class=\"value\">{payload['summary']['total']}</div></div>
      <div class=\"card"><div class=\"label\">Pass rate</div><div class=\"value\">{payload['summary']['pass_rate']}%</div></div>
      <div class=\"card"><div class=\"label\">Risk level</div><div class=\"value\">{payload['summary']['risk_level']}</div><div class=\"sub\">Lower is better</div></div>
      <div class=\"card"><div class=\"label\">Failures + Errors</div><div class=\"value\">{payload['summary']['failed'] + payload['summary']['errors']}</div></div>
      <div class=\"card"><div class=\"label\">Quality gate</div><div class=\"value\">{'MET' if payload['summary']['quality_gate']['met'] else 'NOT MET'}</div><div class=\"sub\">Minimum pass rate: {payload['summary']['quality_gate']['min_pass_rate']}%</div></div>
      <div class=\"card"><div class=\"label\">Data artifact</div><div class=\"artifact-path\">{html.escape(payload['artifacts']['monthly_summary_csv'])}</div></div>
    </section>

    <section class=\"score-wrap\">
      <div class=\"score-head\">
        <div class=\"score-label\">Quality score</div>
        <div class=\"score-value\">{payload['summary']['pass_rate']} / 100</div>
      </div>
      <div class=\"bar\"><div class=\"bar-fill\"></div></div>
    </section>

    <section class=\"plain\">
      <h2>What this means in plain language</h2>
      <ul>
        <li>The dashboard calculations are being checked automatically before sharing results.</li>
        <li>Filter behavior and ranking logic are validated to reduce reporting mistakes.</li>
        <li>The monthly CSV summary is generated automatically and ready for stakeholders.</li>
      </ul>
    </section>

    <section class=\"table-wrap\">
      <table>
        <thead>
          <tr><th>Validation</th><th>Status</th><th>Duration</th></tr>
        </thead>
        <tbody>
          {html_rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""

    HTML_REPORT.write_text(html_content, encoding="utf-8")
    print(f"JSON report generated at: {JSON_REPORT}")
    print(f"HTML report generated at: {HTML_REPORT}")

    return 0 if meets_gate else 1


if __name__ == "__main__":
    raise SystemExit(run_quality_checks())
