from .prompts import (SYSTEM_PROMPT, USER_PROMPT )
from .llm_client import LLMClient
from typing import Dict, Any
from logconfig import setup_logging
from logging import getLogger

setup_logging()
logger = getLogger("llm")

def generate_caption(llm_client: LLMClient,video_path:str, src: str, tgt: str) -> Dict[str, Any]:
    """
    Generates a caption for the given video using the LLM.

    Args:
        audio_filename (str): The path to the audio file extracted from the video.
        src (str): The source text to be captioned.
        tgt (str): The target text to be generated.
        human_prompt (str): The human-readable prompt for the LLM.

    Returns:
        Dict[str, Any]: The response from the LLM containing the generated caption.
    """

    message = llm_client.create_message(src, tgt, USER_PROMPT)
    
    logger.info(f"Generating caption  with message: {message}")

    audio_filename = llm_client._extract_audio(video_path)

    response = llm_client._run(message, SYSTEM_PROMPT, audio_filename)

    return response

if __name__ == "__main__":
    # Example usage
    llm_client = LLMClient(model_name="gemini-2.5-flash")
    video_path = "/home/koshish/projects/caption_generator/sample.mp4"
    src = "English"
    tgt = "English"
    
    caption_response = generate_caption(llm_client, video_path, src, tgt)
    print(caption_response)