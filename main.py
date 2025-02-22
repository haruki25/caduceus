import os
import re
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# Google Drive API credentials
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# Function to list all patient folders
def list_patient_folders(parent_folder_id):
    query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    return {folder["name"]: folder["id"] for folder in folders}

# Function to update app.yaml with the selected folder ID
def update_yaml(folder_id):
    yaml_path = "app.yaml"
    
    with open(yaml_path, "r") as file:
        yaml_content = file.read()
    
    yaml_content = re.sub(r"(object_id:\s*)[^\n]+", rf"object_id: {folder_id}", yaml_content)
    
    with open(yaml_path, "w") as file:
        file.write(yaml_content)

    st.success("Updated app.yaml successfully!")
    
st.set_page_config(
    page_title="Caduceus",
    page_icon="assets/favicon.ico",
    layout="wide"
)

st.title("Patient Data Selection")

PARENT_FOLDER_ID = os.getenv("PARENT_FOLDER_ID")

# Fetch patient folders
folders = list_patient_folders(PARENT_FOLDER_ID)
if not folders:
    st.error("No patient folders found.")
else:
    selected_folder = st.selectbox("Select a patient folder:", list(folders.keys()))
    if st.button("Load Data"):
        update_yaml(folders[selected_folder])
        st.success(f"Selected patient: {selected_folder}")
        
        # Run app.py after updating yaml
        st.warning("Launching chat interface...")
        try:
            server = subprocess.Popen("python app.py &", shell=True)
            ui = subprocess.Popen("streamlit run ui.py", shell=True)
            server.wait()
            ui.wait()
        except Exception as e:
            logger.error(f"Error launching chat interface: {e}")
            server.terminate_on_error()
            ui.terminate_on_error()
            sys.exit(0)
