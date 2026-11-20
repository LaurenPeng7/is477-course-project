# Interim Status Report

- **Project:** Food Price Inflation, Agrifood Employment, and Agrifood GHG Emissions in the United States
- **Team:** Lauren Peng, Vanisha Janaki, Kevin Ting, Ranveer Ganna
- **Milestone:** 3 – Interim Status Report

## 1. Summary of Progress

All three data sources have been obtained, described and cleaned and a first integrated data source now exists. This integration links the three cleaned sources on the basis of country (USA) and year and results in one observation per year between 2000 and 2021 (22 years). A post-integration quality assessment and a first exploration graph have been created as well. The remaining task is primarily that of putting together all of these individual components into an integrated, documented workflow: acquisition script with SHA-256 check, cleaning script for each dataset, workflow orchestration and necessary metadata and licensing documents.

## 2. Task Updates

### 2.1 Data acquisition — *complete (manual), automation pending*

The three datasets were downloaded from the World Bank Data360 portal and committed to the repository:

| Dataset | Raw file | Source | Granularity | Coverage |
|---|---|---|---|---|
| Consumer Price Indices (FAO_CP) | [`FAO_CP.csv.zip`](FAO_CP.csv.zip) | [Data360 FAO_CP](https://data360.worldbank.org/en/dataset/FAO_CP?country=USA) | Monthly, 207 areas | 2000-01 to 2026-03 |
| Employment in Agrifood Systems (WB_AFS) | [`AFS.csv`](AFS.csv) | [Data360 WB_AFS](https://data360.worldbank.org/en/dataset/WB_AFS?country=USA) | Annual, 172 countries | 2000–2024 |
| Emissions Totals (FAO_EMSTOT) | [`FAO_EMSTOT.csv`](FAO_EMSTOT.csv) | [Data360 FAO_EMSTOT](https://data360.worldbank.org/en/dataset/FAO_EMSTOT?country=USA) | Annual, 237 areas | 1961–2021 |

The CPI file is about 86 MB without compression and thus exceeds GitHub’s size limit of 50 MB; it is kept zipped. The download was performed manually, but a scripted download with SHA-256 check still needs to be created (see Section 3).

### 2.2 Data profiling and cleaning — *complete for all three datasets*

**Employment (Vanisha).** [`employment_cleaning.ipynb`](employment_cleaning.ipynb) profiles the raw dataset (4,287 rows, 41 columns, 172 countries) and discovers 74 missing employment values worldwide, but there are no missing values for the US. The script looks for duplicate rows and duplicate country–indicator–year combinations, filters data on the United States (25 annual rows), leaves only six columns with clear names and standardizes data types. Results: [`employment_cleaned.csv`](employment_cleaned.csv), [`employment_data_quality_report.csv`](employment_data_quality_report.csv), and [`employment_trend.png`](employment_trend.png).

**Consumer prices (Kevin).** [`FAO_CP_cleaning.py`](FAO_CP_cleaning.py) reads the CSV file straight from the zip file (ignores the `__MACOSX` folder inside the zip), drops the columns where all values are the same in each row, and renames three indicators as `cpi_general`, `cpi_food`, and `food_inflation_pct`. The dataset is pivoted from long to wide format (one row per country–month), and the rows where all three indicators are missing are dropped. In addition, flags are added for the partial year of 2026 and hyperinflation (>100%). Result: [`FAO_CP_cleaned.csv`](FAO_CP_cleaned.csv) (64,492 rows).

**Emissions (Lauren).** [`FAO_EMSTOT_cleaned.csv`](FAO_EMSTOT_cleaned.csv) retains all 12,639 rows and creates an `IS_AGGREGATE` flag to distinguish aggregates (North America, South Asia, World; 183 rows) from individual countries, thus making sure that aggregates won't be confused with countries when integrating data. There were no missing values identified by profiling, and the status of each value is "Normal value". The chart from EDA is placed in [`FAO_EMSTOT_EDA.png`](FAO_EMSTOT_EDA.png).

### 2.3 Data integration — *first version complete*

[`integrate_data.py`](integrate_data.py) builds the integrated dataset in five steps:

1. **Monthly to annual.** It restricts CPI to the US only and averages the months into calendar-year means. It drops years with an incomplete set of months, so that an incomplete year like 2026 (January–March only) won't affect the annual value.
2. **Standardize schemas.** It renames the key and value columns in each source to a shared schema: `year`, `cpi_food`, `cpi_general`, `food_inflation_pct`, `offfarm_employment_share_pct`, and `agrifood_ghg_kt_co2eq`.
3. **Validate keys.** It confirms that `year` is unique in every source before joining, and fails loudly if not.
4. **Join.** It inner-joins all three on `year` with pandas `validate="one_to_one"`.
5. **Check quality.** It writes a post-integration quality report.

Outputs: [`integrated_us_annual.csv`](integrated_us_annual.csv) and [`integration_quality_report.csv`](integration_quality_report.csv).

**Post-integration quality results:**

- **Completeness:** 22 out of 22 years in the 2000–2021 period are present, so there are no missing years. There is only one null: `food_inflation_pct` for 2000, since it is a year-over-year rate and requires the previous year's value.
- **Consistency:** No duplicate years. Each source contributes exactly one row per year.
- **Accuracy:** The employment shares are within the 0–100% interval, and emissions values are all positive. The mean of the food CPI in 2015 is 100.0, which agrees with 2015 being the base year (2015 = 100) according to the dataset description.
- **Timeliness:** The integration time span is restricted by the data available on emissions, as it is up until 2021. CPI and employment figures go up to 2025 and 2024 correspondingly.

### 2.4 Exploratory analysis — *started*

The script [`integrated_eda.py`](integrated_eda.py) calculates Pearson and Spearman correlation coefficients between each of the variables and agrifood emissions, saves them in [`integrated_correlations.csv`](integrated_correlations.csv) and produces an indexed trends graph (2000 = 100) as [`integrated_trends.png`](integrated_trends.png).

![Indexed US trends](integrated_trends.png)

Early results show only weak year-to-year associations with emissions:

| Variable | Pearson r | Spearman ρ |
|---|---|---|
| Food price inflation | −0.15 | −0.18 |
| Food CPI | 0.09 | 0.12 |
| Off-farm employment share | 0.05 | 0.08 |

During that period, the index of food CPI increased by about 54% and the off-farm employment share went down by about 15%. At the same time, emissions stayed almost the same, falling to around 90% of the value of the year 2000 in 2012 before recovering. With such a small sample of 22 annual observations, this is quite a preliminary result. The analysis phase will look at changes in yearly figures and lagged dependencies.

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

- **Timeline pushed back.** Cleaning was originally scheduled for 11/01 and integration for 11/08, but due to team members' schedules these were delayed until 11/19. A greater part of the remaining work is now planned to be done during Thanksgiving break, and the plan has been updated to match.
- **Analysis period fixed at 2000–2021.** This is the intersection of all three data sets, where the CPI and Employment data sets start in 2000 while the Emissions data set ends in 2021.
- **Monthly-to-annual rule defined.** Annual CPI values are calendar-year means of complete years only.
- **Employment indicator clarified.** The employment data set does not have an on-farm employment percentage; it just gives the off-farm employment percentage, which is used as the employment variable in our research question.
- **New tasks added for course requirements.** The acquisition script with checksums, the workflow orchestrator, and the metadata, licensing and reproducibility deliverables have now been included explicitly in the plan.
- **Response to Milestone 2.** After the Project Plan milestone, we made revisions to the plan in [`Milestone 2_ Project Plan IS 477 - Blue Guys.md`](Milestone%202_%20Project%20Plan%20IS%20477%20-%20Blue%20Guys.md) with a view to the new timeline. We have also added tasks for what the course requirements demanded but were missing in the original plan: acquisition script, workflow orchestrator, QA on all four dimensions, and metadata and licensing.

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

Contribution summaries from each team member:

### Ranveer Ganna
In relation to the current milestone, I created the integration phase and began the exploratory analysis phase. The integration phase is captured in [`integrate_data.py`](integrate_data.py), which transforms the monthly CPI data to annual averages for full years and harmonizes the three datasets. It ensures that `year` is a unique key in all sources and then joins the three datasets on year on a one-to-one basis to produce [`integrated_us_annual.csv`](integrated_us_annual.csv) from 2000 to 2021. The same code produces a post-integration quality report on the issues of completeness, consistency, accuracy, and timeliness; it tests whether the average CPI for food in 2015 is equal to the base year of 100. In addition to that, I wrote [`integrated_eda.py`](integrated_eda.py), which calculates correlations with agrifood emissions and generates the indexed trend chart. Lastly, I prepared this status report and the revised timeline and made sure both scripts can be run using a freshly cloned copy of the repository.

### Lauren Peng
In the role of the project coordinator, I created our GitHub repo, defined roles and timelines for the team, and added the raw data and initial project plan. In the current milestone, I was assigned to work on the Emissions Totals dataset (FAO_EMSTOT) from the World Bank Data360.

The dataset has been profiled and includes 12,639 annual observations, spanning over 237 areas and covering the period from 1961 to 2021. There are no missing values; all the observations have the status "Normal value". During my review of the areas, I discovered that the data included both individual countries and aggregated regions (North America, South Asia, and World), which would be counted twice if considered as individual countries. Therefore, I included an IS_AGGREGATE flag that allows separating 183 aggregated rows from the rest, and exported the cleaned output as FAO_EMSTOT_cleaned.csv for integration.

I also generated a descriptive view (FAO_EMSTOT_EDA.png) depicting the world total over time, top emitters in 2021, value distribution, and biggest variations since 1990. There are two facts that are important for our quality assessment. On one hand, the world total almost doubles between 1989 and 1990 (from 6.9 to 14.2 Gt CO2eq), suggesting that there is a change in what is being accounted for in the source since 1990 rather than an increase in emissions. On the other hand, the total of individual countries is not equal to the total World aggregate. Our analysis of US data uses the period from 2000 to 2021 and is therefore not affected by the 1990 gap, but we will document both as consistency limitations of the dataset.

### Vanisha Janaki
For this milestone, I focused on inspecting and cleaning the Employment in Agrifood System dataset (AFS.csv) from World Bank Data360. The original dataset contained 4,287 observations from 172 countries covering 2000–2024. I filtered it to US observations only, since our project focuses on the United States.

During inspection, I found that the dataset contained 25 annual observations for the US, and that the available employment indicator, Off-Farm Employment Share, is measured as a percentage. The US subset had no missing values or duplicate records; the full dataset had 74 missing employment values across other countries.

I created a Python notebook to document this process: examining column names and data types, checking for missing values and duplicates, filtering the data to the project's needs, and standardizing data types and syntax. I exported the cleaned dataset as a CSV file for integration with the other datasets.

One challenge was that the dataset only reports employment as an Off-Farm Employment Share percentage, with no separate On-Farm percentage, which we will need to consider when forming conclusions.

### Kevin Ting
I used a Python notebook to test and clean the Consumer Price Index data, then converted it into a script for easier reuse. The dataset was already fairly clean, but some columns held the same value in every row.

I dropped 29 columns because they had the same value for every row, and 7 more that were not relevant to our analysis (such as OBS_STATUS, which marked the existence of missing values). The remaining columns are iso3, country, year, month, cpi_food, cpi_general, food_inflation_pct, partial_year, and hyperinflation_flag. food_inflation_pct is missing for the first recorded year (2000), since it is a year-over-year statistic that needs two years of data; I consider this a fair trade-off.

I then exported the data as a CSV file to support the integration step.
