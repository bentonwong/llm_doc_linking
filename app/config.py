from dotenv import load_dotenv
from pathlib import Path
import os

if Path(".env").exists():
    load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
