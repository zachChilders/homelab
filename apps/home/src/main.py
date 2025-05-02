from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from .video_processor import extract_key_frames
from .image_analyzer import analyze_image_with_openai, BearDetectionResponse

# Load environment variables
load_dotenv()

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
    uvicorn.run("src.main:app", host="0.0.0.0", port=3030, reload=True)

if __name__ == "__main__":
    main()