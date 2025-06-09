import streamlit as st
import json
import tempfile
import os 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

@st.cache_resource
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

drive = authenticate_drive()

st.set_page_config(page_title="PAM Request JSON Generator", layout="wide")
st.title("PAM Request JSON Generator")
st.markdown("Paste your full Confluence row (including all fields and values). It will parse the row, convert it to JSON, and upload to your Google Drive.")

pasted_text = st.text_area("Paste Confluence Row Below", height=300)

if st.button("Convert & Upload to Google Drive"):
        try:
                rows = pasted_text.strip().split("\n")
                content_rows = [r.strip() for r in rows if r.strip() != ""][-17:]
                data = {
                        "target_safe": content_rows[0],
                        "login_ids": [id_.strip() for id_ in content_rows[1].split("  ") if id_.strip()],
                        "data_export_type": content_rows[3],
                        "data_export_detail": content_rows[4],
                        "service_request_ticket": content_rows[5],
                        "access_start_datetime": content_rows[6] + " " + content_rows[7],
                        "access_end_datetime": content_rows[8] + " " + content_rows[9],
                        "request_reason": content_rows[10],
                        "pam_usage_snow": content_rows[11],
                        "gops_acpf_info": [content_rows[12], content_rows[13]],
                        "service_account": content_rows[14],
                        "emergency_account_usage": content_rows[15],
                        "emergency_reason": content_rows[16]
                }
                json_str = json.dumps(data, indent=4)
                st.subheader("Generated JSON")
                st.code(json_str, language='json')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                        tmp.write(json_str.encode('utf-8'))
                        tmp_path = tmp.name
                file_drive = drive.CreateFile({"title": "pam_request.json"})
                file_drive.SetContentFile(tmp_path)
                file_drive.Upload()
                file_drive.InsertPermission({
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader'
                })
                
                file_id = file_drive['id']
                st.success("Uploaded to Google Drive!")
                st.markdown(f"Public JSON URL: [Click to Download](https://drive.google.com/uc?id={file_id}&export=download)")

try:
    file_drive=drive.CreateFile({'title': file_name})
    file_drive.SetContentString(json_str)
    file_drive.upload()
except Exception as e:
    st.error(f"Error: {e}")
