from flask import Flask, render_template, request, send_file
import yt_dlp
import tempfile
import os
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format = request.form['format']
        try:
            # Create a temporary directory to store the video file
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'noprogress': True,
                    'cachedir': False,
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),  # Use a template for the output file
                    'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'  # Add a User-Agent
                }
                
                if format == 'mp4':
                    ydl_opts['format'] = 'best[ext=mp4]'  # Select the best mp4 format
                elif format == 'mp3':
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    
                    # Get title from info_dict
                    title = info_dict.get('title', 'video')
                    
                    # Download the video to the temporary directory
                    ydl.download([url])
                    
                    # Find the downloaded file in the temporary directory
                    filename = ydl.prepare_filename(info_dict)
                    if format == 'mp3':
                        filename = os.path.splitext(filename)[0] + '.mp3'
                    
                    with open(filename, 'rb') as f:
                        video_data = f.read()
                    
                    # Create a BytesIO buffer from the video data
                    buffer = io.BytesIO(video_data)
                    
                    # Reset buffer position to the start
                    buffer.seek(0)
                    
                    if format == 'mp4':
                        return send_file(buffer, as_attachment=True, download_name=f"{title}.mp4", mimetype='video/mp4')
                    elif format == 'mp3':
                        return send_file(buffer, as_attachment=True, download_name=f"{title}.mp3", mimetype='audio/mpeg')

        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
