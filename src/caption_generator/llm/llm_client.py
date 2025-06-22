from dotenv import load_dotenv
import os
from typing import Dict, Any
from logconfig import setup_logging
from logging import getLogger
from moviepy.editor import VideoFileClip
from google import genai
from google.genai import types

setup_logging()
logger = getLogger("llm")


#Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

class LLMClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        logger.info(f"Initializing LLMClient with model: {model_name}")
        if not GEMINI_API_KEY:
            logger.warning("GOOGLE_API_KEY is not set. LLM client may not function properly.")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = model_name

    def _extract_audio(self, videofilename: str) -> str:
        logger.info(f"Extracting audio from: {videofilename}")
        try:
            audiofilename = videofilename.replace(".mp4", ".mp3")
            clip = VideoFileClip(videofilename)
            clip.audio.write_audiofile(audiofilename, codec='mp3')
            logger.info(f"Audio saved to: {audiofilename}")
            return audiofilename
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            raise

    def create_message(self, src, tgt, human_prompt):
        logger.debug(f"Creating prompt with src={src}, tgt={tgt}")
        task_action = 'transcribe and translate' if src != tgt else 'transcribe'
        message = human_prompt.format(src=src, tgt=tgt, task_action=task_action)
        logger.debug(f"Formatted human message: {message}")
        return message

    def _run(self, message, sys_instruction: str, audio_filename: str) -> Dict[str, Any]:
        logger.info("Sending request to LLM model")
        try:

            myfile = self.client.files.upload(file=audio_filename)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[message,myfile],
                config=types.GenerateContentConfig(system_instruction=sys_instruction)
            )
            logger.info("Received response from LLM model")
            return response.text
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise
