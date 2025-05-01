from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import cv2
import numpy as np
from fastapi.responses import StreamingResponse
import io

app = FastAPI(
    title="Home API",
    description="A simple FastAPI application",
    version="1.0.0"
)

class HealthResponse(BaseModel):
    status: str

@app.get("/", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy"}

@app.get("/opencv-test")
async def opencv_test():
    # Create a simple image with OpenCV
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[:] = (0, 255, 0)  # Fill with green color
    cv2.putText(img, "OpenCV Test", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Convert image to bytes
    _, buffer = cv2.imencode('.png', img)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/png")

def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=3030, reload=True)

if __name__ == "__main__":
    main()