from pathlib import Path
import io
import os
import secrets
import pandas as pd
from flask import Flask, render_template, request, send_file
from werkzeug.exceptions import HTTPException
from analysis.preprocessing import prepare, PROCESSED, cleaning_report, load_raw
from analysis.eda import summary, chart_payload, insights

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
ROOT = Path(__file__).resolve().parent

def get_data():
    if not PROCESSED.exists():
        _, df = prepare()
        return df
    return pd.read_csv(PROCESSED)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("setup.html", error="The page you requested does not exist."), 404

@app.errorhandler(Exception)
def handle_application_error(error):
    if isinstance(error, HTTPException):
        return error
    app.logger.exception("Unhandled analytics application error")
    return render_template(
        "setup.html",
        error="The analytics workspace could not complete this request. Check the server log for details.",
    ), 500

@app.route("/")
def home():
    try:
        df = get_data()
        cases = int(df["target"].sum())
        return render_template(
            "index.html", total=len(df), cases=cases, without=len(df) - cases,
            rate=round(cases / len(df) * 100, 1) if len(df) else 0,
            variables=len([column for column in df.columns if column not in {"sex_label", "disease_label", "age_group"}]),
        )
    except Exception as exc:
        return render_template("setup.html", error=str(exc))

@app.route("/dashboard")
def dashboard():
    try:
        df = get_data()
        age = request.args.get("age", "All")
        sex = request.args.get("sex", "All")
        view = df.copy()
        if age != "All":
            view = view[view["age_group"].astype(str) == age]
        if sex != "All":
            view = view[view["sex_label"] == sex]
        total = len(view)
        cases = int(view["target"].sum()) if total else 0
        kpis = {
            "total": total, "cases": cases, "without": total-cases,
            "rate": round(cases/total*100, 1) if total else 0,
            "age": round(view.age.mean(), 1) if total else 0,
            "chol": round(view.chol.mean(), 1) if total else 0,
            "bp": round(view.trestbps.mean(), 1) if total else 0,
            "heart_rate": round(view.thalach.mean(), 1) if total else 0
        }
        return render_template("dashboard.html", kpis=kpis, charts=chart_payload(view),
                               age_options=["Under 40","40–49","50–59","60–69","70+"],
                               selected_age=age, selected_sex=sex)
    except Exception as exc:
        return render_template("setup.html", error=str(exc))

@app.route("/explorer")
def explorer():
    df = get_data()
    q = request.args.get("q", "").strip()
    age = request.args.get("age_group", "All")
    sex = request.args.get("sex", "All")
    disease = request.args.get("disease", "All")
    sort_by = request.args.get("sort", "age")
    sort_order = request.args.get("order", "asc")
    filter_error = ""

    if q:
        mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False, regex=False)).any(axis=1)
        df = df[mask]
    if age in df["age_group"].astype(str).unique():
        df = df[df["age_group"].astype(str) == age]
    if sex in df["sex_label"].unique():
        df = df[df["sex_label"] == sex]
    if disease in df["disease_label"].unique():
        df = df[df["disease_label"] == disease]

    for parameter, column, operator in [
        ("min_chol", "chol", "min"), ("max_chol", "chol", "max"),
        ("min_bp", "trestbps", "min"), ("max_bp", "trestbps", "max")
    ]:
        value = request.args.get(parameter, "").strip()
        if value:
            try:
                threshold = float(value)
                df = df[df[column] >= threshold] if operator == "min" else df[df[column] <= threshold]
            except ValueError:
                filter_error = "Enter numeric values for cholesterol and blood-pressure limits."

    if sort_by not in df.columns:
        sort_by = "age"
    sort_order = "desc" if sort_order == "desc" else "asc"
    df = df.sort_values(sort_by, ascending=sort_order == "asc", kind="stable")
    count = len(df)
    page_size = 50
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    pages = max(1, (count + page_size - 1) // page_size)
    page = min(page, pages)
    start = (page - 1) * page_size
    rows = df.iloc[start:start + page_size].to_dict("records")

    return render_template(
        "explorer.html", rows=rows, columns=df.columns.tolist(), count=count,
        query=q, selected_age=age, selected_sex=sex, selected_disease=disease,
        age_options=["Under 40", "40–49", "50–59", "60–69", "70+"],
        min_chol=request.args.get("min_chol", ""), max_chol=request.args.get("max_chol", ""),
        min_bp=request.args.get("min_bp", ""), max_bp=request.args.get("max_bp", ""),
        sort_by=sort_by, sort_order=sort_order, page=page, pages=pages,
        first_record=start + 1 if count else 0, last_record=min(start + page_size, count),
        filter_error=filter_error
    )

@app.route("/analysis")
def analysis_page():
    df = get_data()
    raw = load_raw()
    return render_template(
        "analysis.html", stats=summary(df), findings=insights(df),
        cleaning=cleaning_report(raw, df),
    )

@app.route("/insights")
def insights_page():
    return render_template("insights.html", findings=insights(get_data()))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/tableau-guide")
def tableau_guide():
    return send_file(ROOT / "tableau_guide.md", mimetype="text/markdown")

@app.route("/download/csv")
def download_csv():
    get_data()
    return send_file(PROCESSED, as_attachment=True, download_name="heart_disease_cleaned.csv", mimetype="text/csv")

@app.route("/download/report")
def download_report():
    df = get_data()
    lines = ["HEART DISEASE ANALYTICS SUMMARY", "="*34, f"Records: {len(df)}",
             f"Disease-present records: {int(df.target.sum())}",
             f"No-disease records: {int((df.target == 0).sum())}", "",
             "KEY DESCRIPTIVE INSIGHTS", *[f"- {x}" for x in insights(df)],
             "", "Educational analysis only; not medical advice."]
    buffer = io.BytesIO("\n".join(lines).encode("utf-8"))
    return send_file(buffer, as_attachment=True, download_name="heart_analytics_report.txt",
                     mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
