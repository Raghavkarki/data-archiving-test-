"""Logging utility functions"""
import csv
import os
from flask import current_app


def log_deletion(contact_id, doc_id, result):
    """Log deletion operation to CSV file"""
    log_file = current_app.config['LOG_FILE']
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Contact ID", "Document ID", "Result"])
        writer.writerow([contact_id, doc_id, result])

