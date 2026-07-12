"""
convert_masterlist_to_json.py

Turns the official Department of Basic Education (DBE) EMIS Schools
Masterlist Excel file into the schools.json file the Vulani app
expects. Column mapping below is pre-filled for the "National -
ordinary schools.xlsx" download from
    education.gov.za/Programmes/EMIS/EMISDownloads.aspx

HOW TO USE
----------
1. Install dependencies once:
     pip install pandas openpyxl

2. Run:
     python convert_masterlist_to_json.py "National - ordinary schools.xlsx" -o schools.json

3. Copy the resulting schools.json into the same folder as
   school-registration-app.html.

If your file's column headers differ from the ones below, run with
--inspect first to print the real headers, then adjust COLUMN_MAP.
"""

import argparse
import json
import sys

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency. Run: pip install pandas openpyxl")


# ---------------------------------------------------------------
# Matches the real DBE "National - ordinary schools.xlsx" headers.
# ---------------------------------------------------------------
COLUMN_MAP = {
    "name":     "Official_Institution_Name",
    "province": "Province",
    "town":     "Town_City",
    "phase":    "Phase_PED",
    "sector":   "Sector",
}

# These three columns together let us classify each school as
# Township / Suburb / Rural for the app's area filter.
TOWNSHIP_COLUMN = "Township_Village"
SUBURB_COLUMN = "Suburb"
URBAN_RURAL_COLUMN = "Urban_Rural"

# Rows whose Status contains any of these words (case-insensitive)
# are dropped — closed / de-registered schools shouldn't appear
# as a place a parent can register their child.
STATUS_COLUMN = "Status"
EXCLUDE_STATUS_KEYWORDS = ["clos", "deregist", "de-regist"]


def load_file(path):
    if path.lower().endswith(".csv"):
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    return pd.read_excel(path, dtype=str, keep_default_na=False)


def inspect(path):
    df = load_file(path)
    print(f"\nColumns found in {path}:")
    for c in df.columns:
        print(f"  - {c}")
    print(f"\n{len(df)} rows.")
    print("\nIf these differ from COLUMN_MAP at the top of this script, update it, then re-run without --inspect.")


def classify_area(row):
    township = (row.get(TOWNSHIP_COLUMN, "") or "").strip()
    suburb = (row.get(SUBURB_COLUMN, "") or "").strip()
    urban_rural = (row.get(URBAN_RURAL_COLUMN, "") or "").strip().lower()

    if township:
        return "Township"
    if "rural" in urban_rural:
        return "Rural"
    if suburb:
        return "Suburb"
    if "urban" in urban_rural:
        return "Suburb"
    return "Unclassified"


def classify_phase(phase_raw):
    p = phase_raw.lower()
    if "sec" in p or "high" in p:
        return "High"
    if "combcombined" in p or "combined" in p:
        return "Combined"
    if "intermediate" in p:
        return "Primary"
    if "pre" in p:
        return "Pre-Primary"
    return "Primary"


def convert(paths, out_path):
    all_schools = []
    skipped_closed = 0
    skipped_not_public = 0

    for path in paths:
        df = load_file(path)
        missing = [v for v in COLUMN_MAP.values() if v not in df.columns]
        if missing:
            sys.exit(
                f"'{path}' is missing expected column(s): {missing}\n"
                f"Run with --inspect '{path}' to see its real column names, "
                f"then fix COLUMN_MAP at the top of this script."
            )

        for _, row in df.iterrows():
            sector = (row.get(COLUMN_MAP["sector"], "") or "").strip().lower()
            if sector and sector != "public":
                skipped_not_public += 1
                continue

            status = (row.get(STATUS_COLUMN, "") or "").strip().lower()
            if any(k in status for k in EXCLUDE_STATUS_KEYWORDS):
                skipped_closed += 1
                continue

            name = (row.get(COLUMN_MAP["name"], "") or "").strip()
            if not name:
                continue

            all_schools.append({
                "name": name,
                "province": (row.get(COLUMN_MAP["province"], "") or "").strip(),
                "town": (row.get(COLUMN_MAP["town"], "") or "").strip(),
                "phase": classify_phase((row.get(COLUMN_MAP["phase"], "") or "").strip()),
                "area": classify_area(row),
            })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_schools, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_schools)} schools to {out_path}")
    print(f"Skipped {skipped_closed} closed/de-registered schools and {skipped_not_public} non-public institutions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="Masterlist Excel/CSV file(s)")
    parser.add_argument("-o", "--output", default="schools.json", help="Output JSON path (default: schools.json)")
    parser.add_argument("--inspect", action="store_true", help="Just print column headers for the first file and exit")
    args = parser.parse_args()

    if args.inspect:
        inspect(args.files[0])
    else:
        convert(args.files, args.output)
