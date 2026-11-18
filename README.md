# Heart Disease Analytics Platform

A Flask-based educational data analytics application built around the Cleveland subset of the UCI Heart Disease dataset. It includes preprocessing, exploratory summaries, interactive charts, dataset exploration, automatically calculated descriptive insights, and CSV/report downloads.

## Dataset

The downloader retrieves UCI Heart Disease dataset ID 45 via `ucimlrepo`; a public Cleveland CSV mirror is used only as a fallback. The Cleveland subset has 303 instances and 13 input features. UCI documents target values 0–4; this project maps 0 to `No disease` and values 1–4 to `Disease present` for descriptive binary grouping. The raw download is preserved under `data/raw/`; the processed version is written to `data/processed/`.

**Citation:** Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease*. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C52P4X  
**License:** CC BY 4.0. See https://archive.ics.uci.edu/dataset/45/heart+disease

## Run on Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python download_dataset.py
python app.py
```

Open http://127.0.0.1:5000

If `data/raw/heart.csv` already exists, `download_dataset.py` keeps it unchanged. The application uses the existing file and writes analysis output to `data/processed/heart_cleaned.csv`.

## Features

- Dataset download and provenance documentation
- Before/after missing-value and duplicate checks, with documented preprocessing
- Dashboard KPIs calculated from the processed dataset
- Age, sex, outcome, cholesterol and resting blood-pressure visualizations
- Searchable Data Explorer with age, sex, target, cholesterol and blood-pressure filters
- Paginated, sortable processed records
- Descriptive findings with group counts and denominators
- Cleaned CSV and text report downloads
- Tableau-ready CSV and in-app link to the workbook guide

## Project structure

- `app.py` – Flask routes
- `analysis/` – preprocessing, EDA and insights
- `data/raw/` – original downloaded data
- `data/processed/` – cleaned data
- `templates/` – HTML pages
- `static/css/` – styling
- `download_dataset.py` – dataset acquisition
- `tableau_guide.md` – workbook creation instructions

## Important interpretation notes

This is a historical, relatively small dataset and may not represent present-day or wider populations. Correlation and group differences do not establish causation. The application is for education and analytics demonstration only, not diagnosis or individual medical advice.

No machine-learning model is trained in this project. The original target values 0–4 are grouped into 0 versus 1–4 only for descriptive summaries.

## Project contributions

Team Leader for a four-member team. Coordinated data cleaning and preprocessing, EDA, analysis of age, cholesterol, blood pressure and outcome patterns, Tableau dashboard development, and the Flask application used to present findings. GitHub was used for team collaboration and version control.

The About page lists the role and team size without inventing member names or individual contribution details.
