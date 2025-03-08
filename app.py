from flask import Flask, render_template, request, send_file, redirect, url_for
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
import tempfile
import os
import io
import re
import urllib.request
from functools import wraps

app = Flask(__name__)

def sanitize_filename(filename):
    # Remove invalid characters and trim length
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename[:200]  # Limit length to avoid path issues

def set_user_agent(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['headers'] = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        return func(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format = request.form['format']
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return render_template('error.html', error="Please enter a valid URL")
        
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    yt = YouTube(url, on_progress_callback=on_progress)
                    try:
                        title = sanitize_filename(yt.title)
                    except:
                        title = "Video"  # Default title if retrieval fails
                    
                    if format == 'mp4':
                        stream = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
                        if stream is None:
                            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
                        if stream is None:
                            return render_template('error.html', error="No suitable MP4 stream found.")
                        
                        file_path = stream.download(output_path=temp_dir, filename=f"{title}.mp4")
                        mime_type = 'video/mp4'
                        
                    elif format == 'mp3':
                        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                        if stream is None:
                            return render_template('error.html', error="No suitable MP3 stream found.")
                        
                        file_path = stream.download(output_path=temp_dir, filename=f"{title}.mp3")
                        mime_type = 'audio/mpeg'

                    else:
                        return render_template('error.html', error="Invalid format specified.")
                    
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    buffer = io.BytesIO(file_data)
                    buffer.seek(0)
                    
                    return send_file(
                        buffer,
                        as_attachment=True,
                        download_name=os.path.basename(file_path),
                        mimetype=mime_type
                    )

                except RegexMatchError:
                    return render_template('error.html', error="Invalid YouTube URL.")
                except VideoUnavailable:
                    return render_template('error.html', error="This video is unavailable.")
                except Exception as e:
                    return render_template('error.html', error=f"Download failed: {str(e)}")

        except Exception as e:
            return render_template('error.html', error=f"An error occurred: {str(e)}")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
