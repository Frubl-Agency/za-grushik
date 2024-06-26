import yt_dlp
from nicegui import ui, app
from pathlib import Path
import sys
import threading
import io
import re

# Redirect stdout to capture yt_dlp logs
class LogCapture(io.StringIO):
    def __init__(self, ui_log, progress_bar, current_song_label):
        super().__init__()
        self.ui_log = ui_log
        self.progress_bar = progress_bar
        self.current_song_label = current_song_label
        self.percentage_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%')
        self.song_number_pattern = re.compile(r'\[download\] Downloading item (\d+) of (\d+)')

    def write(self, message):
        super().write(message)
        self.ui_log.push(message)
        sys.__stdout__.write(message)
        
        match = self.percentage_pattern.search(message)
        if match:
            percentage = float(match.group(1)) / 100
            self.progress_bar.set_value(percentage)
        
        song_match = self.song_number_pattern.search(message)
        if song_match:
            current_song, total_songs = song_match.groups()
            self.current_song_label.set_text(f"{current_song} of {total_songs}")

    def flush(self):
        pass

def download_playlist(playlist_url, is_music, download_entire_playlist, progress_bar, current_song_label):
    common_opts = {
        'outtmpl': r'D:\Music\%(title)s.%(ext)s',
        'ignoreerrors': True,
        'retries': float('inf'),
        'embedthumbnail': True,
        'embedmetadata': True,
    }

    if is_music:
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': '0',
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '0'},
                {'key': 'FFmpegMetadata'}
            ],
            'yesplaylist': download_entire_playlist,
            'noplaylist': not download_entire_playlist,
        }
    else:
        ydl_opts = {
            **common_opts,
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{'key': 'FFmpegVideoConvertor'}],
            'noplaylist': True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])
    
    ui.notify('Download finished')  # Notify when the download is finished

def start_download():
    playlist_url = url_input.value
    is_music = format_select.value == 1
    download_entire_playlist = is_music and playlist_checkbox.value
    progress_bar.set_value(0)  # Reset progress bar to 0
    current_song_label.set_text('')  # Reset current song label
    ui.notify('Started downloading')

    threading.Thread(target=download_playlist, args=(playlist_url, is_music, download_entire_playlist, progress_bar, current_song_label)).start()

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
        with ui.row().classes('settings__item is-playlist') as is_playlist:
            playlist_checkbox = ui.checkbox('Download entire playlist').classes('checkbox')
        with ui.row().classes('settings__item'):
            ui.label('Format')
            format_select = ui.toggle({1: 'Music', 2: 'Video'}, value=1).classes('media-format')
        with ui.row().classes('settings__item'):
            ui.label('Select a folder for downloading')
            ui.label('D:/Music/').classes('path')

        def playlist_disable():
            if format_select.value == 2:
                is_playlist.classes('disable')
            else:
                is_playlist.classes(remove='disable')

        # Add the event listener for format_select value change
        format_select.on('update:model-value', playlist_disable)

    with ui.row().classes('progress-bar__wrapper'):
        current_song_label = ui.label().classes('current-song-label')
        progress_bar = ui.linear_progress(show_value=False).classes('progress-bar')

    log_area = ui.log().classes('log-area')
    log_area.visible = False

    # Define a function to toggle the visibility of log_area
    def toggle_log_area():
        log_area.visible = not log_area.visible

    sys.stdout = LogCapture(log_area, progress_bar, current_song_label)  # Redirect stdout to log_area and progress_bar
    
    with ui.row().classes('buttons'):
        ui.button('Start', on_click=start_download).classes('btn')
        ui.button('Advanced settings', icon='settings').classes('btn advanced-settings').on('click', toggle_log_area)

ui.run(native=True)
