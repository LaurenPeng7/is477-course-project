# Interim Status Report

- **Project:** Food Price Inflation, Agrifood Employment, and Agrifood GHG Emissions in the United States
- **Team:** Lauren Peng, Vanisha Janaki, Kevin Ting, Ranveer Ganna
- **Milestone:** 3 – Interim Status Report

## 1. Summary of Progress

All three datasets have been acquired, profiled, and cleaned, and a first version of the integrated dataset now exists. The integration joins the three cleaned sources on country (USA) and calendar year, producing one row per year for **2000–2021 (22 years)**. A post-integration quality check and a first exploratory chart have also been produced. The remaining work is mainly about turning these separate pieces into a reproducible, documented pipeline: an acquisition script with SHA-256 checks, script-based cleaning for every dataset, an orchestrating workflow, and the required metadata and licensing files.

## 2. Task Updates

### 2.1 Data acquisition — *complete (manual), automation pending*

The three datasets were downloaded from the World Bank Data360 portal and committed to the repository:

| Dataset | Raw file | Source | Granularity | Coverage |
|---|---|---|---|---|
| Consumer Price Indices (FAO_CP) | [`FAO_CP.csv.zip`](FAO_CP.csv.zip) | [Data360 FAO_CP](https://data360.worldbank.org/en/dataset/FAO_CP?country=USA) | Monthly, 207 areas | 2000-01 to 2026-03 |
| Employment in Agrifood Systems (WB_AFS) | [`AFS.csv`](AFS.csv) | [Data360 WB_AFS](https://data360.worldbank.org/en/dataset/WB_AFS?country=USA) | Annual, 172 countries | 2000–2024 |
| Emissions Totals (FAO_EMSTOT) | [`FAO_EMSTOT.csv`](FAO_EMSTOT.csv) | [Data360 FAO_EMSTOT](https://data360.worldbank.org/en/dataset/FAO_EMSTOT?country=USA) | Annual, 237 areas | 1961–2021 |

The CPI file is about 86 MB uncompressed, above GitHub's 50 MB limit, so it is stored zipped. The downloads were done by hand; a scripted download with SHA-256 integrity checks is still to be written (see Section 3).

### 2.2 Data profiling and cleaning — *complete for all three datasets*

**Employment (Vanisha).** [`employment_cleaning.ipynb`](employment_cleaning.ipynb) profiles the raw file (4,287 rows, 41 columns, 172 countries) and finds 74 missing employment values globally but none for the US. It checks for duplicate rows and duplicate country–indicator–year combinations, filters to the United States (25 annual rows), keeps six relevant columns with readable names, and standardizes data types. Outputs: [`employment_cleaned.csv`](employment_cleaned.csv), [`employment_data_quality_report.csv`](employment_data_quality_report.csv), and [`employment_trend.png`](employment_trend.png).

**Consumer prices (Kevin).** [`FAO_CP_cleaning.py`](FAO_CP_cleaning.py) reads the CSV directly from the zip (ignoring a `__MACOSX` entry), drops columns that hold the same value in every row, and renames the three indicators to `cpi_general`, `cpi_food`, and `food_inflation_pct`. It then pivots the data from long to wide (one row per country–month), removes rows where all three indicators are empty, and adds flags for the partial year 2026 and for hyperinflation (>100%). Output: [`FAO_CP_cleaned.csv`](FAO_CP_cleaned.csv), with 64,492 rows.

**Emissions (Lauren).** [`FAO_EMSTOT_cleaned.csv`](FAO_EMSTOT_cleaned.csv) keeps all 12,639 observations and adds an `IS_AGGREGATE` flag. That flag separates regional aggregates (North America, South Asia, World; 183 rows) from individual countries, so aggregates cannot be mistaken for countries during integration. The profiling found no missing values, and every observation has status "Normal value". An EDA chart is in [`FAO_EMSTOT_EDA.png`](FAO_EMSTOT_EDA.png).

### 2.3 Data integration — *first version complete*

[`integrate_data.py`](integrate_data.py) builds the integrated dataset in five steps:

1. **Monthly to annual.** It filters CPI to the US and aggregates months to calendar-year means. Years without all 12 months are dropped so a partial year (2026: January–March only) cannot distort an annual value.
2. **Standardize schemas.** It renames the key and value columns in each source to a shared schema: `year`, `cpi_food`, `cpi_general`, `food_inflation_pct`, `offfarm_employment_share_pct`, and `agrifood_ghg_kt_co2eq`.
3. **Validate keys.** It confirms that `year` is unique in every source before joining, and fails loudly if not.
4. **Join.** It inner-joins all three on `year` with pandas `validate="one_to_one"`.
5. **Check quality.** It writes a post-integration quality report.

Outputs: [`integrated_us_annual.csv`](integrated_us_annual.csv) and [`integration_quality_report.csv`](integration_quality_report.csv).

**Post-integration quality results:**

- **Completeness:** 22 of 22 years in 2000–2021 are present, with no gaps. There is one null: `food_inflation_pct` for 2000, because it is a year-over-year rate and needs a prior year.
- **Consistency:** No duplicate years. Each source contributes exactly one row per year.
- **Accuracy:** Employment shares fall within 0–100%, and all emissions values are positive. The 2015 mean of the food CPI is 100.0, matching the dataset's stated base year (2015 = 100), which is a useful sanity check on the monthly-to-annual aggregation.
- **Timeliness:** The integrated range is limited by the emissions data, which ends in 2021. The CPI and employment data extend to 2025 and 2024 respectively.

### 2.4 Exploratory analysis — *started*

[`integrated_eda.py`](integrated_eda.py) computes Pearson and Spearman correlations between each variable and agrifood emissions and saves them to [`integrated_correlations.csv`](integrated_correlations.csv). It also plots indexed trends (2000 = 100) in [`integrated_trends.png`](integrated_trends.png).

![Indexed US trends](integrated_trends.png)

Early results show only weak year-to-year associations with emissions:

| Variable | Pearson r | Spearman ρ |
|---|---|---|
| Food price inflation | −0.15 | −0.18 |
| Food CPI | 0.09 | 0.12 |
| Off-farm employment share | 0.05 | 0.08 |

Over the period, the food CPI rose about 54% and the off-farm employment share fell about 15%. Emissions stayed roughly flat, dipping to about 90% of their 2000 level around 2012 before recovering. With only 22 annual observations, these results are preliminary. The analysis phase will look at year-over-year changes and lagged relationships instead of levels alone.

## 3. Updated Timeline

| Task | Owner(s) | Original date | Status | New / actual date |
|---|---|---|---|---|
| Finalize plan | Everyone | 10/22 | ✅ Done | 10/22 |
| Acquire datasets | Vanisha, Lauren | 10/22 | ✅ Done (manual) | 10/22 |
| Profile & clean employment data | Vanisha | 11/01 | ✅ Done | 11/19 |
| Profile & clean CPI data | Kevin | 11/01 | ✅ Done | 11/19 |
| Profile & clean emissions data | Lauren | 11/01 | ✅ Done | 11/19 |
| Integrate datasets + post-integration QA | Ranveer, Kevin | 11/08 | ✅ First version | 11/19 |
| Acquisition script with SHA-256 checks | Vanisha | — | ⏳ To do | 11/26 |
| Convert notebook/manual cleaning to scripts; fix file paths | Vanisha, Lauren | — | ⏳ To do | 11/26 |
| Pre-integration quality write-up (accuracy, completeness, timeliness, consistency) | Lauren, Vanisha | — | ⏳ To do | 11/26 |
| Workflow orchestration (Snakefile or `run_all` script) | Kevin, Ranveer | — | ⏳ To do | 11/30 |
| Analysis & visualizations | Ranveer, Kevin | 11/22 | 🔄 Started | 11/30 |
| `requirements.txt`, licenses, data dictionary, metadata file | Lauren, Kevin | — | ⏳ To do | 12/03 |
| Final README report | Everyone | 12/06 | ⏳ To do | 12/06 |
| Fresh-clone reproducibility test + final release | Lauren | Before submission | ⏳ To do | Before deadline |

## 4. Changes to the Project Plan

- **Timeline pushed back.** The original dates for cleaning (11/01) and integration (11/08) slipped because of team members' schedules. Cleaning and a first integration were completed on 11/19. More of the remaining work is now planned for Thanksgiving break, and the plan has been updated to match.
- **Analysis period fixed at 2000–2021.** This is the overlap of all three datasets: CPI and employment begin in 2000, and emissions end in 2021.
- **Monthly-to-annual rule defined.** Annual CPI values are calendar-year means of complete years only.
- **Employment indicator clarified.** The employment dataset only provides the off-farm employment share, not a separate on-farm measure, so the research question uses off-farm share as its employment variable.
- **New tasks added for course requirements.** The plan now explicitly includes the acquisition script with checksums, the workflow orchestrator, and the metadata, licensing, and reproducibility deliverables.
- **Response to Milestone 2.** After the project plan milestone, we revised the plan in [`Milestone 2_ Project Plan IS 477 - Blue Guys.md`](Milestone%202_%20Project%20Plan%20IS%20477%20-%20Blue%20Guys.md) to reflect the new timeline. We also added the tasks above for the course requirements the original plan did not yet cover: the acquisition script, workflow orchestration, quality assessment across all four dimensions, and metadata and licensing.

## 5. Challenges and How We Are Addressing Them

| Challenge | Resolution / plan |
|---|---|
| Different time granularity (monthly CPI vs. annual employment and emissions) | Resolved: CPI aggregated to complete calendar years before the join. |
| Different year ranges across sources | Resolved: inner join on year. The coverage of each source is recorded in the integration quality report. |
| Regional aggregates mixed in with countries in emissions data | Resolved: `IS_AGGREGATE` flag added during cleaning, and integration filters by ISO3 code. |
| CPI raw file exceeds GitHub's 50 MB limit | Resolved: stored as a zip, and the cleaning script reads from the zip directly. |
| Small number of integrated observations (22 years) limits statistical power | Plan: report correlations with this caveat, and look at year-over-year changes and lags. A comparison with other countries may be added, since the raw files already cover 170+ countries. |
| Pipeline not yet reproducible: the employment notebook reads `WB_AFS.csv` (the committed file is `AFS.csv`), the emissions cleaning has no script, and an older duplicate CPI file (`fao_cp_clean.csv`) remains | Plan: convert all cleaning steps into standalone scripts with relative paths, remove the outdated file, and connect everything through one workflow by 11/30. |
| Off-farm employment share is the only employment measure available | Documented as a limitation and reflected in how the findings are interpreted. |

## 6. Individual Contributions

Each team member adds and commits their own summary below.

### Ranveer Ganna
For this milestone I built the integration step and started the exploratory analysis. I wrote [`integrate_data.py`](integrate_data.py), which converts the monthly CPI data to annual means for complete years and puts all three cleaned datasets into a common schema. It checks that `year` is a unique key in every source, then joins the three datasets one-to-one on year. The result is [`integrated_us_annual.csv`](integrated_us_annual.csv), covering 2000–2021. The same script produces a post-integration quality report covering completeness, consistency, accuracy, and timeliness, including a check that the 2015 food CPI average equals the base value of 100. I also wrote [`integrated_eda.py`](integrated_eda.py), which computes correlations with agrifood emissions and produces the indexed trend chart. Finally, I drafted this status report and the updated timeline.

### Lauren Peng
*[Lauren to add and commit]*

### Vanisha Janaki
*[Vanisha to add and commit]*

### Kevin Ting
*[Kevin to add and commit]*
