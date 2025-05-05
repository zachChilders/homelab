import logging
import time
import requests

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .image_analyzer import analyze_image_with_openai
from .video_processor import extract_key_frames
from .config import WEBHOOK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, output_dir: str = "key_frames"):
        self.output_dir = output_dir
        super().__init__()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            logging.info(f"New video file detected: {event.src_path}")
            try:
                num_frames = extract_key_frames(
                    video_path=event.src_path,
                    output_dir=self.output_dir,
                    rel_threshold=1.5,
                    abs_threshold=0.5,
                    min_time_diff=0.5
                )
                logging.info(f"Extracted {num_frames} key frames from {event.src_path}")
            except Exception as e:
                logging.error(f"Error processing {event.src_path}: {e!s}")

class ImageFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            logging.info(f"New image file detected: {event.src_path}")
            try:
                result = analyze_image_with_openai(event.src_path)
                logging.info(f"Analysis result for {event.src_path}: contains_bear={result.contains_bear}, confidence={result.confidence}")

                if result.contains_bear:
                    requests.post(WEBHOOK, json={"message": f"Bear detected in {event.src_path}"})
            except Exception as e:
                logging.error(f"Error analyzing {event.src_path}: {e!s}")

def watch_folder(path: str, output_dir: str = None, handler_type: str = "video"):
    """
    Watch a folder for new files and process them when detected.    
    Args:
        path (str): Path to the folder to watch
        output_dir (str): Directory to save the extracted frames (for video handler)
        handler_type (str): Type of handler to use ("video" or "image")
    """
    if handler_type == "video":
        event_handler = VideoFileHandler(output_dir)
        watch_path = path
        recursive = False
    else:
        event_handler = ImageFileHandler()
        watch_path = output_dir or path
        recursive = True  # Watch recursively for key frames in subdirectories

    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=recursive)
    observer.start()

    logging.info(f"Started watching folder: {watch_path} for {handler_type} files (recursive={recursive})")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopped watching folder")

    observer.join()
