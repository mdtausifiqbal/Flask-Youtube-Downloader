import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request, session
from pytube import YouTube

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route('/')
def index():
    videoUrl = request.args.get('url')

    if (videoUrl == None):
        return render_template('index.html', context=None)
    
    session['url'] = videoUrl
    
    yt = YouTube(videoUrl)
    videos = yt.streams.filter(progressive=True).order_by('resolution').desc()
    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
        "length": str(timedelta(seconds=yt.length)),
        "streams": videos,
        "url": videoUrl

    }
    return render_template('index.html', context=context)

@app.route('/download/<itag>')
def download(itag):
    videoUrl = session['url']
    yt = YouTube(videoUrl)
    video = yt.streams.get_by_itag(itag)
    file_url = video.url
    filename = video.default_filename

     # Set the Content-Disposition header to suggest the filename
    headers = {'Content-Disposition': f'attachment; filename={filename}'}

    # Fetch the file content using requests with streaming
    response = requests.get(file_url, headers=headers, stream=True)

     # Check if the server provided Content-Length
    content_length = response.headers.get('Content-Length')
    if content_length:
        headers['Content-Length'] = content_length

    # Stream the file content back to the client
    return Response(response.iter_content(chunk_size=1024), headers=headers, content_type=response.headers['content-type'])

if __name__ == '__main__':
    app.run(debug=True)