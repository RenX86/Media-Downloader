import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALLOWED_DOMAINS = ['youtube.com', 'youtu.be', 'vimeo.com','instagram.com']
    BASE_DIR = Path(__file__).parent.parent
    DOWNLOAD_FOLDER = BASE_DIR / 'downloads'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    # MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    @staticmethod
    def init_app(app):
        Config.DOWNLOAD_FOLDER.mkdir(exist_ok=True)