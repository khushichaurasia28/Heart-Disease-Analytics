from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "heart.csv"
PROCESSED = ROOT / "data" / "processed" / "heart_cleaned.csv"

EXPECTED = ["age","sex","cp","trestbps","chol","fbs","restecg","thalach",
            "exang","oldpeak","slope","ca","thal","target"]

def load_raw(path=RAW):
    if not Path(path).exists():
        raise FileNotFoundError("Dataset not found. Run: python download_dataset.py")
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "num" in df.columns and "target" not in df.columns:
        df = df.rename(columns={"num": "target"})
    # Support UCI processed Cleveland files without headers.
    if len(df.columns) == 1 or not set(["age", "target"]).issubset(df.columns):
        raise ValueError("Unexpected dataset format. Expected named columns including age and target.")
    missing = set(EXPECTED) - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {sorted(missing)}")
    return df[EXPECTED].copy()

def clean_data(df):
    out = df.copy()
    out = out.replace("?", np.nan)
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.drop_duplicates()
    # Preserve the original values; median-impute only the two UCI fields with missing values.
    for col in ["ca", "thal"]:
        if col in out and out[col].isna().any():
            out[col] = out[col].fillna(out[col].median())
    out = out.dropna(subset=["target"])
    out["target"] = (out["target"] > 0).astype(int)
    out["sex_label"] = out["sex"].map({0: "Female", 1: "Male"}).fillna("Unknown")
    out["disease_label"] = out["target"].map({0: "No disease", 1: "Disease present"})
    out["age_group"] = pd.cut(out["age"], bins=[0, 39, 49, 59, 69, 120],
                              labels=["Under 40", "40–49", "50–59", "60–69", "70+"])
    return out

def cleaning_report(raw, cleaned):
    numeric = raw.replace("?", np.nan).apply(pd.to_numeric, errors="coerce")
    missing_by_column = {
        column: int(count)
        for column, count in numeric.isna().sum().items()
        if count
    }
    imputed_by_column = {
        column: missing_by_column.get(column, 0)
        for column in ("ca", "thal")
        if missing_by_column.get(column, 0)
    }
    return {
        "raw_rows": int(len(raw)),
        "cleaned_rows": int(len(cleaned)),
        "missing_by_column": missing_by_column,
        "raw_missing": sum(missing_by_column.values()),
        "imputed_by_column": imputed_by_column,
        "imputed_values": sum(imputed_by_column.values()),
        "duplicate_rows": int(raw.duplicated().sum()),
        "rows_removed": int(len(raw) - len(cleaned)),
        "cleaned_missing": int(cleaned.isna().sum().sum()),
    }

def prepare():
    raw = load_raw()
    cleaned = clean_data(raw)
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED, index=False)
    return raw, cleaned
