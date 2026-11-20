# Exploratory analysis of the integrated US dataset
#
# Input:  integrated_us_annual.csv  (from integrate_data.py)
# Output: integrated_correlations.csv  - Pearson + Spearman correlations with emissions
#         integrated_trends.png        - indexed trends of the three sources, 2000 = 100

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

folder = Path(__file__).resolve().parent
df = pd.read_csv(folder / "integrated_us_annual.csv")

target = "agrifood_ghg_kt_co2eq"
drivers = ["food_inflation_pct", "cpi_food", "offfarm_employment_share_pct"]

rows = []
for col in drivers:
    rows.append({
        "variable": col,
        "pearson_r": round(df[col].corr(df[target], method="pearson"), 3),
        "spearman_rho": round(df[col].corr(df[target], method="spearman"), 3),
        "n_years": int(df[[col, target]].dropna().shape[0]),
    })
corr = pd.DataFrame(rows)
corr.to_csv(folder / "integrated_correlations.csv", index=False)
print(corr.to_string(index=False))

# indexed trend chart so the three very different units fit on one axis
base = df.iloc[0]
fig, ax = plt.subplots(figsize=(9, 5))
for col, label in [
    ("cpi_food", "Food CPI"),
    ("offfarm_employment_share_pct", "Off-farm employment share"),
    ("agrifood_ghg_kt_co2eq", "Agrifood GHG emissions"),
]:
    ax.plot(df["year"], df[col] / base[col] * 100, marker="o", markersize=3, label=label)
ax.axhline(100, color="grey", linewidth=0.8, linestyle="--")
ax.set_title(f"United States, {df.year.min()}-{df.year.max()} (indexed, {int(base.year)} = 100)")
ax.set_xlabel("Year")
ax.set_ylabel("Index")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(folder / "integrated_trends.png", dpi=150)
print("saved integrated_trends.png")
