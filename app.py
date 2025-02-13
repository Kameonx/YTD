from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]',  # Select the best mp4 format
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'cachedir': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                
                # Get title from info_dict
                title = info_dict.get('title', 'video')
                
                # Download video using yt_dlp directly without extracting info again
                filename = f"{title}.mp4"
                
                # Use outtmpl option in ydl_opts to specify output filename template
                new_ydl_opts = {
                    **ydl_opts,
                    'outtmpl': f'{filename}'
                }
                
                with yt_dlp.YoutubeDL(new_ydl_opts) as new_ydl:
                    new_ydl.download([url])
                    
                    return send_file(filename, as_attachment=True)

        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)