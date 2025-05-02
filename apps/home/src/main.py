import os
import threading

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from .file_watcher import watch_folder
from .config import VIDEO_PATH, FRAMES_PATH

app = FastAPI(
    title="Bear Detector",
    description="Detects bears in security camera videos",
    version="1.0.0"
)

class HealthResponse(BaseModel):
    status: str

@app.get("/", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy"}

def main():
    # Start the video file watcher in a separate thread
    video_path = VIDEO_PATH
    if video_path:
        if not os.path.exists(video_path):
            raise ValueError(f"VIDEO_PATH {video_path} does not exist")
        if not os.path.isdir(video_path):
            raise ValueError(f"VIDEO_PATH {video_path} is not a directory")

        video_watcher_thread = threading.Thread(
            target=watch_folder,
            args=(video_path, "key_frames", "video"),
            daemon=True
        )
        video_watcher_thread.start()

    # Start the image file watcher in a separate thread
    frames_path = FRAMES_PATH
    if frames_path:
        if not os.path.exists(frames_path):
            raise ValueError(f"FRAMES_PATH {frames_path} does not exist")
        if not os.path.isdir(frames_path):
            raise ValueError(f"FRAMES_PATH {frames_path} is not a directory")

        image_watcher_thread = threading.Thread(
            target=watch_folder,
            args=(frames_path, None, "image"),
            daemon=True
        )
        image_watcher_thread.start()

    # Start the FastAPI server
    uvicorn.run("src.main:app", host="0.0.0.0", port=3030, reload=True)

if __name__ == "__main__":
    main()
