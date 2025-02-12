from flask import Flask
from config import Config
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
from app.routes import main
from app.services import downloader

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Configure caching
    cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

    # Configure logging
    if not app.debug:

        log_file = app.config["LOG_DIR"] / "media_downloader.log"

        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Media Downloader startup")

    # Register blueprints
    app.register_blueprint(main)

    return app