import yt_dlp
from nicegui import ui, app
from pathlib import Path

def download_playlist(playlist_url, is_playlist, quality, format):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # download best video+audio format
        'outtmpl': r'D:\Music\%(title)s.%(ext)s',  # name the downloaded file
        'ignoreerrors': True,  # continue on download errors
        'retries': float('inf'),  # retry infinitely on error
        'postprocessors': [{
            'key': 'FFmpegMetadata',
        }],
        'embedthumbnail': True,  # embed thumbnail if possible
        'embedmetadata': True,  # embed metadata if possible
        'yesplaylist': is_playlist  # download entire playlist if is_playlist is True
    }

    if format == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'extractaudio': True,  # only keep the audio
            'audioformat': format,  # convert to the chosen format
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '0',
            }, {
                'key': 'FFmpegMetadata',
            }],
        })

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
                quality_slider = ui.slider(min=0, max=100, step=10, value=80).classes('range')
                ui.label().bind_text_from(quality_slider, 'value').classes('range-slider__value')
        with ui.row().classes('settings__item'):
            ui.label('Format')
            format_select = ui.select(['mp3', 'webm', 'mp4'], value='mp3').classes('media-format')

    ui.button('Start', on_click=start_download).classes('btn')

ui.run(native=True)
