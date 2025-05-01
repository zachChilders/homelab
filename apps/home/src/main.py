from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import cv2
import numpy as np
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Bear Detector API",
    description="A simple FastAPI application",
    version="1.0.0"
)

class HealthResponse(BaseModel):
    status: str

class BearDetectionResponse(BaseModel):
    contains_bear: bool
    confidence: float

@app.get("/", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy"}

def extract_key_frames(video_path: str, output_dir: str = "key_frames", abs_threshold: float = 0.85, rel_threshold: float = 1.5, min_time_diff: float = 0.5, window_size: int = 10):
    """
    Extract key frames from a video file using perceptual hash comparison with both absolute and relative thresholds.
    
    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory to save the extracted frames
        abs_threshold (float): Absolute similarity threshold (0-1). Lower values mean more key frames
        rel_threshold (float): Relative threshold multiplier for detecting significant changes
        min_time_diff (float): Minimum time difference between key frames in seconds
        window_size (int): Number of recent frames to consider for relative threshold calculation
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    min_frames_diff = int(fps * min_time_diff)
    
    frame_count = 0
    saved_count = 0
    prev_frame = None
    prev_hash = None
    last_key_frame = -min_frames_diff  # Initialize to allow first frame
    
    # Initialize sliding window for recent similarities
    recent_similarities = []
    
    def compute_phash(image):
        """Compute perceptual hash of an image."""
        # Convert to grayscale and resize to 32x32
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (32, 32))
        
        # Compute DCT transform
        dct = cv2.dct(np.float32(resized))
        dct_low = dct[:8, :8]
        
        # Compute average value (excluding first term)
        avg = (dct_low[0, 1:].sum() + dct_low[1:].sum()) / 63
        
        # Create binary hash
        return dct_low >= avg
    
    def hash_similarity(hash1, hash2):
        """Compute similarity between two perceptual hashes."""
        return 1 - np.count_nonzero(hash1 != hash2) / hash1.size
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # For the first frame, save it and continue
        if prev_frame is None:
            output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            prev_frame = frame
            prev_hash = compute_phash(frame)
            last_key_frame = frame_count
            frame_count += 1
            continue
            
        # Compute hash of current frame
        curr_hash = compute_phash(frame)
        
        # Compare hashes
        similarity = hash_similarity(curr_hash, prev_hash)
        
        # Update sliding window
        recent_similarities.append(similarity)
        if len(recent_similarities) > window_size:
            recent_similarities.pop(0)
        
        # Calculate mean and standard deviation of recent similarities
        if len(recent_similarities) >= 2:
            mean_sim = np.mean(recent_similarities)
            std_sim = np.std(recent_similarities)
            z_score = (similarity - mean_sim) / std_sim if std_sim > 0 else 0
        else:
            mean_sim = similarity
            std_sim = 0
            z_score = 0
        
        # Determine if this is a key frame based on both thresholds
        is_key_frame = False
        
        # Check absolute threshold
        if similarity < abs_threshold:
            is_key_frame = True
        
        # Check relative threshold (if we have enough history)
        if len(recent_similarities) >= 2 and z_score < -rel_threshold:
            is_key_frame = True
        
        # Save frame if it's a key frame and enough time has passed
        if is_key_frame and (frame_count - last_key_frame) >= min_frames_diff:
            output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            last_key_frame = frame_count
        
        # Always update previous frame and hash
        prev_frame = frame
        prev_hash = curr_hash
        frame_count += 1
    
    cap.release()
    return saved_count


def analyze_image_with_openai(image_path: str) -> BearDetectionResponse:
    """
    Check if an image contains a bear using OpenAI's Vision API.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        BearDetectionResponse: Response containing bear detection result and confidence
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Read the image file and encode it in base64
    with open(image_path, "rb") as image_file:
        import base64
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Send the image to OpenAI
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Does this image contain a bear? Respond with a JSON object containing 'contains_bear' (boolean) and 'confidence' (float between 0 and 1)."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            text_format=BearDetectionResponse,
            max_tokens=50
        )
    
    # Parse and validate the response
    return BearDetectionResponse.model_validate_json(response.output_text)

def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=3030, reload=True)

if __name__ == "__main__":
    main()