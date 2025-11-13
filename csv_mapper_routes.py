from flask import Blueprint, render_template, request, send_file
import pandas as pd
import io
import os

csv_mapper_bp = Blueprint("csv_mapper", __name__)

# === Column Mapping ===
column_mapping = {
    "Unnamed: 0":"S.N"
}

# === Final Order ===
final_order = [
     "S.N","_id", "_rev", "form", "reported_date", "from","chw",
    "fields.inputs.source",
    "fields.inputs.source_id",
    "fields.inputs.contact._id",
    "fields.inputs.contact.nepali_full_name",
    "fields.inputs.contact.patient_id",
    "fields.inputs.contact.date_of_registration",
    "fields.patient_uuid",
    "fields.patient_name",
    "fields.patient_id",
    "fields.delivery_date",
    "fields.updated_dd",
    "fields.latestlmp",
    "fields.lmpdays",
    "fields.ddno",
    "fields.up_dd",
    "fields.formatted_date",
    "fields.epds.condit_bn",
    "fields.epds.intro",
    "fields.epds.cnst_scrn",
    "fields.epds.reprtd_date",
    "fields.epds.s_date",
    "fields.epds.screening.curr_sts",
    "fields.epds.screening.del_date",
    "fields.epds.screening.pp_days",
    "fields.epds.screening.pp_days_note",
    "fields.epds.screening.migration",
    "fields.epds.screening.prob_part",
    "fields.epds.postnatal_d_screen.epds_inst",
    "fields.epds.postnatal_d_screen.epds_1",
    "fields.epds.postnatal_d_screen.epds_2",
    "fields.epds.postnatal_d_screen.epds_3",
    "fields.epds.postnatal_d_screen.epds_4",
    "fields.epds.postnatal_d_screen.epds_5",
    "fields.epds.postnatal_d_screen.epds_6",
    "fields.epds.postnatal_d_screen.epds_7",
    "fields.epds.postnatal_d_screen.epds_8",
    "fields.epds.postnatal_d_screen.epds_9",
    "fields.epds.postnatal_d_screen.epds_10",
    "fields.epds.postnatal_d_screen.epds_score",
    "fields.epds.postnatal_d_screen.fln_elig",
    "fields.epds.ness",
    "fields.epds.study_eligibility.inelig_ins2",
    "fields.epds.study_cnst",
    "fields.epds.screening.lmp_wom",
    "fields.epds.screening.gest_wk",
    "fields.epds.screening.gest_wk_note",
    "fields.epds.screening.plan_birth",
    "fields.epds.screening.diff_prob",
    "fields.epds.study_eligibility.elig_ins1",
    "fields.epds.study_cnst.cnst_int",
    "fields.epds.study_cnst.cnst_part",
    "fields.epds.socidem_info.instr_socidem",
    "fields.epds.socidem_info.age_resp",
    "fields.epds.socidem_info.age_yrs",
    "fields.epds.socidem_info.fam_mem",
    "fields.epds.socidem_info.fam_type",
    "fields.epds.socidem_info.ethn",
    "fields.epds.socidem_info.religion",
    "fields.epds.socidem_info.edu_resp",
    "fields.epds.socidem_info.edu_husb",
    "fields.epds.socidem_info.occu_resp",
    "fields.epds.socidem_info.occu_husb",
    "fields.epds.socidem_info.monthly_expend",
    "fields.epds.socidem_info.dur_marriage",
    "fields.epds.socidem_info.gravida",
    "fields.epds.socidem_info.intend_preg",
    "fields.epds.socidem_info.parity",
    "fields.epds.socidem_info.livebirth_num",
    "fields.epds.socidem_info.depress_hstry",
    "fields.epds.socidem_info.other_occu_husb",
    "fields.epds.socidem_info.mode_deli",
    "fields.epds.study_cnst.rsn_part",
    "fields.epds.study_cnst.cnst_specify",
    "fields.epds.study_cnst.time",
    "fields.epds.ness.ness_inst",
    "fields.epds.ness.ness1",
    "fields.epds.ness.ness2",
    "fields.epds.ness.ness_score",
    "fields.epds.ness.elig_ness1",
    "fields.epds.socidem_info.age_dob",
    "fields.epds.socidem_info.age",
    "fields.epds.socidem_info.age_display",
    "fields.epds.study_eligibility",
    "fields.epds.rsn_no_scrn",
    "fields.epds.specify_reason",
    "fields.epds.ness.Inelig_ness1",
    "fields.epds.ness.ness3",
    "fields.epds.ness.Elig_ness3",
    "fields.epds.ness.risk_suicide",
    "fields.epds.study_eligibility.no_imm_risk",
    "fields.inputs.meta.location.lat",
    "fields.inputs.meta.location.long",
    "fields.inputs.meta.location.error",
    "fields.inputs.meta.location.message",
    "fields.inputs.meta.deprecatedID",
    "fields.meta.instanceID",
    "geolocation.code",
    "geolocation.message",
    "_attachments.content.content_type",
    "_attachments.content.revpos",
    "_attachments.content.digest",
    "_attachments.content.length",
    "_attachments.content.stub",
    "geolocation.latitude",
    "geolocation.longitude",
    "geolocation.altitude",
    "geolocation.accuracy",
    "geolocation.altitudeAccuracy",
    "geolocation.heading",
    "geolocation.speed",
]

# === Routes ===
@csv_mapper_bp.route("/csv-mapper")
def csv_mapper():
    return render_template("csv_mapper.html")


@csv_mapper_bp.route("/process-csv", methods=["POST"])
def process_csv():
    file = request.files['file']
    filename = file.filename.lower()

    # === Read file (CSV or Excel) ===
    if filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        return "Unsupported file format. Please upload CSV or Excel.", 400

    # === Rename ===
    df.rename(columns=column_mapping, inplace=True)

    # Collect all required columns
    required_columns = set(column_mapping.values()) | set(final_order)

    # Find missing ones
    missing_cols = [col for col in required_columns if col not in df.columns]

    # Add them in one shot to avoid fragmentation
    if missing_cols:
        df = df.reindex(columns=df.columns.tolist() + missing_cols)

    # Reorder, but keep extra unmapped columns at the end
    cols_to_keep = [c for c in final_order if c in df.columns]
    reordered_df = df[cols_to_keep + [c for c in df.columns if c not in cols_to_keep]]

    # === Save in same format as input ===
    output = io.BytesIO()

    # Build new name with "_rearranged"
    base, ext = os.path.splitext(file.filename)
    download_name = f"{base}_rearranged{ext}"

    if filename.endswith(".csv"):
        reordered_df.to_csv(output, index=False)
        mimetype = "text/csv"
    else:
        reordered_df.to_excel(output, index=False, engine="openpyxl")
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    output.seek(0)
    return send_file(output, mimetype=mimetype, as_attachment=True, download_name=download_name)

# @csv_mapper_bp.route("/process-csv", methods=["POST"])
# def process_csv():
#     file = request.files['file']
#     filename = file.filename.lower()

#     # === Read file (CSV or Excel) ===
#     if filename.endswith(".csv"):
#         df = pd.read_csv(file)
#     elif filename.endswith((".xlsx", ".xls")):
#         df = pd.read_excel(file)
#     else:
#         return "Unsupported file format. Please upload CSV or Excel.", 400

#     # === Rename ===
#     df.rename(columns=column_mapping, inplace=True)

#     # Collect all required columns
#     required_columns = set(column_mapping.values()) | set(final_order)

#     # Find missing ones
#     missing_cols = [col for col in required_columns if col not in df.columns]

#     # Add them in one shot to avoid fragmentation
#     if missing_cols:
#         df = df.reindex(columns=df.columns.tolist() + missing_cols)

#     # Reorder, but keep extra unmapped columns at the end
#     cols_to_keep = [c for c in final_order if c in df.columns]
#     reordered_df = df[cols_to_keep + [c for c in df.columns if c not in cols_to_keep]]

#     # === Save in same format as input ===
#     output = io.BytesIO()
#     if filename.endswith(".csv"):
#         reordered_df.to_csv(output, index=False)
#         mimetype = "text/csv"
#         download_name = "processed.csv"
#     else:
#         reordered_df.to_excel(output, index=False, engine="openpyxl")
#         mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         download_name = "processed.xlsx"

#     output.seek(0)
#     return send_file(output, mimetype=mimetype, as_attachment=True, download_name=download_name)
