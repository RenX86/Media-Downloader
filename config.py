import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base directory - root of the project
    BASE_DIR = Path(__file__).parent

    # Application directories
    APP_DIR = BASE_DIR / 'app'
    STORAGE_DIR = APP_DIR / 'storage'  # New storage directory within app
    DOWNLOAD_FOLDER = STORAGE_DIR / 'downloads'  # Downloads inside storage
    LOG_DIR = STORAGE_DIR / 'logs'  # Logs inside storage
    
    # Video download settings
    ALLOWED_VIDEO_DOMAINS = ['youtube.com', 'youtu.be', 'vimeo.com', 'instagram.com']
    
    # Image download settings
    ALLOWED_IMAGE_DOMAINS = ['imgur.com', 'reddit.com', 'deviantart.com', 'pixiv.net', 'wallhaven.cc', 'instagram.com']
    
    # General settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    # MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    @staticmethod
    def init_app(app):
        """Initialize application directories and logging."""
        # Create storage directory and its subdirectories
        storage_dirs = [
            app.config["STORAGE_DIR"],
            app.config["DOWNLOAD_FOLDER"],
            app.config["LOG_DIR"],
            app.config["DOWNLOAD_FOLDER"] / "videos",
            app.config["DOWNLOAD_FOLDER"] / "images"
        ]
        
        # Create all required directories
        for directory in storage_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Create .gitignore in storage directory to ignore downloaded content
