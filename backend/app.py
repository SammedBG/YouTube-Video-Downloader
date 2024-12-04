from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import re
import uuid
from pymongo import MongoClient
import logging
import yt_dlp

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# MongoDB setup with error handling
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['youtube_downloader']
    collection = db['videos']
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    raise

# Directory to save videos
DOWNLOAD_FOLDER = os.path.abspath('downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Function to sanitize filenames
def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Use yt-dlp to download the video
        ydl_opts = {
            'format': 'best',  # Download the best quality video
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s_%(id)s.%(ext)s'),  # Save the video with a safe filename
            'noplaylist': True,  # Do not download playlists
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)  # Download the video
            
            # Get the filename from the result
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{safe_filename(result['title'])}_{result['id']}.mp4")
        
        # Save video metadata to MongoDB
        video_data = {
            'title': result['title'],
            'url': url,
            'file_path': file_path
        }
        collection.insert_one(video_data)

        return jsonify({'message': 'Download successful', 'title': result['title']}), 200

    except Exception as e:
        logging.error(f"Error downloading video: {e}", exc_info=True)
        return jsonify({'error': f'Error downloading video: {str(e)}'}), 500

@app.route('/video/<filename>', methods=['GET'])
def serve_video(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        logging.error(f"Error serving video: {e}", exc_info=True)
        return jsonify({'error': f'Error serving video: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
