"""Update checker for MP3Yap"""

import platform
import logging
import requests
from packaging import version
from PyQt5.QtCore import QThread, pyqtSignal
from version import __version__, __github_repo__


class UpdateChecker(QThread):
    """Check for updates in background"""
    
    update_available = pyqtSignal(dict)  # Emits update info
    check_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self):
        super().__init__()
        self.current_version = __version__
        self.api_url = f"https://api.github.com/repos/{__github_repo__}/releases/latest"
    
    def run(self):
        """Check for updates"""
        try:
            headers = {'User-Agent': f'{__github_repo__.split("/")[1]}/{__version__}'}
            response = requests.get(self.api_url, timeout=5, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data.get('tag_name', '').lstrip('v')
            
            if latest_version and self.is_newer_version(latest_version):
                update_info = {
                    'version': latest_version,
                    'url': data.get('html_url', ''),
                    'body': data.get('body', ''),
                    'download_url': self.get_download_url(data),
                    'published_at': data.get('published_at', '')
                }
                self.update_available.emit(update_info)
                self.check_finished.emit(True, f"Yeni sürüm mevcut: v{latest_version}")
            else:
                self.check_finished.emit(True, "Güncel sürümü kullanıyorsunuz")
        except requests.exceptions.JSONDecodeError as e:
            self.check_finished.emit(False, f"Hata: API yanıtı okunamadı: {e}")
        except requests.exceptions.RequestException as e:
            self.check_finished.emit(False, f"Güncelleme kontrolü başarısız: {e}")
        except Exception as e:
            logging.exception("Unexpected error during update check")
            self.check_finished.emit(False, "Hata: Beklenmedik bir hata oluştu.")
    
    def is_newer_version(self, latest_version):
        """Check if latest version is newer than current"""
        try:
            return version.parse(latest_version) > version.parse(self.current_version)
        except version.InvalidVersion:
            return False
    
    def get_download_url(self, release_data):
        """Get the appropriate download URL for the platform"""
        assets = release_data.get('assets', [])
        system = platform.system().lower()
        
        platform_map = {
            'windows': ('.exe', '.msi'),
            'darwin': ('.dmg', '.pkg'),
            'linux': ('.appimage', '.deb')
        }
        
        extensions = platform_map.get(system, ())  # Get extensions for the current system
        
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith(extensions):
                return asset.get('browser_download_url', '')
        
        # Fallback to release page
        return release_data.get('html_url', '')
