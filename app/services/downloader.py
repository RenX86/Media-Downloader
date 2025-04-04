import yt_dlp
import os
import re
import subprocess
import time
import zipfile
import shutil
from config import Config
from pathlib import Path
from werkzeug.utils import secure_filename

class DownloadValidationError(Exception):
    pass

def sanitize_filename(filename):
    secure_name = secure_filename(filename)
    return re.sub(r"[\\/*?:\"<>|]", "", secure_name)

def get_video_info(url):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "simulate": True,
        "format": "bestvideo,bestaudio",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError as e:
            raise DownloadValidationError(f"Error extracting video info: {str(e)}")
        
        # Initialize lists for video and audio formats
        video_formats = []
        audio_formats = []

        # Ensure 'formats' exists to avoid KeyError
        if "formats" not in info:
            raise DownloadValidationError("No formats found for this video")
        
        for fmt in info["formats"]:
            # Check if 'vcodec' exists to prevent KeyError
            vcodec = fmt.get("vcodec", "none")
            format_type = "video" if vcodec != "none" else "audio"
            
            # Extract relevant format details
            try:
                file_size = fmt.get("filesize", 0) or 0
                resolution = fmt.get("resolution", "Unknown")
                bitrate = fmt.get("abr", 0)
                ext = fmt.get("ext", "Unknown")
            except KeyError:
                continue  # Skip incomplete formats
            
            data = {
                "format_id": fmt["format_id"],
                "ext": ext,
                "filesize": file_size,
                "resolution": resolution,
                "bitrate": bitrate,
                "format_type": format_type
            }

            if format_type == "video":
                video_formats.append(data)
            else:
                audio_formats.append(data)
        
        # Check if formats are not empty
        if not video_formats:
            raise DownloadValidationError("No video formats found")
        if not audio_formats:
            raise DownloadValidationError("No audio formats found")
        
        # Prepare info dictionary
        return {
            "title": sanitize_filename(info["title"]),
            "thumbnail": info.get("thumbnail", ""),
            "video_formats": video_formats,
            "audio_formats": audio_formats,
            "url": url
        }

def download_video(url, video_format, audio_format):

    videos_dir = Config.DOWNLOAD_FOLDER / "videos"

    ydl_opts = {
        "format": f"{video_format}+{audio_format}",
        "outtmpl": str(videos_dir / "%(title)s.%(ext)s"),
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
        "merge_output_format": "mp4"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
        except Exception as e:
            raise DownloadValidationError(f"Download failed: {str(e)}")


def download_images(url):
    """Download images using gallery-dl and return the path to the first downloaded image"""
    images_dir = Config.DOWNLOAD_FOLDER / "images"
    
    # Create directory if it doesn't exist
    images_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Parse domain to validate
        domain = url.split('/')[2]
        if not any(allowed in domain for allowed in Config.ALLOWED_IMAGE_DOMAINS):
            raise DownloadValidationError(f"Domain {domain} is not in the allowed list")
        
        # Generate a unique subfolder for this download
        timestamp = int(time.time())
        download_dir = images_dir / f"download_{timestamp}"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Run gallery-dl to download images
        result = subprocess.run([
            "gallery-dl", 
            "--dest", str(download_dir),
            "--filename", "{filename}.{extension}",
            url
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise DownloadValidationError(f"gallery-dl error: {result.stderr}")
        
        # Find all downloaded files
        downloaded_files = list(download_dir.glob('**/*.*'))
        if not downloaded_files:
            raise DownloadValidationError("No images were downloaded")
        
        # Return information about downloaded files
        return {
            'directory': str(download_dir),
            'files': [str(f) for f in downloaded_files],
            'count': len(downloaded_files)
        }
    
    except Exception as e:
        raise DownloadValidationError(f"Failed to download images: {str(e)}")