import os
import glob
import sys
import urllib.request
import imageio_ffmpeg
import yt_dlp
from .signals import DownloadSignals

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def get_node_path() -> str | None:
    """Resolves node.exe path for both source runs and PyInstaller builds."""
    # PyInstaller unpack directory check
    if hasattr(sys, '_MEIPASS'):
        bundle_path = os.path.join(sys._MEIPASS, 'core', 'bin', 'node.exe')
        if os.path.exists(bundle_path):
            return bundle_path

    # Local development path (relative to this file)
    local_path = os.path.join(os.path.dirname(__file__), 'bin', 'node.exe')
    if os.path.exists(local_path):
        return local_path

    return None


NODE_EXE = get_node_path()


class QtYtdlLogger:
    def __init__(self, signals: DownloadSignals):
        self.signals = signals

    def debug(self, msg: str):
        if not msg.startswith('[download]'):
            self.signals.log.emit(f"[DEBUG] {msg}")

    def info(self, msg: str):
        self.signals.log.emit(f"[INFO] {msg}")

    def warning(self, msg: str):
        self.signals.log.emit(f"[WARNING] {msg}")

    def error(self, msg: str):
        self.signals.log.emit(f"[ERROR] {msg}")


class VideoDownloadService:
    def __init__(self, signals: DownloadSignals):
        self.signals = signals

    def fetch_preview(self, url: str):
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'socket_timeout': 10,
        }
        if NODE_EXE:
            ydl_opts['js_runtimes'] = {'node': {'path': NODE_EXE}}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                thumbnail_url = info.get('thumbnail')
                image_data = None
                if thumbnail_url:
                    try:
                        req = urllib.request.Request(thumbnail_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            image_data = response.read()
                    except Exception:
                        image_data = None

                duration = info.get('duration', 0)
                dur_str = f"{duration // 60:02d}:{duration % 60:02d}" if duration else "N/A"

                metadata = {
                    'title': info.get('title', 'Unknown Title'),
                    'uploader': info.get('uploader', 'Unknown Creator'),
                    'duration': dur_str,
                    'image_data': image_data
                }
                self.signals.preview_loaded.emit(metadata)
        except Exception as e:
            self.signals.preview_failed.emit(str(e))

    def _progress_hook(self, d: dict):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)

            speed = d.get('speed')
            speed_str = f"{speed / (1024 * 1024):.1f} MB/s" if speed else "N/A"

            eta = d.get('eta')
            if eta is not None:
                try:
                    eta_sec = int(eta)
                    eta_str = f"{eta_sec // 60:02d}:{eta_sec % 60:02d}"
                except (ValueError, TypeError):
                    eta_str = "N/A"
            else:
                eta_str = "N/A"

            if total_bytes > 0:
                percent = (downloaded / total_bytes) * 100
                status_text = f"Downloading: {percent:.1f}% ({speed_str} | ETA: {eta_str})"
                self.signals.progress.emit(percent, status_text)
            else:
                self.signals.progress.emit(0, f"Downloading: {downloaded / (1024 * 1024):.1f} MB ({speed_str})")

        elif d['status'] == 'finished':
            self.signals.progress.emit(100.0, "Processing and converting media with FFmpeg...")

    def _cleanup_partial_files(self, folder: str, initial_snapshot: set):
        try:
            current_files = set(os.listdir(folder))
            new_files = current_files - initial_snapshot

            for fname in new_files:
                file_path = os.path.join(folder, fname)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

            for stray in glob.glob(os.path.join(folder, "*.part*")) + glob.glob(os.path.join(folder, "*.ytdl")):
                try:
                    os.remove(stray)
                except OSError:
                    pass
        except Exception:
            pass

    def download(self, url: str, destination_dir: str, audio_only: bool = False):
        os.makedirs(destination_dir, exist_ok=True)
        try:
            snapshot = set(os.listdir(destination_dir))
        except OSError:
            snapshot = set()

        ydl_opts = {
            'noplaylist': True,
            'socket_timeout': 15,
            'ffmpeg_location': FFMPEG_EXE,
            'outtmpl': os.path.join(destination_dir, '%(title)s.%(ext)s'),
            'nopart': False,
            'progress_hooks': [self._progress_hook],
            'logger': QtYtdlLogger(self.signals),
        }

        # Only register js_runtimes if the binary actually exists
        if NODE_EXE:
            ydl_opts['js_runtimes'] = {'node': {'path': NODE_EXE}}

        if audio_only:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status = ydl.download([url])
                if status != 0:
                    raise RuntimeError(f"yt-dlp failed with return code {status}")
            self.signals.finished.emit(True, "Download complete!")
        except Exception as e:
            self._cleanup_partial_files(destination_dir, snapshot)
            self.signals.finished.emit(False, f"Download failed: {e}")