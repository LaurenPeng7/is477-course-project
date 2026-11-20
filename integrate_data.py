# Integration of the three cleaned datasets (US, annual)
#
# Inputs (all produced by the cleaning step):
#   FAO_CP_cleaned.csv       - monthly consumer price indices, all countries (Kevin)
#   employment_cleaned.csv   - annual off-farm employment share, USA (Vanisha)
#   FAO_EMSTOT_cleaned.csv   - annual agrifood GHG emissions, all countries (Lauren)
#
# Outputs:
#   integrated_us_annual.csv           - one row per year, all three sources joined
#   integration_quality_report.csv     - post-integration checks (coverage, nulls, ranges)
#
# Linkage key: country (ISO3 = USA) + calendar year.
# The CPI data is monthly, so it is first aggregated to calendar-year means
# before the join. Only years that appear in all three sources are kept
# (inner join); the coverage report records what was dropped and why.

from pathlib import Path
import pandas as pd

folder = Path(__file__).resolve().parent
COUNTRY = "USA"

# ---- 1. Consumer prices: monthly -> annual -------------------------------
cp = pd.read_csv(folder / "FAO_CP_cleaned.csv")
cp = cp[cp["iso3"] == COUNTRY]

cp_annual = (
    cp.groupby("year")
    .agg(
        cpi_food=("cpi_food", "mean"),
        cpi_general=("cpi_general", "mean"),
        food_inflation_pct=("food_inflation_pct", "mean"),
        cpi_months_reported=("cpi_food", "count"),
    )
    .reset_index()
)
# a partial year (e.g. 2026 only has Jan-Mar) would give a misleading annual mean
cp_annual = cp_annual[cp_annual["cpi_months_reported"] == 12]

# ---- 2. Employment (already US-only, annual) -----------------------------
emp = pd.read_csv(folder / "employment_cleaned.csv")
emp = emp.rename(columns={
    "Year": "year",
    "Employment_Share_Percent": "offfarm_employment_share_pct",
})[["year", "offfarm_employment_share_pct"]]

# ---- 3. Emissions: filter to USA, keep year + value ----------------------
ems = pd.read_csv(folder / "FAO_EMSTOT_cleaned.csv")
ems = ems[ems["REF_AREA"] == COUNTRY]
ems = ems.rename(columns={
    "TIME_PERIOD": "year",
    "OBS_VALUE": "agrifood_ghg_kt_co2eq",
})[["year", "agrifood_ghg_kt_co2eq"]]

# make sure the key really is unique in every source before joining
for name, d in [("cpi", cp_annual), ("employment", emp), ("emissions", ems)]:
    dupes = d["year"].duplicated().sum()
    if dupes:
        raise ValueError(f"{name} has {dupes} duplicate years - fix before integrating")

# ---- 4. Join on year -----------------------------------------------------
merged = (
    cp_annual.merge(emp, on="year", how="inner", validate="one_to_one")
    .merge(ems, on="year", how="inner", validate="one_to_one")
)
merged.insert(0, "iso3", COUNTRY)
merged = merged.sort_values("year").reset_index(drop=True)
merged.to_csv(folder / "integrated_us_annual.csv", index=False)

# ---- 5. Post-integration quality checks ----------------------------------
value_cols = ["cpi_food", "cpi_general", "food_inflation_pct",
              "offfarm_employment_share_pct", "agrifood_ghg_kt_co2eq"]
expected_years = set(range(merged["year"].min(), merged["year"].max() + 1))

checks = [
    ("cpi_years_available", f"{cp_annual.year.min()}-{cp_annual.year.max()} ({len(cp_annual)})"),
    ("employment_years_available", f"{emp.year.min()}-{emp.year.max()} ({len(emp)})"),
    ("emissions_years_available", f"{ems.year.min()}-{ems.year.max()} ({len(ems)})"),
    ("integrated_rows", len(merged)),
    ("integrated_year_range", f"{merged.year.min()}-{merged.year.max()}"),
    ("missing_years_in_range", sorted(expected_years - set(merged.year)) or "none"),
    ("duplicate_years", int(merged.year.duplicated().sum())),
    ("null_values_total", int(merged[value_cols].isna().sum().sum())),
    ("employment_share_within_0_100", bool(merged.offfarm_employment_share_pct.between(0, 100).all())),
    ("emissions_all_positive", bool((merged.agrifood_ghg_kt_co2eq > 0).all())),
    ("cpi_2015_mean_food_index", round(merged.loc[merged.year == 2015, "cpi_food"].mean(), 2)),
]
report = pd.DataFrame(checks, columns=["check", "result"])
report.to_csv(folder / "integration_quality_report.csv", index=False)

print(report.to_string(index=False))
print("\nintegrated:", merged.shape)
