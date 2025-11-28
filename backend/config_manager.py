"""
Config Manager
Handles loading and saving application configuration to JSON file
"""
import json
import os
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "output_dir": str(Path.home() / "Music"),
    "quality": "192",
    "auto_open": True,
    "language": "tr",
    "history_retention_days": 0,  # 0 = keep forever
}

# Config file path (next to the database)
CONFIG_FILE = "config.json"


class ConfigManager:
    """Manages application configuration persistence"""

    def __init__(self, config_path: str = CONFIG_FILE):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from JSON file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # Merge with defaults (in case new fields were added)
                    self._config = {**DEFAULT_CONFIG, **saved_config}
                    logger.info(f"Configuration loaded from {self.config_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
                self._config = DEFAULT_CONFIG.copy()
        else:
            logger.info("No config file found. Using defaults.")
            self._config = DEFAULT_CONFIG.copy()
            # Save defaults to create the file
            self._save()

    def _save(self) -> None:
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except IOError as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save"""
        self._config[key] = value
        self._save()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values and save"""
        self._config.update(updates)
        self._save()

    def reset(self) -> None:
        """Reset to default configuration"""
        self._config = DEFAULT_CONFIG.copy()
        self._save()


# Global config manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get or create global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
