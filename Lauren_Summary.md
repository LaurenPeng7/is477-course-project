# Lauren Peng

For this milestone, I cleaned the FAO agrifood-system emissions dataset (FAO_EMSTOT) and did the exploratory data analysis.

## Data cleaning
- Checked the raw file (12,639 rows, 37 columns) for missing values and duplicates and found none.
- Added an `IS_AGGREGATE` column to separate regional and world aggregates from individual countries.
- Saved the result as `FAO_EMSTOT_cleaned.csv`.

## Exploratory data analysis
- Made a four-panel overview figure (`FAO_EMSTOT_EDA.png`).
- Found a jump in the world total between 1989 and 1990, likely from a change in country coverage.
- Identified the top emitters in 2021 (China, Brazil, India, US).
- Found a strongly right-skewed distribution, so a log scale is needed.
- Found the largest increases (China, India) and decreases (Indonesia, Brazil) since 1990.
