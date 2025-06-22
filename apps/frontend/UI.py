
import streamlit as st
import requests
import pandas as pd

from logconfig import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger("frontend")

API_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000")
logger.debug(f"API_URL set to {API_URL}")

st.title("Caption Your Video")
logger.info("Streamlit app started")

uploaded_file = st.file_uploader("Choose an MP4 video file", type=["mp4"])
if uploaded_file:
    if st.button("Transcribe Video"):
        logger.info("Transcribe button clicked")
        with st.spinner("Uploading and transcribing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "video/mp4")}
                resp = requests.post(f"{API_URL}/uploadfile/", files=files)
                logger.info("Sent /uploadfile request")
            except Exception:
                logger.exception("Failed to send /uploadfile request")
                st.error("Upload failed")
                st.stop()

        if resp.status_code == 200:
            data = resp.json()
            vid = data.get("video_id")
            cap = data.get("caption")
            st.session_state["video_id"] = vid
            st.session_state["caption_df"] = pd.DataFrame(cap)
            st.success("Transcription complete.")
            logger.info(f"Transcription success, video_id={vid}")
        else:
            logger.error(f"/uploadfile failed: {resp.status_code} {resp.text}")
            st.error(f"Error: {resp.status_code}")

if st.session_state.get("caption_df") is not None:
    st.header("2. Edit caption and timestamps")
    df = st.session_state.caption_df

    if not st.session_state.get("correction_submitted", False):
        corrected = []
        for i, row in df.iterrows():
            label = f"Word {i+1} [{row['start']:.2f}s - {row['end']:.2f}s]"
            word = st.text_input(label, value=row["word"], key=f"word_{i}")
            corrected.append({"word": word, "start": float(row["start"]), "end": float(row["end"])})

        if st.button("Confirm Correction"):
            logger.info("Confirm Correction clicked")
            payload = {"video_id": st.session_state.video_id, "corrected_caption": corrected}
            with st.spinner("Submitting corrections..."):
                try:
                    resp = requests.post(f"{API_URL}/correctcaption", json=payload)
                    logger.info("/correctcaption request sent")
                except Exception:
                    logger.exception("Failed /correctcaption request")
                    st.error("Submission failed")
                    st.stop()

            if resp.status_code == 200:
                st.session_state["corrected_caption"] = corrected
                st.session_state["correction_submitted"] = True
                logger.info("Caption correction successful")
                st.rerun()  # Refresh the app to hide inputs immediately
            else:
                logger.error(f"/correctcaption failed: {resp.status_code}")
                st.error(f"Error: {resp.status_code}")
    else:
        st.success("✅ Captions updated.")


if st.session_state.get("corrected_caption"):
    st.header("3. Generate & Preview Captioned Video")
    if st.button("Generate & Preview"):
        logger.info("Generate & Preview clicked")
        with st.spinner("Rendering and downloading..."):
            try:
                resp = requests.get(f"{API_URL}/createvideowithcaption", stream=True)
                logger.info("/createvideowithcaption request sent")
            except Exception:
                logger.exception("Failed /createvideowithcaption request")
                st.error("Generation failed")
                st.stop()

        if resp.status_code == 200:
            video_bytes = resp.content
            st.video(video_bytes)
            st.success("Captioned video ready!")
            logger.info("Captioned video received")
            download = st.download_button(
                label="Download",
                data=video_bytes,
                file_name=f"{st.session_state.video_id}_captioned.mp4",
                mime="video/mp4"
            )
            if download:
                st.rerun()
                logger.info("Download button clicked")
        else:
            logger.error(f"/createvideowithcaption failed: {resp.status_code}")
            st.error(f"Error: {resp.status_code}")
