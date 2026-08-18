# Forward Power Report Analyzer

A small Python automation project for comparing sequential **Forward Power Problem Report** CSV files in an operations workflow.

The script reduces repetitive report review by carrying known issue context forward, identifying sites that are new in the latest report, and producing clean CSV outputs for follow-up.

## What It Does

1. Scans the working directory for CSV files whose names contain `Forward Power Problem Report`.
2. Extracts the report date from the filename, such as `Forward Power Problem Report(May 20).csv`.
3. Selects the two newest matching reports.
4. Normalizes the expected columns as `Site`, `FP`, and `Issue`.
5. Carries the previous report's `Issue` value forward when the current report does not already contain one.
6. Identifies sites that appear in the newest report but not in the previous report.
7. Writes two timestamped CSV files:
   - `merged_sites_YYYY-MM-DD.csv`
   - `new_sites_only_YYYY-MM-DD.csv`

## Why I Built It

Operational reports often contain a mix of continuing issues and newly appearing conditions. Re-checking the same rows and manually transferring context creates unnecessary operator work and increases the chance that a new item gets overlooked.

This project turns that comparison into a repeatable process so the operator can focus on investigation and follow-up rather than manual reconciliation.

## Requirements

- Python 3.x
- pandas

Install the dependency:

```bash
python -m pip install -r requirements.txt
```

## Usage

Place at least two matching report files in the project directory, then run:

```bash
python "FP Report Analyzer.py"
```

Example input filenames:

```text
Forward Power Problem Report(May 19).csv
Forward Power Problem Report(May 20).csv
```

Example console output:

```text
Comparing: Forward Power Problem Report(May 19).csv -> Forward Power Problem Report(May 20).csv
Merged with carried Issues: merged_sites_2026-08-17.csv
New Sites: new_sites_only_2026-08-17.csv
```

## Expected Input

The current script expects each report to contain three columns representing:

| Column | Purpose |
|---|---|
| `Site` | Site or location identifier |
| `FP` | Forward-power value or report field |
| `Issue` | Operator notes or issue context |

The project intentionally operates on report files only. It does not connect to or modify network or broadcast equipment.

## Operational Value

- Reduces repetitive comparison work
- Preserves known issue context between reports
- Surfaces newly appearing sites quickly
- Creates consistent output for review or downstream processing
- Provides a simple example of using Python to improve an operations workflow

## Scope

This is a focused utility rather than a full monitoring platform. Future improvements could include schema validation, configurable input columns, logging, automated tests, and additional trend reporting.

## License

Use and adapt this project as appropriate for your own workflow and data-handling requirements.
