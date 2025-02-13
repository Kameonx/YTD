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
        try:
            # Create a temporary directory to store the video file
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {
                    'format': 'best[ext=mp4]',  # Select the best mp4 format
                    'quiet': True,
                    'no_warnings': True,
                    'noprogress': True,
                    'cachedir': False,
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s')  # Use a template for the output file
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    
                    # Get title from info_dict
                    title = info_dict.get('title', 'video')
                    
                    # Download the video to the temporary directory
                    ydl.download([url])
                    
                    # Find the downloaded file in the temporary directory
                    filename = ydl.prepare_filename(info_dict)
                    with open(filename, 'rb') as f:
                        video_data = f.read()
                    
                    # Create a BytesIO buffer from the video data
                    buffer = io.BytesIO(video_data)
                    
                    # Reset buffer position to the start
                    buffer.seek(0)
                    
                    return send_file(buffer, as_attachment=True, download_name=f"{title}.mp4", mimetype='video/mp4')

        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
