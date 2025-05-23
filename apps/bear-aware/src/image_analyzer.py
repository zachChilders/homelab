import base64
import json
import logging

from openai import OpenAI
from pydantic import BaseModel

from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class BearDetectionResponse(BaseModel):
    contains_bear: bool
    confidence: float

def analyze_image_with_openai(image_path: str) -> BearDetectionResponse:
    """
    Check if an image contains a bear using OpenAI's Vision API.    
    Args:
        image_path (str): Path to the image file

    Returns:
        BearDetectionResponse: Response containing bear detection result and confidence
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Read the image file and encode it in base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Send the image to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
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
            max_tokens=50
        )

    # Parse the response text as JSON and validate with Pydantic
    response_text = response.choices[0].message.content
    
    # Strip markdown code block syntax if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove ```json
    if response_text.startswith("```"):
        response_text = response_text[3:]  # Remove ```
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove trailing ```
    response_text = response_text.strip()
    
    try:
        response_json = json.loads(response_text)
        return BearDetectionResponse(**response_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {response_text}")
        raise
