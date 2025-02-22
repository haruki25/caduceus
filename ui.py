import logging
import os
import streamlit as st
from dotenv import load_dotenv
from pathway.xpacks.llm.question_answering import RAGClient
from groq import Groq
from prompt import system_prompt
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
import re

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Google Drive API credentials
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# Set host and port from env or defaults
PATHWAY_HOST = os.environ.get("PATHWAY_HOST", "localhost")
PATHWAY_PORT = os.environ.get("PATHWAY_PORT", 8000)

st.set_page_config(
    page_title="Caduceus: Healthcare Diagnostics 🏥",
    page_icon="assets/favicon.ico",
    layout="wide"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger("caduceus")
logger.setLevel(logging.INFO)

# Instantiate the RAG client
conn = RAGClient(url=f"http://{PATHWAY_HOST}:{PATHWAY_PORT}")

def enhance_with_groq(prompt: str) -> str:
    """Sends the response from Pathway RAG to Groq for refinement."""
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=False,
            stop=None
        )
        response = completion.choices[0].message.content
        clean_response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        
        return clean_response
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "Error processing the request with Groq."

# Sidebar: Display system info and indexed files
with st.sidebar:
    st.title("🩺 Caduceus AI")
    st.write("Healthcare Diagnostics Support System")
    st.info(
        "See the source code [here](https://github.com/haruki25/caduceus).",
        icon=":material/code:"
    )
    st.markdown("---")
    
    # **File Upload Section**
    st.markdown("### Upload Document to Google Drive")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "pptx"])

    # Fetch folder ID from app.yaml
    with open("app.yaml", "r") as file:
        app_yaml = file.read()
    folder_id = re.search(r"(object_id:\s*)([^\n]+)", app_yaml)
    if folder_id:
        folder_id = folder_id.group(2)
    else:
        folder_id = ""

    if uploaded_file:
        parent_folder_id = os.getenv("FOLDER_ID", folder_id)

        def upload_to_drive(file, folder_id):
            """Uploads the file to Google Drive in the specified folder."""
            file_metadata = {"name": file.name, "parents": [folder_id]}
            media = MediaIoBaseUpload(file, mimetype="application/octet-stream")
            uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            return uploaded.get("id")

        if st.button("Upload & Refresh"):
            file_id = upload_to_drive(uploaded_file, parent_folder_id)
            if file_id:
                st.success(f"File uploaded successfully: {uploaded_file.name}")
                logger.info(f"File {uploaded_file.name} uploaded to Drive with ID {file_id}")
                
                # Refresh RAG pipeline
                st.warning("Refreshing RAG pipeline...")
                st.session_state["document_meta_list"] = conn.pw_list_documents(keys=[])
                st.rerun()
                st.success("RAG Index Updated Successfully!")

    st.markdown("---")
    
    # Fetch and cache document metadata
    if "document_meta_list" not in st.session_state:
        logger.info("Fetching document metadata...")
        st.session_state["document_meta_list"] = conn.pw_list_documents(keys=[])
    
    available_files = [
        meta["path"].split("/")[-1] for meta in st.session_state["document_meta_list"]
    ]
    if available_files:
        st.markdown("### Indexed Files 📂")
        st.markdown("\n".join(f"- {file}" for file in available_files))
    else:
        st.write("No indexed files found.")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state["document_meta_list"] = conn.pw_list_documents(keys=[])
        st.rerun()

# Custom CSS for input and button enhancements
st.markdown(
    """
    <style>
        div[data-baseweb="base-input"] input {
            font-size: 18px !important;
            padding: 10px !important;
        }
        button[data-testid="baseButton-primary"] {
            background-color: #0066CC !important;
            color: white !important;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 16px;
        }
        button[data-testid="baseButton-primary"]:hover {
            background-color: #004499 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Chat Interface
with st.container(border=True):
    left, right = st.columns([1,15], vertical_alignment="bottom")
    with left:
        st.image("assets/medical.png", width=50)
    with right:
        st.title("Caduceus AI")
    st.write("Enter your healthcare-related query in the chat below.")

# Initialize conversation history if not already present
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello, I am Caduceus AI. How can I help you today?"}
    ]

# Display all conversation messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Capture user input using the chat input component
user_input = st.chat_input("Type your question here...")
if user_input:
    # Append and display the user's message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    logger.info(f"User question: {user_input}")

    # Retrieve response from the RAG client with a spinner
    with st.spinner("Retrieving AI-generated response..."):
        try:
            api_response = conn.pw_ai_answer(user_input)
            response_text = api_response.get("response", "No response received.")
            groq_response = enhance_with_groq(user_input + " " + "RAG Response:" + response_text)
        except Exception as e:
            logger.error(f"Error fetching response: {e}")
            response_text = "⚠️ An error occurred while fetching the response."

    # Append and display the assistant's response
    st.session_state["messages"].append({"role": "assistant", "content": groq_response})
    st.chat_message("assistant").write(groq_response)
