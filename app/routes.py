from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, jsonify, session, current_app
from app.services.downloader import DownloadValidationError, get_video_info, download_video, download_images
from flask_wtf.csrf import CSRFProtect
from urllib.parse import urlparse
from app.utils.file_manager import FileManager
import os
from flask import send_file, after_this_request
from pathlib import Path
from config import Config  

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


@main.route("/handle_image", methods=["GET", "POST"])
def handle_image():
    if request.method == "GET":
        # If accessed via GET, redirect to the index page
        return redirect(url_for("main.index"))
    
    url = request.form.get("image_url")
    if not url:
        flash("Please enter a valid image URL", "danger")
        return redirect(url_for("main.index"))
    
    # Validate image URL
    try:
        domain = urlparse(url).netloc
        if not any(allowed in domain for allowed in Config.ALLOWED_IMAGE_DOMAINS):
            raise DownloadValidationError("Unsupported image domain")
        
        # Store the URL in session for the next step
        session['image_url'] = url
        return render_template("image_download.html", url=url)
    
    except DownloadValidationError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Error processing image URL: {str(e)}", "danger")
    return redirect(url_for("main.index"))

@main.route("/process_image_download/<path:url>", methods=["GET"])
def process_image_download(url):
    try:
        # Download images
        download_result = download_images(url)
        
        # Store the download info in session for browsing
        session['image_download_dir'] = download_result['directory']
        session['image_files'] = download_result['files']
        
        return jsonify({
            'success': True,
            'message': f"Downloaded {download_result['count']} images successfully",
            'count': download_result['count']
        })
    except Exception as e:
        current_app.logger.error(f"Image download failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@main.route("/download_images_zip", methods=["GET"])
def download_images_zip():
    try:
        # Get the first image from the session
        image_files = session.get('image_files', [])
        if not image_files:
            flash("No images found", "danger")
            return redirect(url_for("main.index"))
        
        # Redirect to the browse images page
        return redirect(url_for("main.browse_images"))
        
    except Exception as e:
        flash(f"Download failed: {str(e)}", "danger")
        return redirect(url_for("main.index"))

@main.route("/browse_images", methods=["GET"])
def browse_images():
    image_files = session.get('image_files', [])
    if not image_files:
        flash("No images found", "danger")
        return redirect(url_for("main.index"))
    
    # Get just the filenames for display
    image_filenames = [os.path.basename(f) for f in image_files]
    
    return render_template("browse_images.html", 
                          images=image_files,
                          filenames=image_filenames,
                          count=len(image_files))

@main.route("/download_image/<int:index>", methods=["GET"])
def download_image(index):
    try:
        image_files = session.get('image_files', [])
        if not image_files or index >= len(image_files):
            flash("Image not found", "danger")
            return redirect(url_for("main.index"))
        
        image_path = image_files[index]
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        
        # Set up a callback to delete the file after it's sent
        @after_this_request
        def remove_file(response):
            # We don't delete individual images immediately as they might be viewed again
            # The entire directory will be deleted when the user is done browsing
            return response
        
        return send_from_directory(
            directory=directory,
            path=filename,
            as_attachment=True
        )
        
    except Exception as e:
        flash(f"Download failed: {str(e)}", "danger")
        return redirect(url_for("main.browse_images"))

# Update the download_video_route function
# Look for this route definition
@main.route("/download_video", methods=["POST"])
def download_video_route():
    """Download a video with the selected formats"""
    url = request.form.get("url")
    video_format = request.form.get("video_format")
    audio_format = request.form.get("audio_format")
    
    if not url or not video_format or not audio_format:
        flash("Missing required parameters", "danger")
        return redirect(url_for("main.index"))
    
    try:
        # Download the video
        output_file = download_video(url, video_format, audio_format)
        
        # Get the filename from the path
        filename = os.path.basename(output_file)
        
        # Set up a callback to delete the file after it's sent
        @after_this_request
        def remove_file(response):
            # Add code to delete the file after sending
            try:
                # Use a small delay to ensure the download completes
                def delete_later():
                    import time
                    time.sleep(5)  # Wait 5 seconds
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        current_app.logger.info(f"Deleted file: {output_file}")
                
                # Start a thread to delete the file
                import threading
                thread = threading.Thread(target=delete_later)
                thread.daemon = True
                thread.start()
            except Exception as e:
                current_app.logger.error(f"Error setting up file deletion: {str(e)}")
            return response
        
        # Send the file to the user
        return send_file(output_file, as_attachment=True, download_name=filename)
    
    except Exception as e:
        flash(f"Error downloading video: {str(e)}", "danger")
        return redirect(url_for("main.index"))

# Make sure there are no duplicate route definitions for download_video_route
# If you find another one, either remove it or rename the function and endpoint

# Update the download_image function
# REMOVE THIS DUPLICATE FUNCTION - This is causing the error
# @main.route("/download_image/<int:index>")
# def download_image(index):
#     """Download a specific image"""
#     images = session.get("images", [])
#     filenames = session.get("filenames", [])
#     
#     if not images or index >= len(images):
#         flash("Image not found", "danger")
#         return redirect(url_for("main.index"))
#     
#     image_path = images[index]
#     filename = filenames[index]
#     
#     # Set up a callback to delete the file after it's sent
#     @after_this_request
#     def remove_file(response):
#         # We don't delete individual images immediately as they might be viewed again
#         # The entire directory will be deleted when the user is done browsing
#         return response
#     
#     return send_file(image_path, as_attachment=True, download_name=filename)

# Add a new route to clean up after browsing images
@main.route("/cleanup_images")
def cleanup_images():
    """Clean up image directory after user is done browsing"""
    # Update to use image_files instead of images
    image_files = session.get("image_files", [])
    
    if image_files and len(image_files) > 0:
        # Get the directory of the first image
        image_dir = os.path.dirname(image_files[0])
        
        # Delete the directory
        FileManager.delete_directory(image_dir)
        
        # Clear session data
        session.pop("image_files", None)
        
        flash("Downloaded images have been cleaned up", "success")
    
    return redirect(url_for("main.index"))