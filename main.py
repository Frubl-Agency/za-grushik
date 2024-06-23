import yt_dlp
from nicegui import ui, app
from pathlib import Path

def download_playlist(playlist_url, is_playlist, quality, format):
    ydl_opts = {
        'format': 'bestaudio/best' if format == 'mp3' else format,
        'extractaudio': True if format == 'mp3' else False,  # only keep the audio if mp3
        'audioformat': format,  # convert to specified format
        'audioquality': str(quality),  # specified audio quality
        'outtmpl': r'D:\Music\%(title)s.%(ext)s',  # name the downloaded file
        'yesplaylist': is_playlist,  # download entire playlist
        'ignoreerrors': True,  # continue on download errors
        'retries': float('inf'),  # retry infinitely on error
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': str(quality),
        }] if format == 'mp3' else [],
        'embedthumbnail': True,  # embed thumbnail
        'embedmetadata': True,  # embed metadata
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def start_download():
    playlist_url = url_input.value
    is_playlist = playlist_checkbox.value
    quality = int(quality_slider.value)
    format = format_select.value
    download_playlist(playlist_url, is_playlist, quality, format)
    ui.notify(f'Started downloading from URL: {playlist_url} with format: {format} and quality: {quality}')

# Serve static files
app.add_static_files('/static', str(Path(__file__).parent / "static"))

# Add custom styles
ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/reset.css">')
ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

# Create a NiceGUI app with custom styling
with ui.column().classes('main') as main:
    ui.colors(primary='#fff')

    # ui.html('<input type="text" id="url-input" placeholder="Enter link" class="link">')
    url_input = ui.input(label='Enter link', placeholder='Enter link').classes('link')

    with ui.column().classes('settings') as settings:
        with ui.row().classes('settings__item'):
            playlist_checkbox = ui.checkbox('Download entire playlist').classes('checkbox')
        with ui.row().classes('settings__item'):
            ui.label('Audio/Video Quality')
            quality_slider = ui.slider(min=0, max=100, step=10, value=80).classes('range')
            ui.label().bind_text_from(quality_slider, 'value').classes('range-slider__value')
        with ui.row().classes('settings__item'):
            ui.label('Format')
            ui.html('''
            <select id="media-format" name="media-format" class="media-format">
                <option value="mp3" selected>mp3</option>
                <option value="webm">webm</option>
                <option value="mp4">mp4</option>
            </select>
            ''')

    ui.button('Start', on_click=start_download).classes('btn')

ui.run()
