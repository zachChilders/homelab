"""
Environment variables
"""

import os

from dotenv import load_dotenv

load_dotenv()

VIDEO_PATH = os.environ.get("VIDEO_PATH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WEBHOOK = os.environ.get("WEBHOOK")