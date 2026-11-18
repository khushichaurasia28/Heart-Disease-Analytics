import io
import pandas as pd
from unittest.mock import patch
import app as web_app
import download_dataset
from analysis.preprocessing import clean_data, cleaning_report
from analysis.eda import chart_payload, insights

def sample():
    return pd.DataFrame({
        "age":[45,62,55], "sex":[1,0,1], "cp":[1,4,3],
        "trestbps":[120,140,130], "chol":[200,250,220], "fbs":[0,0,1],
        "restecg":[0,1,0], "thalach":[170,130,150], "exang":[0,1,0],
        "oldpeak":[0.0,2.1,1.0], "slope":[1,2,2], "ca":[0,1,0],
        "thal":[3,7,3], "target":[0,2,1]
    })

def test_binary_target_and_labels():
    cleaned = clean_data(sample())
    assert cleaned["target"].tolist() == [0,1,1]
    assert set(cleaned["disease_label"]) == {"No disease","Disease present"}

def test_chart_payload_and_insights():
    cleaned = clean_data(sample())
    payload = chart_payload(cleaned)
    assert sum(payload["disease_values"]) == 3
    assert sum(payload["age_counts"]) == 3
    assert sum(payload["sex_counts"]) == 3
    assert sum(payload["cp_counts"]) == 3
    assert payload["heart_rate_labels"] == ["Disease present", "No disease"]
    assert payload["heart_rate_values"] == [140.0, 170.0]
    assert len(insights(cleaned)) >= 2
    assert not any("average average" in finding.lower() for finding in insights(cleaned))

def test_cleaning_report_tracks_imputation_and_duplicates():
    raw = sample()
    raw.loc[0, "ca"] = float("nan")
    raw.loc[1, "thal"] = float("nan")
    raw = pd.concat([raw, raw.iloc[[2]]], ignore_index=True)
    report = cleaning_report(raw, clean_data(raw))
    assert report["raw_missing"] == 2
    assert report["imputed_values"] == 2
    assert report["duplicate_rows"] == 1
    assert report["cleaned_rows"] == 3

def test_explorer_applies_filters_and_search():
    cleaned = clean_data(sample())
    with patch.object(web_app, "get_data", return_value=cleaned):
        response = web_app.app.test_client().get(
            "/explorer?q=250&sex=Female&age_group=60%E2%80%9369&disease=Disease+present&min_chol=240"
        )
    assert response.status_code == 200
    assert b"Showing 1\xe2\x80\x931 of 1 matching records" in response.data
    assert b"<td>250</td>" in response.data
    assert b"<td>200</td>" not in response.data

def test_explorer_sorts_and_paginates_rows():
    cleaned = pd.concat([clean_data(sample())] * 17, ignore_index=True)
    with patch.object(web_app, "get_data", return_value=cleaned):
        response = web_app.app.test_client().get("/explorer?sort=age&order=desc&page=2")
    assert response.status_code == 200
    assert b"Showing 51\xe2\x80\x9351 of 51 matching records" in response.data
    assert b"Page 2 of 2" in response.data
    assert b"<td>45</td>" in response.data
    assert b"<td>62</td>" not in response.data
    assert b"page=1" in response.data

def test_explorer_handles_invalid_pagination_and_numeric_filter():
    cleaned = clean_data(sample())
    with patch.object(web_app, "get_data", return_value=cleaned):
        response = web_app.app.test_client().get("/explorer?page=invalid&min_chol=high")
    assert response.status_code == 200
    assert b"numeric values" in response.data
    assert b"Page 1 of 1" in response.data

def test_project_pages_and_downloads_are_available():
    client = web_app.app.test_client()
    for path in ["/", "/dashboard", "/explorer", "/analysis", "/insights", "/about", "/tableau-guide", "/download/csv", "/download/report"]:
        assert client.get(path).status_code == 200
    assert client.get("/not-a-page").status_code == 404

def test_dashboard_filters_maximum_heart_rate_kpi():
    cleaned = clean_data(sample())
    with patch.object(web_app, "get_data", return_value=cleaned):
        response = web_app.app.test_client().get("/dashboard?age=60%E2%80%9369&sex=Female")
    assert response.status_code == 200
    assert b"Mean maximum heart rate" in response.data
    assert b"130.0" in response.data

def test_explorer_treats_search_as_literal_text():
    cleaned = clean_data(sample())
    with patch.object(web_app, "get_data", return_value=cleaned):
        response = web_app.app.test_client().get("/explorer?q=%5B")
    assert response.status_code == 200
    assert b"No records match these filters" in response.data

def test_dataset_downloader_preserves_an_existing_file(tmp_path, capsys):
    dataset_path = tmp_path / "heart.csv"
    original = b"existing,dataset\n1,unchanged\n"
    dataset_path.write_bytes(original)
    with patch.object(download_dataset, "OUT", dataset_path):
        download_dataset.main()
    assert dataset_path.read_bytes() == original
    assert "leaving it unchanged" in capsys.readouterr().out

def test_csv_download_is_clean_and_tableau_ready():
    response = web_app.app.test_client().get("/download/csv")
    exported = pd.read_csv(io.BytesIO(response.data))
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert len(exported) == len(web_app.get_data())
    assert {"sex_label", "disease_label", "age_group"}.issubset(exported.columns)
    assert set(exported["target"]) == {0, 1}
    assert int(exported.isna().sum().sum()) == 0

def test_unhandled_error_returns_a_safe_application_message():
    with patch.object(web_app, "get_data", side_effect=RuntimeError("internal detail")):
        response = web_app.app.test_client().get("/explorer")
    assert response.status_code == 500
    assert b"could not complete this request" in response.data
    assert b"internal detail" not in response.data
