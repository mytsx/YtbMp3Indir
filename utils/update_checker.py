"""Update checker for MP3Yap"""

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
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
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
            else:
                self.check_finished.emit(False, "Güncelleme kontrolü başarısız")
        except requests.exceptions.RequestException as e:
            self.check_finished.emit(False, f"Bağlantı hatası: {str(e)}")
        except Exception as e:
            self.check_finished.emit(False, f"Hata: {str(e)}")
    
    def is_newer_version(self, latest_version):
        """Check if latest version is newer than current"""
        try:
            return version.parse(latest_version) > version.parse(self.current_version)
        except version.InvalidVersion:
            return False
    
    def get_download_url(self, release_data):
        """Get the appropriate download URL for the platform"""
        import platform
        
        assets = release_data.get('assets', [])
        system = platform.system().lower()
        
        # Find appropriate asset based on platform
        for asset in assets:
            name = asset.get('name', '').lower()
            if system == 'windows' and ('.exe' in name or '.msi' in name):
                return asset.get('browser_download_url', '')
            elif system == 'darwin' and ('.dmg' in name or '.pkg' in name):
                return asset.get('browser_download_url', '')
            elif system == 'linux' and ('.appimage' in name or '.deb' in name):
                return asset.get('browser_download_url', '')
        
        # Fallback to release page
        return release_data.get('html_url', '')