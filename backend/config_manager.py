"""
Config Manager
Handles loading and saving application configuration to JSON file
Thread-safe implementation with atomic writes and proper error handling
"""
import json
import os
import logging
import threading
import tempfile
import shutil
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

# Config file path anchored to this file's directory (backend/)
CONFIG_FILE = Path(__file__).parent / "config.json"


class ConfigManager:
    """Manages application configuration persistence (thread-safe)"""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Load configuration from JSON file (thread-safe)"""
        with self._lock:
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
                self._save_atomic(self._config)

    def _save_atomic(self, config: Dict[str, Any]) -> None:
        """
        Save configuration atomically using temp file + rename.
        This ensures the config file is never left in a corrupted state.
        Raises IOError on failure.
        """
        config_dir = self.config_path.parent
        tmp_path = None
        try:
            # Write to temp file in same directory (for atomic rename)
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=config_dir,
                suffix='.tmp',
                delete=False
            ) as tmp_file:
                json.dump(config, tmp_file, indent=2, ensure_ascii=False)
                tmp_path = tmp_file.name

            # Atomic rename (works on POSIX, best-effort on Windows)
            shutil.move(tmp_path, self.config_path)
            logger.info(f"Configuration saved to {self.config_path}")
        except (IOError, OSError) as e:
            # Clean up temp file if it exists
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            logger.error(f"Failed to save config: {e}")
            raise IOError(f"Failed to save configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        with self._lock:
            return self._config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        with self._lock:
            return self._config.copy()

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save.
        Only updates in-memory config after successful persist.
        Raises IOError on failure.
        """
        with self._lock:
            # Create new config with update
            new_config = self._config.copy()
            new_config[key] = value
            # Persist first (raises on failure)
            self._save_atomic(new_config)
            # Only update in-memory after successful persist
            self._config = new_config

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values and save.
        Only updates in-memory config after successful persist.
        Raises IOError on failure.
        """
        with self._lock:
            # Create new config with updates
            new_config = {**self._config, **updates}
            # Persist first (raises on failure)
            self._save_atomic(new_config)
            # Only update in-memory after successful persist
            self._config = new_config

    def reset(self) -> None:
        """
        Reset to default configuration.
        Only updates in-memory config after successful persist.
        Raises IOError on failure.
        """
        with self._lock:
            new_config = DEFAULT_CONFIG.copy()
            # Persist first (raises on failure)
            self._save_atomic(new_config)
            # Only update in-memory after successful persist
            self._config = new_config


# Global config manager instance with thread-safe initialization
_config_manager = None
_config_manager_lock = threading.Lock()


def get_config_manager() -> ConfigManager:
    """Get or create global config manager instance (thread-safe)"""
    global _config_manager
    if _config_manager is None:
        with _config_manager_lock:
            # Double-checked locking pattern
            if _config_manager is None:
                _config_manager = ConfigManager()
    return _config_manager
