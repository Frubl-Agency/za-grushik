import yt_dlp
from nicegui import ui, app
from pathlib import Path
import sys
import threading
import io

# Redirect stdout to capture yt_dlp logs
class LogCapture(io.StringIO):
    def __init__(self, ui_log):
        super().__init__()
        self.ui_log = ui_log

    def write(self, message):
        super().write(message)
        self.ui_log.push(message)
        sys.__stdout__.write(message)

    def flush(self):
        pass

def download_playlist(playlist_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,  # only keep the audio
        'audioformat': 'mp3',  # convert to mp3
        'audioquality': '0',  # best audio quality
        'outtmpl': r'D:\Music\%(title)s.%(ext)s',  # name the downloaded file
        'yesplaylist': True,  # download entire playlist
        'ignoreerrors': True,  # continue on download errors
        'retries': float('inf'),  # retry infinitely on error
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }, {
            'key': 'FFmpegMetadata',
        }],
        'embedthumbnail': True,  # embed thumbnail in mp3
        'embedmetadata': True,  # embed metadata in mp3
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def start_download():
    playlist_url = url_input.value
    ui.notify(f'Started downloading')

    # Start download in a separate thread to avoid blocking the UI
    download_thread = threading.Thread(target=download_playlist, args=(playlist_url,))
    download_thread.start()

# Serve static files
app.add_static_files('/static', str(Path(__file__).parent / "static"))

# Add custom styles
ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/css/reset.css">')
ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/css/styles.css">')

# Create a NiceGUI app with custom styling
with ui.column().classes('main__inner'):
    ui.colors(primary='#7773FE')

    url_input = ui.input(placeholder='Enter link').classes('link')

    with ui.column().classes('settings') as settings:
        with ui.row().classes('settings__item is-playlist'):
            playlist_checkbox = ui.checkbox('Download entire playlist').classes('checkbox')
        with ui.row().classes('settings__item quality'):
            ui.label('Audio/Video Quality')
            with ui.row().classes('range__wrapper'):
                quality_slider = ui.slider(min=0, max=100, step=10, value=100).classes('range')
                ui.label().bind_text_from(quality_slider, 'value').classes('range-slider__value')
        with ui.row().classes('settings__item'):
            ui.label('Format')
            format_select = ui.select(['mp3', 'webm', 'mp4'], value='mp3').classes('media-format')
        with ui.row().classes('settings__item'):
            ui.label('Select a folder for downloading')
            ui.label('D:/Music/').classes('path')

    log_area = ui.log().classes('log-area')
    sys.stdout = LogCapture(log_area)  # Redirect stdout to log_area

    ui.button('Start', on_click=start_download).classes('btn')

ui.run(native=True)
