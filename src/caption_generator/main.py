import os
from typing import List, Dict
import json
from logger import setup_logging
from tempfile import NamedTemporaryFile 
from logging import getLogger
import whisper
import numpy as np
from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips,VideoFileClip, ColorClip

setup_logging()

logger=getLogger('main')

class VideoTranscriber:
    def __init__(self, model_size: str = "turbo"):
        """
        Initializes the VideoTranscriber.
        """
        device = "cpu"
        self.model = whisper.load_model(model_size,device)

    def extract_audio(self, videofilename: str) -> str:
        """
        Extracts audio from a video file and saves it as an MP3.

        Args:
            video_path (str): Path to the input video file (.mp4).
            audio_path (str, optional): Desired path for the output .mp3.
                                        If None, replaces .mp4 with .mp3.

        Returns:
            str: Path to the generated audio file.
        """

        logger.info(f"Extracting audio from video file: {videofilename}")
        audiofilename = videofilename.replace(".mp4",'.mp3')

        clip=VideoFileClip(videofilename)
        clip.audio.write_audiofile(audiofilename, codec='mp3')

        return audiofilename

    def audio_to_text(self, audiofilename: str) -> str:
        """
        Transcribes an audio file to text using Whisper.

        Args:
            audiofilename (str): Path to the input audio file.

        Returns:
            str: The transcribed text.
        """
        
        # Load the Whisper model
        model = self.model
        # Transcribe with word-level timestamps
        # (requires openai-whisper >= 20231117)
        result = model.transcribe(
            audio=audiofilename,
            word_timestamps=True
        )

        # Flatten out words across all segments
        words = []
        for seg in result["segments"]:
            for w in seg.get("words", []):
                words.append({
                    "word": w["word"],
                    "start": w["start"],
                    "end": w["end"]
                })

        return words
    
        
    def video_to_text(self, videofilename: str) -> str:
        """
        Transcribes a video file to text using Whisper.

        Args:
            videofilename (str): Path to the input video file.

        Returns:
            str: The transcribed text.
        """

        logger.info(f"Transcribing video file: {videofilename}")
        # Extract audio from the video
        audiofilename = self.extract_audio(videofilename)
        
        logger.info(f"Audio extracted to: {audiofilename}")

        logger.info("Starting transcription of audio...")
        # Transcribe the extracted audio
        transcript = self.audio_to_text(audiofilename)
        
        logger.info(f"Transcription result: {transcript}")
        logger.info("Transcription completed.")
        #Remove the audio file after transcription
        os.remove(audiofilename)
        
        return transcript


def create_final_video(captions,videofilename):

    """
    Adds word-by-word captions to a video using moviepy based on timestamps.

    Parameters:
    - video_path: path to input video file
    - output_path: path for the output video file
    - captions: list of dicts with keys "word", "start", "end"
    - font: font name for the captions (default: Arial)
    - fontsize: size of the font for the captions (default: 24)
    - color: color of the caption text (default: white)
    - position: tuple for TextClip position (default: center bottom)

    This function writes the video with captions overlaid.
    """
    font='Lato-Bold'
    color='white'
    position=('center', 'bottom')
    fontsize=100
    # Load the original video
    clip = VideoFileClip(videofilename)
    
    # Create a list of TextClips for each word
    text_clips = []
    for cap in captions:
        txt = TextClip(cap.word, font=font, fontsize=fontsize, color=color)
        txt = txt.set_start(cap.start).set_end(cap.end).set_position(position)
        text_clips.append(txt)
    
    # Composite the original clip with the text clips
    final = CompositeVideoClip([clip, *text_clips])

    output_path = videofilename.replace(".mp4", "_captioned.mp4")
    with NamedTemporaryFile(delete=False,suffix=".mp4") as temp_file:
        # Create a temporary file to store the output
        # Write the final video to the temporary file
        final.write_videofile(output_path, codec='libx264', audio_codec='aac')
        

    return output_path
        
def transcribe_video(video_file:str):
    """
    Main function to demonstrate the usage of VideoTranscriber.
    """
    vt = VideoTranscriber()
    # video_file = "/home/koshish/projects/caption_generator/sample.mp4"
 
    full_text = vt.video_to_text(video_file)

    return full_text
# Example usage:
if __name__ == "__main__":
    transcribe_video()
