# Tableau Dashboard Guide

## Prepare the data source

1. Start the Flask application once, or run the preprocessing workflow, so `data/processed/heart_cleaned.csv` is available.
2. Alternatively, use **Download processed CSV** in the web application. The download contains the cleaned source fields plus `sex_label`, `disease_label`, and `age_group`.
3. In Tableau Desktop, choose **Connect → Text File** and select `heart_disease_cleaned.csv` (or `data/processed/heart_cleaned.csv`).
4. Confirm that `target` is numeric and that `age_group`, `sex_label`, and `disease_label` are dimensions.

## Build the worksheets

1. **Outcome summary:** use `disease_label` and `Number of Records` for the two-group distribution.
2. **Disease-present count:** use `SUM([target])`. This is valid because preprocessing converts the original target to 0 or 1.
3. **Disease proportion by age:** place `age_group` on Rows and `AVG([target])` on Columns; format the measure as a percentage and show `Number of Records` in the tooltip.
4. **Sex comparison:** use `sex_label` with `AVG([target])`; include `Number of Records` so group sizes remain visible.
5. **Clinical measures:** compare `AVG([chol])` and `AVG([trestbps])` by `disease_label`, with units in the axis titles.
6. **Optional age profile:** use `age_group` and `Number of Records` to show the size of each group alongside the rate chart.

## Assemble and publish

1. Add filters for `sex_label`, `age_group`, and `disease_label`, then apply each filter to the relevant worksheets.
2. Arrange the outcome, age, sex, cholesterol, and blood-pressure views on one dashboard. Use concise titles, readable tooltips, and consistent units.
3. Add a source note: UCI Heart Disease, Cleveland subset; historical records; descriptive analysis only.
4. Save as `.twb` or `.twbx` from Tableau Desktop. This repository provides the Tableau-ready export and instructions; it does not claim that a Tableau workbook has already been created.

Do not interpret group differences as causal or use them for diagnosis or individual risk assessment.
