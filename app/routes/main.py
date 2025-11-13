"""Main application routes"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, current_app
import requests
import os
from app.utils.couchdb import fetch_reports_by_contact_id, create_headers
from app.utils.logging import log_deletion

main_bp = Blueprint('main', __name__)


def require_login():
    """Check if user is logged in"""
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
    return None


@main_bp.route("/admin")
def admin():
    """Admin dashboard"""
    auth_check = require_login()
    if auth_check:
        return auth_check
    return render_template("dashboard.html")


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Main data archiving page"""
    auth_check = require_login()
    if auth_check:
        return auth_check

    config = current_app.config
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
                        readable_names = ", ".join(config['FORM_NAME_MAPPING'].get(f, f) for f in selected_form_names)
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
        form_name_mapping=config['FORM_NAME_MAPPING'],
        selected_form_names=selected_form_names
    )


@main_bp.route("/delete-report", methods=["POST"])
def delete_report():
    """Delete a single report"""
    if not session.get("logged_in"):
        return jsonify(success=False, message="Unauthorized")

    data = request.get_json()
    doc_id = data.get("docId")
    rev = data.get("rev")
    config = current_app.config

    contact_id = "Unknown"
    fetch_url = f"{config['COUCHDB_URL']}/{doc_id}"
    fetch_response = requests.get(fetch_url, headers=create_headers(), verify=False)
    if fetch_response.status_code == 200:
        json_data = fetch_response.json()
        contact_id = json_data.get("fields", {}).get("patient_id", "Unknown")

    try:
        delete_url = f"{config['COUCHDB_URL']}/{doc_id}?rev={rev}"
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


@main_bp.route("/delete-all-reports", methods=["POST"])
def delete_all_reports():
    """Delete multiple reports"""
    if not session.get("logged_in"):
        return jsonify(success=False, message="Unauthorized")

    data = request.get_json()
    report_ids = data.get("reportIds", [])
    results = []
    config = current_app.config

    try:
        for doc_id in report_ids:
            fetch_url = f"{config['COUCHDB_URL']}/{doc_id}"
            fetch_response = requests.get(fetch_url, headers=create_headers(), verify=False)
            contact_id = "Unknown"

            if fetch_response.status_code == 200:
                json_data = fetch_response.json()
                contact_id = json_data.get("fields", {}).get("patient_id", "Unknown")
                rev = json_data.get("_rev")
                delete_url = f"{config['COUCHDB_URL']}/{doc_id}?rev={rev}"
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


@main_bp.route('/deletion-logs')
def deletion_logs():
    """View deletion logs"""
    auth_check = require_login()
    if auth_check:
        return auth_check

    logs = []
    result_filter = request.args.get('result_filter')
    log_file = current_app.config['LOG_FILE']

    if os.path.exists(log_file):
        import csv
        with open(log_file, newline='') as csvfile:
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

