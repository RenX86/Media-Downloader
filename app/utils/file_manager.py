import os
import shutil
from pathlib import Path
from flask import current_app
import threading
import time

class FileManager:
    """Utility class to manage downloaded files"""
    
    @staticmethod
    def delete_file(file_path):
        """Delete a file after it has been sent to the user"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                current_app.logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def delete_directory(dir_path):
        """Delete a directory and all its contents"""
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                current_app.logger.info(f"Deleted directory: {dir_path}")
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting directory {dir_path}: {str(e)}")
            return False
    
    @staticmethod
    def delayed_delete(file_path, delay=5):
        """Delete a file after a short delay to ensure download completes"""
        def delete_after_delay():
            time.sleep(delay)
            FileManager.delete_file(file_path)
        
        thread = threading.Thread(target=delete_after_delay)
        thread.daemon = True
        thread.start()
    
    @staticmethod
    def delayed_delete_directory(dir_path, delay=5):
        """Delete a directory after a short delay to ensure download completes"""
        def delete_after_delay():
            time.sleep(delay)
            FileManager.delete_directory(dir_path)
        
        thread = threading.Thread(target=delete_after_delay)
        thread.daemon = True
        thread.start()