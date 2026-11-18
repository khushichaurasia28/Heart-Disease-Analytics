import pandas as pd

def summary(df):
    numeric = df.select_dtypes(include="number")
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing": int(df.isna().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "describe": numeric.describe().round(2).to_dict()
    }

def chart_payload(df):
    disease = df["disease_label"].value_counts().reindex(["No disease","Disease present"], fill_value=0)
    age_groups = df.groupby("age_group", observed=False)["target"]
    age = age_groups.mean().mul(100).round(1)
    age_counts = age_groups.count().astype(int)
    sex_groups = df.groupby("sex_label")["target"]
    sex = sex_groups.mean().mul(100).round(1)
    sex_counts = df["sex_label"].value_counts().reindex(sex.index, fill_value=0)
    chest_pain_groups = df.groupby("cp")["target"]
    cp = chest_pain_groups.mean().mul(100).round(1)
    cp_counts = chest_pain_groups.count().astype(int)
    chol = df.groupby("disease_label")["chol"].mean().round(1)
    bp = df.groupby("disease_label")["trestbps"].mean().round(1)
    heart_rate = df.groupby("disease_label")["thalach"].mean().round(1)
    return {
        "disease_labels": disease.index.tolist(), "disease_values": disease.astype(int).tolist(),
        "age_labels": [str(x) for x in age.index], "age_values": age.fillna(0).tolist(),
        "age_counts": age_counts.tolist(),
        "sex_labels": sex.index.tolist(), "sex_values": sex.fillna(0).tolist(),
        "sex_counts": sex_counts.astype(int).tolist(),
        "cp_labels": [str(x) for x in cp.index], "cp_values": cp.fillna(0).tolist(),
        "cp_counts": cp_counts.tolist(),
        "chol_labels": chol.index.tolist(), "chol_values": chol.fillna(0).tolist(),
        "bp_labels": bp.index.tolist(), "bp_values": bp.fillna(0).tolist(),
        "heart_rate_labels": heart_rate.index.tolist(),
        "heart_rate_values": heart_rate.fillna(0).tolist()
    }

def insights(df):
    findings = []
    total = len(df)
    if total:
        cases = int(df["target"].sum())
        findings.append(
            f"{cases} of {total} records ({cases / total * 100:.1f}%) are in the disease-present group after binary target mapping."
        )

    age_groups = df.groupby("age_group", observed=False)["target"].agg(["sum", "count"])
    age_groups = age_groups[age_groups["count"] > 0]
    if not age_groups.empty:
        age_rates = age_groups["sum"] / age_groups["count"]
        highest_age = age_rates.idxmax()
        findings.append(
            f"The {highest_age} age group has the highest observed disease proportion "
            f"({age_groups.loc[highest_age, 'sum']:.0f}/{age_groups.loc[highest_age, 'count']:.0f}, "
            f"{age_rates.loc[highest_age] * 100:.1f}%)."
        )

    sex_groups = df.groupby("sex_label")["target"].agg(["sum", "count"])
    for sex, counts in sex_groups.iterrows():
        if counts["count"]:
            findings.append(
                f"The observed disease proportion for {sex.lower()} records is "
                f"{counts['sum']:.0f}/{counts['count']:.0f} ({counts['sum'] / counts['count'] * 100:.1f}%)."
            )

    for column, label, unit in [
        ("chol", "cholesterol", "mg/dL"),
        ("trestbps", "resting blood pressure", "mm Hg"),
        ("thalach", "maximum heart rate", "bpm"),
    ]:
        means = df.groupby("disease_label")[column].mean()
        if "Disease present" in means and "No disease" in means:
            findings.append(
                f"Mean {label} is {means['Disease present']:.1f} {unit} for disease-present records "
                f"and {means['No disease']:.1f} {unit} for no-disease records."
            )

    cp_groups = df.groupby("cp")["target"].agg(["sum", "count"])
    cp_groups = cp_groups[cp_groups["count"] > 0]
    if not cp_groups.empty:
        cp_rates = cp_groups["sum"] / cp_groups["count"]
        highest_cp = cp_rates.idxmax()
        findings.append(
            f"Chest-pain code {highest_cp} has the highest observed disease proportion "
            f"({cp_groups.loc[highest_cp, 'sum']:.0f}/{cp_groups.loc[highest_cp, 'count']:.0f}, "
            f"{cp_rates.loc[highest_cp] * 100:.1f}%)."
        )
    findings.append("These are descriptive associations in this historical dataset; they do not establish causation or diagnose an individual.")
    return findings
