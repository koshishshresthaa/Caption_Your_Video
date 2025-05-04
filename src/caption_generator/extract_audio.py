import ffmpeg


def extract_audio_from_video(videofilename):
    """
    Extracts audio from a video file and saves it as an MP3 file.

    Args:
        videofilename (str): The path to the input video file.

    Returns:
        The output audio file in mp3.
    """
    # Define the output audio filename by replacing the video file extension with .mp3
    audiofilename = videofilename.replace(".mp4",'.mp3')

    # Create the ffmpeg input stream
    input_stream = ffmpeg.input(videofilename)

    # Extract the audio stream from the input stream
    audio = input_stream.audio

    # Save the audio stream as an MP3 file
    output_stream = ffmpeg.output(audio, audiofilename)

    return output_stream