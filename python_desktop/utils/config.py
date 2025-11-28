import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """Uygulama ayarları yöneticisi"""
    
    DEFAULT_CONFIG = {
        'output_path': 'music',
        'audio_quality': '192',
        'audio_format': 'mp3',
        'theme': 'light',
        'notification_sound': True,
        'language': 'tr',
        'max_simultaneous_downloads': 3,
        'auto_open_folder': False,
        'save_history': True,
        'history_days': 0,  # 0 = süresiz
        'playlist_limit': 0,  # 0 = limitsiz
        'auto_retry': True
    }
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Ayarları dosyadan yükle"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Varsayılan değerlerle birleştir
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Config file corrupted or invalid encoding: {e}")
                return self.DEFAULT_CONFIG.copy()
            except (IOError, OSError) as e:
                logger.error(f"Failed to read config file: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Ayarları dosyaya kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save config file: {e}")
        except TypeError as e:
            logger.error(f"Invalid config data type for JSON serialization: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Bir ayar değerini getir"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Bir ayar değerini güncelle"""
        self.config[key] = value
        self.save_config()
    
    def reset_to_defaults(self):
        """Ayarları varsayılana döndür"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get config as dictionary"""
        return self.config.copy()