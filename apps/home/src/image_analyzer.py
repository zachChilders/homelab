import base64

from openai import OpenAI
from pydantic import BaseModel

from .config import OPENAI_API_KEY


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
