from flask import Blueprint, render_template, request, send_from_directory, flash
from app.services.downloader import get_video_info, download_video
from urllib.parse import urlparse
from config import Config
import logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash('Please enter a valid URL', 'danger')
            return render_template('index.html')
        
        # Validate domain
        domain = urlparse(url).netloc
        if not any(allowed in domain for allowed in Config.ALLOWED_DOMAINS):
            flash('Domain not allowed', 'danger')
            return render_template('index.html')
        
        try:
            video_info = get_video_info(url)
            return render_template('info.html', info=video_info)
        except Exception as e:
            flash(str(e), 'danger')
    
    return render_template('index.html')

@main.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    video_format = request.form.get('video_format')
    audio_format = request.form.get('audio_format')
    
    try:
        if not video_format or not audio_format:
            raise ValueError("Both video and audio formats must be selected")
            
        filename = download_video(url, video_format, audio_format)
        return send_from_directory(
            directory=Config.DOWNLOAD_FOLDER,
            path=filename,
            as_attachment=True,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        flash(f"Download failed: {str(e)}", 'danger')
        return render_template('index.html')
    
