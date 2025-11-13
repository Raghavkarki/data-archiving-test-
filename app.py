from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import base64
import urllib3
import csv
import os


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure random key in production

COUCHDB_URL1 = "https://13.235.245.131/medic/_design/medic-forms/_view/u2_registry?include_docs=true"
##COUCHDB_URL = "https://13.235.245.131/medic"
COUCHDB_URL = "https://chisdhkuh.sambhavpossible.org/medic"



USERNAME = "medic"
# PASSWORD = "password"
PASSWORD = "ch!$m3d!cdhkuh"


def encode_credentials(username, password):
    credentials = f"{username}:{password}"
    return base64.b64encode(credentials.encode()).decode()

def create_headers():
    return {
        "Accept": "application/json",
        "Authorization": f"Basic {encode_credentials(USERNAME, PASSWORD)}"
    }

FORM_NAME_MAPPING = {
    "u2_registry": "U2 Registry",
    "anc_monitoring": "ANC Monitoring-old",
    "anc_monitoring_form": "ANC Monitoring-new", 
    "pregnancy_screening_form": "Pregnancy Screening Form",
    "epds_module_5": "EPDS Module 5",
    "epds_module_1": "EPDS Module 1",
    "epds_module_2": "EPDS Module 2",
    "post_delivery_form": "Post Delivery Form",
    "epds_screening": "EPDS Screening",
    # Add more mappings as needed
}

LOG_FILE = "deletion_logs.csv"

def log_deletion(contact_id, doc_id, result):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Contact ID", "Document ID", "Result"])
        writer.writerow([contact_id, doc_id, result])


# def fetch_reports_by_contact_id(contact_id):
#     try:
#         url = f"{COUCHDB_URL}/_all_docs?include_docs=true"
#         response = requests.get(url, headers=create_headers(), verify=False)
#         if response.status_code != 200:
#             return None
#         data = response.json()
#         filtered_docs = [
#             row for row in data['rows']
#             if row.get('doc', {}).get('fields', {}).get('inputs', {}).get('contact', {}).get('_id') == contact_id
#         ]
#         return filtered_docs if filtered_docs else None
#     except Exception as e:
#         print(f"Error fetching reports: {e}")
#         return None
def fetch_reports_by_contact_id(contact_id):
    try:
        url = f"{COUCHDB_URL}/_find"
        query = {
            "selector": {
                "fields.patient_id": contact_id,
                # "fields.inputs.contact._id": contact_id,
                # "form": {
                #     "$in": ["pregnancy_screening_form", "u2_registry","anc_monitoring_form","pregnancy_history_form"]
                # }
            },
            "limit": 1000
        }

        response = requests.post(url, json=query, headers=create_headers(), verify=False)
        if response.status_code != 200:
            return None

        data = response.json()
        filtered_docs = data.get('docs', [])
        return [{"doc": doc} for doc in filtered_docs] if filtered_docs else None
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return None



VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    result_messages = []
    records = []
    report_ids = []
    selected_form_names = []

    if request.method == "POST":
        input_ids = request.form.get("report_ids", "")
        selected_form_names = request.form.getlist("form_name")
        report_ids = [id.strip() for id in input_ids.split(",") if id.strip()]
        duplicates = set([id for id in report_ids if report_ids.count(id) > 1])
        if duplicates:
            result_messages.append({
                "message": f"Duplicate Contact IDs detected: {', '.join(duplicates)}. Please remove duplicates.",
                "type": "error"
            })
        if not report_ids:  
            result_messages.append({"message": "Please enter at least one Report ID.", "type": "error"})
        else:
            for contact_id in report_ids:
                filtered = fetch_reports_by_contact_id(contact_id)
                if filtered:
                    if selected_form_names:
                        filtered = [doc for doc in filtered if doc.get('doc', {}).get('form') in selected_form_names]
                    if filtered:
                        records.extend(filtered)
                        result_messages.append({
                            "message": f"Successfully fetched reports for contact._id = {contact_id}.",
                            "type": "success"
                        })
                    else:
                        readable_names = ", ".join(FORM_NAME_MAPPING.get(f, f) for f in selected_form_names)
                        result_messages.append({
                            "message": f"No records found for contact._id = {contact_id} with form(s): {readable_names}.",
                            "type": "error"
                        })
                else:
                    result_messages.append({
                        "message": f"No records found with contact._id = {contact_id}.",
                        "type": "error"
                    })

    return render_template(
        "index.html",
        result_messages=result_messages,
        records=records,
        report_ids=report_ids,
        form_name_mapping=FORM_NAME_MAPPING,
        selected_form_names=selected_form_names
    )

# @app.route("/delete-report", methods=["POST"])
# def delete_report():
#     if not session.get("logged_in"):
#         return jsonify(success=False, message="Unauthorized")

#     data = request.get_json()
#     doc_id = data.get("docId")
#     rev = data.get("rev")

#     try:
#         delete_url = f"{COUCHDB_URL}/{doc_id}?rev={rev}"
#         response = requests.delete(delete_url, headers=create_headers(), verify=False)
#         if response.status_code == 200:
#             return jsonify(success=True, message=f"Report {doc_id} deleted successfully.")
#         else:
#             return jsonify(success=False, message=f"Failed to delete report {doc_id}.")
#     except Exception as e:
#         return jsonify(success=False, message=f"Error deleting report: {e}")
@app.route("/delete-report", methods=["POST"])
def delete_report():
    if not session.get("logged_in"):
        return jsonify(success=False, message="Unauthorized")

    data = request.get_json()
    doc_id = data.get("docId")
    rev = data.get("rev")

    contact_id = "Unknown"
    fetch_url = f"{COUCHDB_URL}/{doc_id}"
    fetch_response = requests.get(fetch_url, headers=create_headers(), verify=False)
    if fetch_response.status_code == 200:
        json_data = fetch_response.json()
        # contact_id = json_data.get("fields", {}).get("inputs", {}).get("contact", {}).get("_id", "Unknown")
        contact_id = json_data.get("fields", {}).get("patient_id", "Unknown")

    try:
        delete_url = f"{COUCHDB_URL}/{doc_id}?rev={rev}"
        response = requests.delete(delete_url, headers=create_headers(), verify=False)
        if response.status_code == 200:
            log_deletion(contact_id, doc_id, "Deleted successfully")
            return jsonify(success=True, message=f"Report {doc_id} deleted successfully.")
        else:
            log_deletion(contact_id, doc_id, "Failed to delete")
            return jsonify(success=False, message=f"Failed to delete report {doc_id}.")
    except Exception as e:
        log_deletion(contact_id, doc_id, f"Error: {e}")
        return jsonify(success=False, message=f"Error deleting report: {e}")


# @app.route("/delete-all-reports", methods=["POST"])
# def delete_all_reports():
#     if not session.get("logged_in"):
#         return jsonify(success=False, message="Unauthorized")

#     data = request.get_json()
#     report_ids = data.get("reportIds", [])
#     results = []

#     try:
#         for doc_id in report_ids:
#             fetch_url = f"{COUCHDB_URL}/{doc_id}"
#             fetch_response = requests.get(fetch_url, headers=create_headers(), verify=False)
#             if fetch_response.status_code == 200:
#                 rev = fetch_response.json().get("_rev")
#                 delete_url = f"{COUCHDB_URL}/{doc_id}?rev={rev}"
#                 delete_response = requests.delete(delete_url, headers=create_headers(), verify=False)
#                 if delete_response.status_code == 200:
#                     results.append({"docId": doc_id, "success": True, "message": f"Report {doc_id} deleted successfully."})
#                 else:
#                     results.append({"docId": doc_id, "success": False, "message": f"Failed to delete report {doc_id}."})
#             else:
#                 results.append({"docId": doc_id, "success": False, "message": f"Failed to fetch report {doc_id}."})
#         return jsonify(success=True, results=results)
#     except Exception as e:
#         return jsonify(success=False, message=f"Error deleting reports: {e}")
@app.route("/delete-all-reports", methods=["POST"])
def delete_all_reports():
    if not session.get("logged_in"):
        return jsonify(success=False, message="Unauthorized")

    data = request.get_json()
    report_ids = data.get("reportIds", [])
    results = []

    try:
        for doc_id in report_ids:
            fetch_url = f"{COUCHDB_URL}/{doc_id}"
            fetch_response = requests.get(fetch_url, headers=create_headers(), verify=False)
            contact_id = "Unknown"

            if fetch_response.status_code == 200:
                json_data = fetch_response.json()
                contact_id = json_data.get("fields", {}).get("patient_id", "Unknown")
                rev = json_data.get("_rev")
                delete_url = f"{COUCHDB_URL}/{doc_id}?rev={rev}"
                delete_response = requests.delete(delete_url, headers=create_headers(), verify=False)

                if delete_response.status_code == 200:
                    result_msg = f"Report {doc_id} deleted successfully."
                    results.append({"docId": doc_id, "success": True, "message": result_msg})
                else:
                    result_msg = f"Failed to delete report {doc_id}."
                    results.append({"docId": doc_id, "success": False, "message": result_msg})
            else:
                result_msg = f"Failed to fetch report {doc_id}."
                results.append({"docId": doc_id, "success": False, "message": result_msg})

            # Log deletion result
            log_deletion(contact_id, doc_id, result_msg)

        return jsonify(success=True, results=results)
    except Exception as e:
        return jsonify(success=False, message=f"Error deleting reports: {e}")

# @app.route("/deletion-logs")
# def deletion_logs():
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))

#     logs = []
#     if os.path.exists(LOG_FILE):
#         with open(LOG_FILE, newline='') as file:
#             reader = csv.DictReader(file)
#             logs = list(reader)

#     return render_template("logs.html", logs=logs)
# @app.route('/deletion-logs')
# def deletion_logs():
#     logs = []
#     result_filter = request.args.get('result_filter')

#     if os.path.exists('deletion_logs.csv'):
#         with open('deletion_logs.csv', newline='') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 if not result_filter or row['Result'].lower() == result_filter.lower():
#                     logs.append(row)

#     return render_template('logs.html', logs=logs, selected_filter=result_filter)
# @app.route('/deletion-logs')
# def deletion_logs():
#     logs = []
#     result_filter = request.args.get('result_filter')

#     if os.path.exists('deletion_logs.csv'):
#         with open('deletion_logs.csv', newline='') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 result_text = row['Result'].strip().lower()
#                 is_success = result_text.endswith("deleted successfully.")

#                 if result_filter == 'Successfully Deleted' and not is_success:
#                     continue
#                 elif result_filter == 'Failed' and is_success:
#                     continue

#                 logs.append(row)

#     return render_template('logs.html', logs=logs, selected_filter=result_filter)
@app.route('/deletion-logs')
def deletion_logs():
    logs = []
    result_filter = request.args.get('result_filter')

    if os.path.exists('deletion_logs.csv'):
        with open('deletion_logs.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                result_text = row['Result'].strip().lower()
                is_success = result_text.endswith("deleted successfully.")

                if result_filter == 'Successfully Deleted' and not is_success:
                    continue
                elif result_filter == 'Failed' and is_success:
                    continue

                logs.append(row)

    total_count = len(logs)

    return render_template(
        'logs.html',
        logs=logs,
        selected_filter=result_filter,
        total_count=total_count
    )



from tombstone_routes import tombstone_bp
from csv_mapper_routes import csv_mapper_bp   
app.register_blueprint(tombstone_bp)
app.register_blueprint(csv_mapper_bp)

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8000, debug=True)
    # if __name__ == "__main__":
    #     app.run(host="0.0.0.0", port=8000, debug=False)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)


