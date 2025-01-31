import yt_dlp
import os
import re
from config import Config

def sanitize_filename(filename):
    # Remove invalid characters
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'format': 'bestvideo,bestaudio',  # Get separate streams
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        video_formats = []
        audio_formats = []
        
        for f in info['formats']:
            format_info = {
                'format_id': f['format_id'],
                'ext': f['ext'],
                'filesize': f.get('filesize') or 0,
                'resolution': f.get('resolution', 'N/A'),
                'bitrate': f.get('abr', 'N/A'),
                'type': 'video' if f.get('vcodec') != 'none' else 'audio'
            }
            
            if format_info['type'] == 'video':
                video_formats.append(format_info)
            else:
                audio_formats.append(format_info)
        
        return {
            'title': info['title'],
            'thumbnail': info['thumbnail'],
            'video_formats': video_formats,
            'audio_formats': audio_formats,
            'url': url
        }

def download_video(url, video_format, audio_format):
    ydl_opts = {
        'format': f'{video_format}+{audio_format}',
        'outtmpl': os.path.join(Config.DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
    return os.path.basename(filename)

