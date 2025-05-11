from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import uvicorn
from tempfile import NamedTemporaryFile 
from pydantic import BaseModel
from caption_generator import transcribe_video,create_final_video
from logger import setup_logging
from logging import getLogger
import os
from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips,VideoFileClip, ColorClip

from typing import List
setup_logging()

logger=getLogger('server')


app = FastAPI()


# In-memory store for single processing
_CAPTIONS = {}

_VIDEO_ID = ""

_VIDEOFILEPATH = ""


class CaptionEntry(BaseModel):
    word: str
    start: float
    end: float


class CaptionUpdate(BaseModel):
    video_id: str
    corrected_caption: List[CaptionEntry]


@app.get("/")
def root():
    return {"message": "Welcome to Caption Generator API"}


@app.post("/uploadfile/")
def create_upload_file(file: UploadFile):
    """
    Upload a video file and process it.

    Args:
        file (UploadFile): The video file to be processed.
        
    """
    global _CAPTIONS
    global _VIDEOFILEPATH
    global _VIDEO_ID
    logger.info(f"Received file: {file.filename}")
    with NamedTemporaryFile(delete=False,suffix=".mp4") as temp_file:
        temp_file.write(file.file.read())
        temp_file_path = temp_file.name
        _VIDEOFILEPATH = temp_file_path

        # Process the video file
        logger.info(f"Processing video file: {temp_file_path}")
        generated_caption=transcribe_video(temp_file_path)

    logger.info(f"Generated caption: {generated_caption}")
    #create unique id to store the caption
    _VIDEO_ID = file.filename.split('.')[0]
    _CAPTIONS[_VIDEO_ID] = generated_caption

    return {"video_id": _VIDEO_ID, "caption": generated_caption}


@app.post("/correctcaption")
def correct_caption(update: CaptionUpdate):
    global _CAPTIONS
    """
    Correct the caption based on the provided JSON data.

    Args:
        json_data (dict): The JSON data containing the caption information.
        
    """
    logger.info(f"Received correction for video_id: {update.video_id}")
    logger.info(f"Corrected caption: {update.corrected_caption}")
    # Update the caption in the in-memory store
    _CAPTIONS[update.video_id]= update.corrected_caption

    # Convert to line-level timestamp
    return {"video_id": update.video_id, "caption": update.corrected_caption}


@app.get("/caption/{video_id}")
def get_caption(video_id: str):
    """
    Retrieve the current caption for a given video_id.
    """

    logger.info(f"Retrieving caption for video_id: {video_id}")
    caption = _CAPTIONS.get(video_id)

    return {"video_id": video_id, "caption": caption}

@app.delete("/caption/{video_id}")
def delete_caption(video_id: str):
    """
    Delete the stored caption for a video_id (cleanup).
    """

    logger.info(f"Deleting caption for video_id: {video_id}")
    removed = _CAPTIONS.pop(video_id, None)
    return {"deleted": bool(removed)}


@app.get("/createvideowithcaption")
def create_video_with_caption():
    """
    Create a video with the caption overlay.
    """

    global _CAPTIONS
    global _VIDEOFILEPATH
    global _VIDEO_ID
    framesize = (1920,1080)
    logger.info(f"Creating video with caption...")
    # print("linelevl caption is",_LINELEVEL_CAPTIONS)
    # print(type(_LINELEVEL_CAPTIONS))
    caption = _CAPTIONS.get(_VIDEO_ID)
    if not caption:
        return {"error": "Caption not found"}

    logger.info(f"Creating video with caption in highligheted format...")
        
    output_path = create_final_video(caption,_VIDEOFILEPATH)

    os.remove(_VIDEOFILEPATH)
    # Remove the temporary video file
    logger.info(f"Temporary video file removed: {_VIDEOFILEPATH}")

    logger.info(f"Video caption in highlighted format created successfully.")

    # Serve the generated video
    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=os.path.basename(output_path)
    )

def main():
    """
    Main function to run the FastAPI server.
    """
    logger.info("Starting FastAPI server...")
    uvicorn.run(app,host="127.0.0.1", port=8000)
    logger.info("FastAPI server started.")


if __name__ == "__main__":
    main()