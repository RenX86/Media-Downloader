from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from app.services.downloader import DownloadValidationError, get_video_info, download_video
from flask_wtf.csrf import CSRFProtect
from urllib.parse import urlparse
import os
import logging
from flask import current_app
from config import Config
from pathlib import Path

csrf = CSRFProtect()
main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@main.route("/handle_video", methods=["POST"])
def handle_video():
    url = request.form.get("video_url")
    if not url:
        flash("Please enter a valid video URL", "danger")
        return redirect(url_for("main.index"))
    
    # Validate video URL
    try:
        domain = urlparse(url).netloc
        if not any(allowed in domain for allowed in Config.ALLOWED_VIDEO_DOMAINS):
            raise DownloadValidationError("Unsupported video domain")
        
        video_info = get_video_info(url)
        return render_template("video_info.html", info=video_info)
    
    except DownloadValidationError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Error processing video: {str(e)}", "danger")
    return redirect(url_for("main.index"))

@main.route("/download/video", methods=["POST"])
def download_video_route():
    downloaded_file = None
    try:
        url = request.form.get("url")
        video_format = request.form.get("video_format")
        audio_format = request.form.get("audio_format")

        if not all([url, video_format, audio_format]):
            raise ValueError("URL and both formats are required")
        
        # Download the video
        downloaded_file = download_video(url, video_format, audio_format)
        
        if not downloaded_file or not os.path.exists(downloaded_file):
            raise FileNotFoundError("Download failed - file not created")

        download_dir = str(Config.DOWNLOAD_FOLDER / "videos")
        secure_name = os.path.basename(downloaded_file)

        # Use send_from_directory with a callback to delete the file
        response = send_from_directory(
            directory=download_dir,
            path=secure_name,
            as_attachment=True,
            mimetype="application/octet-stream"
        )

        # Add callback to delete file after sending
        @response.call_on_close
        def cleanup():
            try:
                file_path = Path(downloaded_file)
                if file_path.exists():
                    file_path.unlink()
                    current_app.logger.info(f"Successfully deleted file: {secure_name}")
            except Exception as e:
                current_app.logger.error(f"Error deleting file {secure_name}: {str(e)}")

        return response

    except Exception as e:
        # Clean up file if download or sending fails
        if downloaded_file and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
                current_app.logger.info(f"Cleaned up file after error: {downloaded_file}")
            except Exception as cleanup_error:
                current_app.logger.error(f"Error cleaning up file: {str(cleanup_error)}")
        
        current_app.logger.error(f"Download failed: {str(e)}")
        flash(f"Download failed: {str(e)}", "danger")
        return redirect(url_for("main.index"))