# Cleaning + formatting for FAO_CP

import zipfile
from pathlib import Path
import pandas as pd

folder = Path(__file__).resolve().parent

# zip has a __MACOSX folder in it too, so grab the csv by name
with zipfile.ZipFile(folder / "FAO_CP.csv.zip") as z:
    df = pd.read_csv(z.open("FAO_CP.csv"))
print("raw:", df.shape)

# most columns are the same value in every row, only need these
df = df[["REF_AREA", "REF_AREA_LABEL", "INDICATOR", "TIME_PERIOD", "OBS_VALUE"]]
df.columns = ["iso3", "country", "indicator", "period", "value"]

df["indicator"] = df["indicator"].replace({
    "FAO_CP_23012": "cpi_general",
    "FAO_CP_23013": "cpi_food",
    "FAO_CP_23014": "food_inflation_pct",
})

df["year"] = df["period"].str[:4].astype(int)
df["month"] = df["period"].str[5:].astype(int)

# one row per country per month
df = df.pivot(index=["iso3", "country", "year", "month"],
              columns="indicator", values="value").reset_index()
df.columns.name = None
cols = ["cpi_general", "cpi_food", "food_inflation_pct"]
print("after pivot:", df.shape)

# how much data each country has per indicator
report = df.groupby(["iso3", "country"])[cols].apply(lambda x: x.notna().mean().round(3)).reset_index()
report.to_csv(folder / "FAO_CP_data_quality_report.csv", index=False)

print("nulls:")
print(df[cols].isna().sum())

# drop rows with nothing in them, leave the rest as is
df = df.dropna(subset=cols, how="all")

# 2026 only goes to March, and some inflation numbers are huge (hyperinflation)
df["partial_year"] = df["year"] == 2026
df["hyperinflation_flag"] = df["food_inflation_pct"] > 100

df.to_csv(folder / "FAO_CP_cleaned.csv", index=False)
print("cleaned:", df.shape)
