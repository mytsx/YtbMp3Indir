import os
import shutil
import yt_dlp
import static_ffmpeg
from PyQt5.QtCore import QObject, pyqtSignal
from database.manager import DatabaseManager


class DownloadSignals(QObject):
    """İndirme işlemleri için sinyal sınıfı"""
    progress = pyqtSignal(str, float, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str)
    status_update = pyqtSignal(str)


class Downloader:
    """YouTube video indirme ve MP3 dönüştürme sınıfı"""
    
    def __init__(self, signals):
        self.signals = signals
        self.is_running = False
        self.current_url = None
        self.db_manager = DatabaseManager()
        # Static FFmpeg'i yükle ve kullan
        try:
            static_ffmpeg.add_paths()
            self.ffmpeg_available = True
        except Exception as e:
            self.ffmpeg_available = self.check_system_ffmpeg()
            if not self.ffmpeg_available:
                self.signals.status_update.emit(f"FFmpeg yüklenemedi: {str(e)}")
    
    def check_system_ffmpeg(self):
        """Sistem FFmpeg'ini kontrol et"""
        return shutil.which('ffmpeg') is not None
    
    def postprocessor_hook(self, d):
        """Dönüştürme işlemi için hook"""
        if d['status'] == 'started':
            self.signals.status_update.emit(f"🔄 MP3'e dönüştürülüyor...")
        elif d['status'] == 'processing':
            self.signals.status_update.emit(f"🔄 Dönüştürme devam ediyor...")
        elif d['status'] == 'finished':
            self.signals.status_update.emit(f"✨ Dönüştürme tamamlandı!")
    
    def download_progress_hook(self, d):
        """İndirme ilerlemesini takip eden fonksiyon"""
        if d['status'] == 'downloading':
            filename = os.path.basename(d['filename'])
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                self.signals.progress.emit(filename, percent, f"%{percent:.1f}")
                self.signals.status_update.emit(f"📥 İndiriliyor: {filename} - %{percent:.1f}")
            else:
                mb_downloaded = d['downloaded_bytes']/1024/1024
                self.signals.progress.emit(filename, -1, f"{mb_downloaded:.1f} MB")
                self.signals.status_update.emit(f"📥 İndiriliyor: {filename} - {mb_downloaded:.1f} MB")
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            if filename.endswith('.webm') or filename.endswith('.m4a') or filename.endswith('.opus'):
                self.signals.status_update.emit(f"✅ İndirme tamamlandı, MP3'e dönüştürülüyor...")
            else:
                self.signals.finished.emit(filename)
        elif d['status'] == 'error':
            filename = os.path.basename(d.get('filename', 'Bilinmeyen dosya'))
            self.signals.error.emit(filename, str(d.get('error', 'Bilinmeyen hata')))

    def process_url(self, url, output_path):
        """URL'yi işler ve MP3 olarak indirir"""
        self.current_url = url
        self.signals.status_update.emit(f"🔗 Bağlantı kontrol ediliyor: {url}")
        
        # yt-dlp seçenekleri
        if self.ffmpeg_available:
            # FFmpeg varsa MP3'e dönüştür
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'postprocessor_hooks': [self.postprocessor_hook],
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'ignoreerrors': True,
                'noplaylist': False,
                'progress_hooks': [self.download_progress_hook],
                'prefer_ffmpeg': True,
            }
        else:
            # FFmpeg yoksa orijinal formatta indir
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'ignoreerrors': True,
                'noplaylist': False,
                'progress_hooks': [self.download_progress_hook],
            }
            self.signals.status_update.emit("Uyarı: FFmpeg bulunamadı. Dosyalar orijinal formatta indirilecek.")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    title = info.get('title', 'Unknown')
                    # Veritabanına kaydet
                    file_info = {
                        'title': title,
                        'file_name': f"{title}.mp3" if self.ffmpeg_available else f"{title}.{info.get('ext', 'webm')}",
                        'file_path': output_path,
                        'format': 'mp3' if self.ffmpeg_available else info.get('ext', 'webm'),
                        'url': url,
                        'file_size': info.get('filesize', 0),
                        'duration': info.get('duration', 0),
                        'channel': info.get('uploader', '')
                    }
                    self.db_manager.add_download(file_info)
                    
                    if not self.ffmpeg_available:
                        ext = info.get('ext', 'webm')
                        self.signals.status_update.emit(f"✅ İndirildi: {title}.{ext} (MP3 dönüşümü için FFmpeg gerekli)")
                    else:
                        self.signals.status_update.emit(f"✅ İşlem tamamlandı: {title}.mp3")
                        self.signals.finished.emit(f"{title}.mp3")
                else:
                    self.signals.status_update.emit(f"✅ İndirme tamamlandı")
            return True
        except yt_dlp.DownloadError as e:
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"İndirme hatası: {e}")
            return False
        except KeyboardInterrupt:
            self.signals.status_update.emit("İndirme kullanıcı tarafından durduruldu")
            return False
        except (OSError, IOError) as e:
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"Dosya sistem hatası: {e}")
            return False
        except Exception as e:  # pylint: disable=broad-except
            # Beklenmeyen hatalar için fallback
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"Beklenmeyen hata: {e}")
            return False

    def download_all(self, urls, output_path):
        """Tüm URL'leri indir"""
        self.is_running = True
        
        # Çıktı dizinini oluştur
        os.makedirs(output_path, exist_ok=True)
        
        for i, url in enumerate(urls, 1):
            if not self.is_running:
                self.signals.status_update.emit("İndirme durduruldu")
                break
                
            self.signals.status_update.emit(f"URL {i}/{len(urls)} işleniyor")
            success = self.process_url(url, output_path)
            
            if not success and not self.is_running:
                break
        
        self.is_running = False
        self.signals.status_update.emit("🎉 Tüm indirmeler tamamlandı!")

    def stop(self):
        """İndirmeyi durdur"""
        self.is_running = False