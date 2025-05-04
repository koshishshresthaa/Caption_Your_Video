import os
import whisperx
import moviepy as mp

class VideoTranscriber:
    def __init__(self, model_size: str = "small"):
        """
        Initializes the VideoTranscriber.
        """
        device = "cpu"
        compute_type = "int8"
        self.model = whisperx.load_model(model_size,device,compute_type=compute_type)

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
        audiofilename = videofilename.replace(".mp4",'.mp3')

        clip=mp.VideoFileClip(videofilename)
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
        # Whisper's transcribe method handles loading and preprocessing internally
        audio=whisperx.load_audio(audiofilename)
        result = self.model.transcribe(audio)  
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device="cpu")
        result = whisperx.align(result["segments"], model_a, metadata, audio, device="cpu", return_char_alignments=False)
        wordlevel_info = []

        for each in result['segments']:
            wordlevel_info.append({'word':each['text'].strip(),'start':each['start'],'end':each['end']})

        return wordlevel_info

    
    def video_to_text(self, videofilename: str) -> str:
        """
        Transcribes a video file to text using Whisper.

        Args:
            videofilename (str): Path to the input video file.

        Returns:
            str: The transcribed text.
        """

        print("Extracting audio from video...")
        # Extract audio from the video
        audiofilename = self.extract_audio(videofilename)
        print(audiofilename)
        
        print("Transcribing audio to text...")
        # Transcribe the extracted audio
        transcript = self.audio_to_text(audiofilename)
        
        print("Transcription complete.")
        #Remove the audio file after transcription
        os.remove(audiofilename)
        
        return transcript

# Example usage:
if __name__ == "__main__":
    vt = VideoTranscriber()
    video_file = "/home/koshish/projects/caption_generator/sample.mp4"
 
    full_text = vt.video_to_text(video_file)
    print("Full video transcript:")
    print(full_text)
