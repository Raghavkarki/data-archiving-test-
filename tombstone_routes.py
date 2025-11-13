from flask import Flask, Blueprint, Response, render_template, request, stream_with_context, jsonify, send_from_directory
import requests
import base64
import urllib3
import json
import time
import os
from datetime import datetime
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
tombstone_bp = Blueprint("tombstone", __name__, template_folder="templates")

app = Flask(__name__)

# === CouchDB Config ===
#COUCHDB_URL = "https://qa.sambhavpossible.org/medic"
#USERNAME = "medic"
#PASSWORD = "password"
COUCHDB_URL = "https://chisdhkuh.sambhavpossible.org/medic"



USERNAME = "medic"
# PASSWORD = "password"
PASSWORD = "ch!$m3d!cdhkuh"

# === Local Storage Directory for Tombstones ===
DATA_DIR = "tombstone_data"
os.makedirs(DATA_DIR, exist_ok=True)

# === Helper Functions ===

def encode_credentials(username, password):
    credentials = f"{username}:{password}"
    return base64.b64encode(credentials.encode()).decode()  

def create_headers():
    return {
        "Accept": "application/json",
        "Authorization": f"Basic {encode_credentials(USERNAME, PASSWORD)}"
    }

def save_all_tombstones_single_file(tombstones):
    os.makedirs(DATA_DIR, exist_ok=True)  # Ensure folder exists
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"All_fetched_report_{timestamp}.csv"
    file_path = os.path.join(DATA_DIR, filename)

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["_id", "form", "deleted"])

        for doc in tombstones:
            form_name = doc.get("tombstone", {}).get("form") or "NA"
            writer.writerow([
                doc.get("_id"),
                form_name,
                doc.get("_deleted")
            ])

    return filename, timestamp

def get_latest_summary():
    os.makedirs(DATA_DIR, exist_ok=True)
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    summary = {}
    for file in files:
        form = file.split("_")[0]
        summary[form] = summary.get(form, 0) + 1
    return summary

# === Routes ===

@tombstone_bp.route("/tombstone")
def index():
    return render_template("fetch_tombstones.html")

@tombstone_bp.route("/stream-tombstones")
def stream_tombstones():
    selected_form = request.args.get("form")

    def generate():
        total_limit = 1000
        batch_size = 500
        all_docs = []
        skip = 0

        try:
            while len(all_docs) < total_limit:
                selector = {"type": "tombstone"}
                if selected_form:
                    selector["tombstone.form"] = selected_form

                query = {
                    "selector": selector,
                    "limit": min(batch_size, total_limit - len(all_docs)),
                    "skip": skip
                }

                response = requests.post(f"{COUCHDB_URL}/_find", json=query, headers=create_headers(), verify=False)
                if response.status_code != 200:
                    yield f"data: ❌ Error fetching data. Status {response.status_code}\n\n"
                    return

                docs = response.json().get("docs", [])
                if not docs:
                    break

                all_docs.extend(docs)
                skip += batch_size

                yield f"data: ✅ {len(all_docs)} reports fetched...\n\n"
                time.sleep(0.2)

            # Trim to first 1000 just in case
            all_docs = all_docs[:total_limit]

            table_data = [
                {
                    "_id": doc.get("_id"),
                    "form": doc.get("tombstone", {}).get("form") or "NA"
                }
                for doc in all_docs
            ]

            yield f"data: TABLE_DATA::{json.dumps(table_data)}\n\n"
            yield f"data: ✔ Done! Displaying first {len(all_docs)} reports only.\n\n"

        except Exception as e:
            yield f"data: ❌ Error: {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")
    
@tombstone_bp.route("/delete-selected-reports", methods=["POST"])
def delete_selected_reports():
    data = request.get_json()
    report_ids = data.get("reportIds", [])
    results = []

    try:
        for doc_id in report_ids:
            # Fetch doc to get _rev
            fetch_url = f"{COUCHDB_URL}/{doc_id}"
            fetch_response = requests.get(fetch_url, headers=create_headers(), verify=False)

            if fetch_response.status_code == 200:
                doc = fetch_response.json()
                rev = doc.get('_rev')
                contact_id = doc.get("fields", {}).get("patient_id", "unknown")

                # Delete document
                delete_url = f"{COUCHDB_URL}/{doc_id}?rev={rev}"
                delete_response = requests.delete(delete_url, headers=create_headers(), verify=False)

                if delete_response.status_code == 200:
                    results.append({"docId": doc_id, "success": True})
                else:
                    results.append({"docId": doc_id, "success": False, "error": delete_response.text})
            else:
                results.append({"docId": doc_id, "success": False, "error": "Document not found"})

        return jsonify(success=True, results=results)
    except Exception as e:
        return jsonify(success=False, message=str(e))



@tombstone_bp.route("/stream-all-tombstones")
def stream_all_tombstones():
    def generate():
        all_docs = []
        all_docs_count = 0
        skip = 0
        batch_size = 500

        try:
            while True:
                query = {
                    "selector": {"type": "tombstone"},
                    "limit": batch_size,
                    "skip": skip
                }
                response = requests.post(f"{COUCHDB_URL}/_find", json=query, headers=create_headers(), verify=False)
                if response.status_code != 200:
                    yield f"data: ❌ Error fetching data. Status {response.status_code}\n\n"
                    break

                docs = response.json().get("docs", [])
                count = len(docs)
                all_docs_count += count
                all_docs.extend(docs)

                yield f"data: ✅ {all_docs_count} reports fetched...\n\n"
                time.sleep(0.2)

                if count < batch_size:
                    break
                skip += batch_size

            # After done, save the fetched data to CSV file
            filename, timestamp = save_all_tombstones_single_file(all_docs)
            yield f"data: ✔ Done! Total: {all_docs_count} tombstone reports. Saved as {filename}\n\n"

        except Exception as e:
            yield f"data: ❌ Error: {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@tombstone_bp.route("/latest-tombstone-summary")
def latest_tombstone_summary():
    os.makedirs(DATA_DIR, exist_ok=True)
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("All_fetched_report_") and f.endswith(".csv")]
    if not files:
        return jsonify({"exists": False})

    latest_file = sorted(files, reverse=True)[0]
    timestamp_part = latest_file.replace("All_fetched_report_", "").replace(".csv", "")

    summary = {}
    file_path = os.path.join(DATA_DIR, latest_file)
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            form = row.get("form") or "NA"
            summary[form] = summary.get(form, 0) + 1

    return jsonify({
        "exists": True,
        "filename": latest_file,
        "timestamp": timestamp_part,
        "summary": summary
    })

@tombstone_bp.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=True)



