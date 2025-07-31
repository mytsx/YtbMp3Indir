"""
FFmpeg Helper - Embedded FFmpeg kullanımı için yardımcı modül
"""
import os
import sys
import platform


def setup_ffmpeg():
    """FFmpeg'i embedded olarak ayarla"""
    try:
        # PyInstaller ile paketlenmiş mi kontrol et
        if getattr(sys, 'frozen', False):
            # Uygulama dizinini bul
            if sys.platform == 'darwin':
                # macOS için .app bundle içindeki path
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(sys.executable)
            
            # FFmpeg binary'lerinin yolu
            if sys.platform == 'darwin':
                ffmpeg_dir = os.path.join(base_path, 'static_ffmpeg', 'bin', 'darwin')
            elif sys.platform == 'win32':
                ffmpeg_dir = os.path.join(base_path, 'static_ffmpeg', 'bin', 'win32')
            else:
                ffmpeg_dir = os.path.join(base_path, 'static_ffmpeg', 'bin', 'linux')
            
            # PATH'e ekle
            if os.path.exists(ffmpeg_dir):
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                print(f"FFmpeg embedded from: {ffmpeg_dir}")
                return True
        
        # Development modda 
        if sys.platform == 'darwin':
            # macOS'ta development modda embedded FFmpeg kullan
            ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'assets', 'ffmpeg', 'darwin')
            if os.path.exists(ffmpeg_dir):
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                print(f"FFmpeg dev mode from: {ffmpeg_dir}")
                return True
        
        # Diğer sistemlerde normal static_ffmpeg kullan
        import static_ffmpeg
        static_ffmpeg.add_paths()
        return True
        
    except Exception as e:
        print(f"FFmpeg setup warning: {e}")
        return False