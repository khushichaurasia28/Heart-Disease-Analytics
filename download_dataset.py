"""Download the Cleveland Heart Disease dataset from UCI (with a documented mirror fallback)."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
OUT = RAW / "heart.csv"

def main():
    if OUT.exists():
        print(f"Dataset already exists; leaving it unchanged: {OUT}")
        return
    try:
        from ucimlrepo import fetch_ucirepo
        dataset = fetch_ucirepo(id=45)
        x = dataset.data.features.copy()
        y = dataset.data.targets.copy()
        df = pd.concat([x, y], axis=1)
        # Normalize the target column name used by UCI versions.
        if "num" in df.columns:
            df = df.rename(columns={"num": "target"})
        elif len(df.columns) == 14:
            df.columns = ["age","sex","cp","trestbps","chol","fbs","restecg",
                          "thalach","exang","oldpeak","slope","ca","thal","target"]
        df.to_csv(OUT, index=False)
        print(f"Downloaded from UCI via ucimlrepo: {len(df)} rows -> {OUT}")
        return
    except Exception as exc:
        print(f"UCI package download failed: {exc}")
    # Public mirror of the same Cleveland subset; original source remains UCI.
    url = "https://raw.githubusercontent.com/quillaja/uci_cleveland_heart_data/main/heart_cleveland_numeric_categories.csv"
    df = pd.read_csv(url)
    if "target" not in df.columns and "num" in df.columns:
        df = df.rename(columns={"num": "target"})
    df.to_csv(OUT, index=False)
    print(f"Downloaded Cleveland subset mirror: {len(df)} rows -> {OUT}")
    print("Dataset citation and license are documented in README.md.")

if __name__ == "__main__":
    main()
