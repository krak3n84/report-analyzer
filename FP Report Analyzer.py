"""Compare the two newest Forward Power Problem Report CSV files.

The utility carries prior issue context into the newest report when the current
Issue field is empty, then writes a merged report and a list of newly appearing
sites. It reads and writes CSV files only; it does not connect to equipment.
"""

from datetime import datetime
from pathlib import Path
import re
import sys

import pandas as pd

REPORT_PREFIX = "Forward Power Problem Report"
REPORT_DATE_PATTERN = re.compile(
    r"Forward Power Problem Report\((?P<date>[A-Za-z]{3,9}\s+\d{1,2})\)\.csv$",
    re.IGNORECASE,
)
EXPECTED_COLUMNS = ["Site", "FP", "Issue"]


def extract_report_date(path: Path) -> datetime:
    """Parse the month/day embedded in a supported report filename."""
    match = REPORT_DATE_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"Unsupported report filename: {path.name}")

    date_text = match.group("date")
    for date_format in ("%b %d", "%B %d"):
        try:
            return datetime.strptime(date_text, date_format)
        except ValueError:
            continue

    raise ValueError(f"Could not parse report date from: {path.name}")


def discover_reports(directory: Path) -> list[Path]:
    """Return matching report files sorted newest first by filename date."""
    candidates = [
        path
        for path in directory.glob("*.csv")
        if path.name.lower().startswith(REPORT_PREFIX.lower())
    ]

    valid_reports = []
    for path in candidates:
        try:
            report_date = extract_report_date(path)
            valid_reports.append((report_date, path))
        except ValueError as error:
            print(f"Skipping {path.name}: {error}", file=sys.stderr)

    valid_reports.sort(key=lambda item: item[0], reverse=True)
    return [path for _, path in valid_reports]


def load_report(path: Path) -> pd.DataFrame:
    """Load and normalize the expected three-column report schema."""
    frame = pd.read_csv(path)

    if len(frame.columns) != len(EXPECTED_COLUMNS):
        raise ValueError(
            f"{path.name} has {len(frame.columns)} column(s); "
            f"expected exactly {len(EXPECTED_COLUMNS)}."
        )

    frame.columns = EXPECTED_COLUMNS
    frame["Site"] = frame["Site"].astype(str).str.strip()
    return frame


def compare_reports(newest: pd.DataFrame, previous: pd.DataFrame):
    """Carry prior issue context forward and identify newly appearing sites."""
    previous_issues = previous[["Site", "Issue"]].drop_duplicates(
        subset=["Site"], keep="last"
    )

    merged = pd.merge(
        newest,
        previous_issues,
        on="Site",
        how="left",
        suffixes=("", "_Previous"),
        validate="many_to_one",
    )

    merged["Issue"] = merged["Issue"].combine_first(merged["Issue_Previous"])
    merged.drop(columns=["Issue_Previous"], inplace=True)

    new_sites = merged.loc[
        ~merged["Site"].isin(previous["Site"]), ["Site", "FP", "Issue"]
    ].copy()

    return merged, new_sites


def main() -> int:
    working_directory = Path.cwd()
    reports = discover_reports(working_directory)

    if len(reports) < 2:
        print(
            "At least two valid Forward Power Problem Report CSV files are required.",
            file=sys.stderr,
        )
        return 1

    newest_path = reports[0]
    previous_path = reports[1]
    print(f"Comparing: {previous_path.name} -> {newest_path.name}")

    try:
        newest = load_report(newest_path)
        previous = load_report(previous_path)
        merged, new_sites = compare_reports(newest, previous)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        print(f"Report analysis failed: {error}", file=sys.stderr)
        return 1

    output_date = datetime.now().strftime("%Y-%m-%d")
    merged_output = working_directory / f"merged_sites_{output_date}.csv"
    new_sites_output = working_directory / f"new_sites_only_{output_date}.csv"

    merged.to_csv(merged_output, index=False)
    new_sites.to_csv(new_sites_output, index=False)

    print(f"Merged report: {merged_output.name}")
    print(f"New sites: {new_sites_output.name} ({len(new_sites)} row(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
