import os
from typing import List, Dict
from tempfile import NamedTemporaryFile
from logging import getLogger
import whisper
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip

logger = getLogger(__name__)

class VideoTranscriber:
    def __init__(self, model_size: str = "turbo"):
        """
        Initializes the VideoTranscriber.
        """
        device = "cpu"
        self.model = whisper.load_model(model_size, device)

    def extract_audio(self, videofilename: str) -> str:
        """
        Extracts audio from a video file and saves it as an MP3.
        """
        logger.info(f"Extracting audio from video file: {videofilename}")
        audiofilename = videofilename.replace(".mp4", ".mp3")
        clip = VideoFileClip(videofilename)
        clip.audio.write_audiofile(audiofilename, codec='mp3')
        return audiofilename

    def audio_to_text(self, audiofilename: str) -> List[Dict]:
        """
        Transcribes an audio file to text using Whisper.
        """
        result = self.model.transcribe(
            audio=audiofilename,
            word_timestamps=True
        )
        words = [
            {"word": w["word"], "start": w["start"], "end": w["end"]}
            for seg in result["segments"]
            for w in seg.get("words", [])
        ]
        return words

    def video_to_text(self, videofilename: str) -> List[Dict]:
        """
        Transcribes a video file to text using Whisper.
        """
        logger.info(f"Transcribing video file: {videofilename}")
        audiofilename = self.extract_audio(videofilename)
        logger.info(f"Audio extracted to: {audiofilename}")

        logger.info("Starting transcription of audio...")
        transcript = self.audio_to_text(audiofilename)
        logger.info(f"Transcription result: {transcript}")
        logger.info("Transcription completed.")

        os.remove(audiofilename)
        return transcript

    def create_final_video(self, captions: List[Dict], videofilename: str):
        """
        Adds word-by-word captions to a video using moviepy based on timestamps.
        """
        logger.info(f"Starting to generate captioned video for: {videofilename}")
        font = 'Lato-Bold'
        color = 'white'
        position = ('center', 'bottom')
        fontsize = 100

        try:
            clip = VideoFileClip(videofilename)
            logger.info(f"Loaded video: duration={clip.duration:.2f}s, fps={clip.fps}")
        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            raise

        text_clips = []
        for i, cap in enumerate(captions):
            try:
                txt = TextClip(cap.word, font=font, fontsize=fontsize, color=color)
                txt = txt.set_start(cap.start).set_end(cap.end).set_position(position)
                text_clips.append(txt)
                logger.debug(f"Added caption {i+1}: '{cap.word}' [{cap.start:.2f}s - {cap.end:.2f}s]")
            except Exception as e:
                logger.warning(f"Skipping caption {i+1} due to error: {e}")

        logger.info(f"Total text clips to overlay: {len(text_clips)}")
        final = CompositeVideoClip([clip, *text_clips])
        output_path = videofilename.replace(".mp4", "_captioned.mp4")

        try:
            with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                final.write_videofile(output_path, codec='libx264', audio_codec='aac')
            logger.info(f"Captioned video successfully created at: {output_path}")
        except Exception as e:
            logger.error(f"Failed to render captioned video: {e}")
            raise

        return output_path

