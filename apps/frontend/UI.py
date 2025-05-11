import streamlit as st
import requests
import json
import pandas as pd

# Configuration
API_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000")

st.title("Caption Your Video")

# Step 1: Upload video
st.header("1. Upload your video")
uploaded_file = st.file_uploader("Choose an MP4 video file", type=["mp4"])

if uploaded_file:
    if st.button("Transcribe Video"):
        with st.spinner("Uploading and transcribing..."):
            files = {"file": (uploaded_file.name, uploaded_file, "video/mp4")}
            resp = requests.post(f"{API_URL}/uploadfile/", files=files)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.video_id = data["video_id"]
            st.session_state.original_caption = data["caption"]
            # Store as DataFrame for easy access
            st.session_state.caption_df = pd.DataFrame(
                st.session_state.original_caption
            )
            st.success("Transcription complete.")
        else:
            st.error(f"Error: {resp.status_code} - {resp.text}")

# Step 2: Edit caption with timestamps (simple list)
if st.session_state.get("caption_df") is not None:
    st.header("2. Edit caption and timestamps")
    df = st.session_state.caption_df
    # Display each word with its timestamps in a text input
    corrected = []
    for i, row in df.iterrows():
        label = f"Word {i+1} [{row['start']:.2f}s - {row['end']:.2f}s]"
        word_input = st.text_input(label, value=row['word'], key=f"word_{i}")
        corrected.append({
            "word": word_input,
            "start": float(row['start']),
            "end": float(row['end'])
        })
    if st.button("Confirm Correction"):
        payload = {"video_id": st.session_state.video_id, "corrected_caption": corrected}
        with st.spinner("Submitting corrections..."):
            resp = requests.post(f"{API_URL}/correctcaption", json=payload)
        if resp.status_code == 200:
            st.success("Captions updated!")
            st.session_state.corrected_caption = corrected
        else:
            st.error(f"Error: {resp.status_code} - {resp.text}")

#Step 3: Generate, preview & download
if st.session_state.get("corrected_caption"):
    st.header("3. Generate & Preview Captioned Video")
    if st.button("Generate & Preview"):
        with st.spinner("Rendering and downloading..."):
            resp = requests.get(f"{API_URL}/createvideowithcaption", stream=True)
        if resp.status_code == 200:
            video_bytes = resp.content
            st.success("Here’s your captioned video!")
            # In‐page preview
            st.video(video_bytes)

            # Download button
            downloaded = st.download_button(
                label="Download Captioned Video",
                data=video_bytes,
                file_name=f"{st.session_state.video_id}_captioned.mp4",
                mime="video/mp4"
            )
            # Refresh page after download
            if downloaded:
                st.rerun()
        else:
            st.error(f"Failed to generate video: {resp.status_code}")

