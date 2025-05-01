import pytest
from httpx import AsyncClient
from src.main import app
import cv2
import numpy as np
import io

@pytest.mark.asyncio
async def test_opencv_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/opencv-test")
        
        # Check status code
        assert response.status_code == 200
        
        # Check content type
        assert response.headers["content-type"] == "image/png"
        
        # Read the image data
        img_data = response.content
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Check image dimensions
        assert img.shape == (300, 300, 3)
        
        # Check if the image is mostly green (BGR format)
        # The image should be green (0, 255, 0 in BGR)
        # Allow for some variation due to compression
        mean_color = cv2.mean(img)
        assert mean_color[0] < 10  # Blue channel should be near 0
        assert mean_color[1] > 200  # Green channel should be high
        assert mean_color[2] < 10  # Red channel should be near 0 