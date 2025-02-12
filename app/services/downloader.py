import yt_dlp
import os
import re
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