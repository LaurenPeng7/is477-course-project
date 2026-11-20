"""Clean and standardization for FAO CP Data

"""
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_ZIP = ROOT / "FAO_CP.csv.zip"
CLEANED = ROOT / "FAO_CP_cleaned.csv"
REPORT = ROOT / "FAO_CP_data_quality_report.csv"

INDICATORS = {
    "FAO_CP_23012": "cpi_general",
    "FAO_CP_23013": "cpi_food",
    "FAO_CP_23014": "food_inflation_pct",
}
VALUE_COLS = list(INDICATORS.values())
KEYS = ["iso3", "country", "year", "month"]
HYPERINFLATION_PCT = 100


def load_raw():
    with zipfile.ZipFile(RAW_ZIP) as z:
        with z.open("FAO_CP.csv") as f:
            return pd.read_csv(f, dtype=str)


def standardize(raw):
    constant = [c for c in raw.columns if raw[c].nunique(dropna=False) == 1]
    print(f"Dropping {len(constant)} columns that have the same value in every row")

    df = raw[["REF_AREA", "REF_AREA_LABEL", "INDICATOR", "TIME_PERIOD", "OBS_VALUE"]]
    df = df.rename(columns={
        "REF_AREA": "iso3",
        "REF_AREA_LABEL": "country",
        "INDICATOR": "indicator",
        "TIME_PERIOD": "period",
        "OBS_VALUE": "value",
    })

    unknown = set(df["indicator"]) - set(INDICATORS)
    if unknown:
        raise ValueError(f"Unexpected indicator codes: {unknown}")
    df["indicator"] = df["indicator"].map(INDICATORS)

    dates = pd.to_datetime(df["period"], format="%Y-%m", errors="coerce")
    if dates.isna().any():
        raise ValueError(f"{dates.isna().sum()} dates are not in YYYY-MM format")
    df["year"] = dates.dt.year
    df["month"] = dates.dt.month

    df["iso3"] = df["iso3"].str.strip().str.upper()
    df["country"] = df["country"].str.strip()
    if not df["iso3"].str.fullmatch(r"[A-Z]{3}").all():
        raise ValueError("Found country codes that are not 3-letter ISO codes")

    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    if df.duplicated(KEYS + ["indicator"]).any():
        raise ValueError("Found duplicate country/indicator/month rows")
    wide = df.pivot(index=KEYS, columns="indicator", values="value").reset_index()
    wide.columns.name = None
    return wide[KEYS + VALUE_COLS].sort_values(KEYS).reset_index(drop=True)


def quality_report(df):
    report = (
        df.groupby(["iso3", "country"])[VALUE_COLS]
        .apply(lambda g: g.notna().mean().round(3))
        .add_suffix("_share_present")
        .reset_index()
    )
    share_cols = [c for c in report.columns if c.endswith("_share_present")]
    missing = (report[share_cols] == 0).any(axis=1).sum()
    print(f"{missing} countries have no data for an one indicator")
    return report


def clean_missing(df):
    print("Null count", df[VALUE_COLS].isna().sum().to_dict())

    all_null = df[VALUE_COLS].isna().all(axis=1)
    df = df[~all_null].copy()

    df["has_missing_indicator"] = df[VALUE_COLS].isna().any(axis=1)

    last_year = df["year"].max()
    last_month = df.loc[df["year"] == last_year, "month"].max()
    df["partial_year"] = (df["year"] == last_year) & (last_month < 12)

    df["hyperinflation_flag"] = df["food_inflation_pct"] > HYPERINFLATION_PCT
    return df


def main():
    raw = load_raw()
    print(f"Loaded {len(raw):,} rows x {raw.shape[1]} columns")

    wide = standardize(raw)
    print(f"Reshaped to {len(wide):,} country-month rows")

    quality_report(wide).to_csv(REPORT, index=False)
    cleaned = clean_missing(wide)
    cleaned.to_csv(CLEANED, index=False)

    print(f"Saved {CLEANED.name} ({len(cleaned):,} rows) and {REPORT.name}")


if __name__ == "__main__":
    main()
