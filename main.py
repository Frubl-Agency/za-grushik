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

def download_playlist(playlist_url, is_music):
    if is_music:
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
    else:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': r'D:\Music\%(title)s.%(ext)s',  # name the downloaded file
            'ignoreerrors': True,  # continue on download errors
            'retries': float('inf'),  # retry infinitely on error
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
            }],
            'embedthumbnail': True,  # embed thumbnail in mp4
            'embedmetadata': True,  # embed metadata in mp4
        }

    print(f"Downloading playlist from URL: {playlist_url} with options: {ydl_opts}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def start_download():
    playlist_url = url_input.value
    is_music = format_select.value == 1
    ui.notify(f'Started downloading')

    # Start download in a separate thread to avoid blocking the UI
    download_thread = threading.Thread(target=download_playlist, args=(playlist_url, is_music))
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
        with ui.row().classes('settings__item'):
            ui.label('Format')
            format_select = ui.toggle({1: 'Music', 2: 'Video'}, value=1).classes('media-format')
        with ui.row().classes('settings__item'):
            ui.label('Select a folder for downloading')
            ui.label('D:/Music/').classes('path')

    log_area = ui.log().classes('log-area')
    sys.stdout = LogCapture(log_area)  # Redirect stdout to log_area

    ui.button('Start', on_click=start_download).classes('btn')

ui.run(native=True)
