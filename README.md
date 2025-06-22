# 🎬 Auto-Captioning Tool

## 📌 Overview

This project automates the process of adding captions to videos. Frustrated with the slow, manual captioning process and ad-filled free apps, I built this tool to streamline the workflow. It uses OpenAI Whisper for transcription and provides an interface to review and correct captions. Future enhancements include customizable fonts and styles.

## ✨ Features

- Automatic caption generation using OpenAI Whisper
- User-friendly interface for reviewing and editing captions
- Upcoming features: customizable fonts and styles

## 🛠️ Built With

- [OpenAI Whisper](https://github.com/openai/whisper) – Speech recognition  
- [FastAPI](https://fastapi.tiangolo.com/) – Backend API  
- [Streamlit](https://streamlit.io/) – Frontend interface  
- [uv](https://astral.sh/blog/uv-unified-python-packaging) – Python package & environment management  

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher  
- [uv](https://astral.sh/blog/uv-unified-python-packaging) installed  

### Installation

#### Clone the repository:
   ```bash
   git clone https://github.com/yourusername/auto-captioning-tool.git
   cd auto-captioning-tool
   ```

#### Install dependencies and sync environments:

```bash
uv sync
```

#### Running the Application
Use uv run to start both the frontend and backend:

```bash
uv run -m streamlit run apps/frontend/UI.py
uv run -m apps.server.api
```
