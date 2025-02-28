# Caduceus 🩺

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**Clinical Augmentation & Diagnostic Understanding Expert System**

Caduceus is an AI-powered clinical support system designed to help hospital staff and doctors access and analyze patient medical records efficiently. The system aggregates information from multiple sources and presents it in a structured format, eliminating the need to manually review extensive patient histories and medical charts.

## Purpose

Caduceus is specifically engineered for healthcare professionals, streamlining clinical workflows by:

- Providing rapid access to patient medical information
- Organizing and summarizing medical documents
- Facilitating context-aware medical question answering
- Supporting clinical decision making through AI-powered analysis

## Core Components

![image](assets/flow.png)

### Data Management

- **Google Drive Integration**
  - Secure access to medical documents (PDF/PPTX)
  - Real-time document synchronization (30-second refresh interval)
  - Patient folder organization and selection

### Technical Architecture

- **Retrieval-Augmented Generation (RAG) Pipeline**
  - Document parsing and chunking via Pathway framework
  - Semantic search with embeddings (OpenAI)
  - Adaptive retrieval for optimal document context
  - Integration with LLM models (GPT-4o-mini via OpenAI, Deepseek models via Groq)

### User Interface

- **Streamlit-Based Dashboard**
  - Patient selection interface
  - Real-time chat interaction
  - Document upload capabilities
  - Index refresh functionality

## System Requirements

- Python 3.10 or higher
- Google Drive API access
- Groq API key (for enhanced responses)
- OpenAI API key (for embedding and RAG)

## Installation

### Using Docker (Recommended)

The easiest way to deploy Caduceus is with Docker:

```bash
# Clone repository
git clone https://github.com/yourusername/caduceus.git
cd caduceus

# Configure credentials
cp .env.example .env
# Edit .env with your API keys and Google Drive folder ID

# Start containers
docker-compose up -d
```

### Manual Installation

For development or custom setups:

1. Clone repository:
```bash
git clone https://github.com/haruki25/caduceus.git
cd caduceus
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install pathway[all]
```

3. Set up credentials:
   - Create a Google Service Account and download `credentials.json`
   - Configure API keys in `.env` file:
```
OPENAI_API_KEY="your_openai_key"
GROQ_API_KEY="your_groq_key"
PARENT_FOLDER_ID="your_google_drive_folder_id"
```

## Configuration

### Google Drive Setup

1. Create a service account in Google Cloud Console
2. Download credentials as `credentials.json`
3. Enable Google Drive API
4. Create a parent folder in Google Drive to store patient folders
5. Share the parent folder with the service account email (with Editor permissions)
6. Create subfolders within the parent folder, one for each patient

### Application Configuration

The primary configuration is in `app.yaml`, which controls:
- Document source (Google Drive folder ID)
- Embedding model settings
- LLM configuration
- Document processing parameters
- Server settings

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Select a patient folder from the dropdown menu
3. Click "Load Data" to initialize the system
4. Interact with the clinical support chat interface

### Adding Patient Documents

You can add documents directly through the UI:
1. Navigate to the file upload section in the sidebar
2. Upload PDF or PPTX files
3. Click "Upload & Refresh" to add files to Google Drive and refresh the index

## Architecture Details

### Backend

- **Pathway Framework**: Orchestrates the RAG pipeline
- **Document Processing**: Automatically splits documents into semantic chunks
- **Vector Database**: Stores embeddings for efficient retrieval
- **REST API**: Exposes endpoints for querying the system

### Frontend

- **Streamlit UI**: Provides an intuitive interface for healthcare professionals
- **Chat Interface**: Facilitates natural language interactions
- **Document Management**: Allows document upload and index refreshing

## Security Considerations

Caduceus is designed with healthcare data security in mind:

- Credential-based access to patient data
- Isolated Docker containers
- API key management through environment variables

**Note**: While the system implements security measures, administrators should perform a security audit before deploying in production healthcare environments.

## Limitations & Disclaimers

- This system is intended for clinical support only and should not replace professional medical judgment
- Always verify AI-generated responses against primary sources
- The system does not currently implement full HIPAA compliance features
- Groq integration for enhanced responses may increase latency

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Important**: Always consult with your IT security team and compliance officers before deploying in a production healthcare environment.
