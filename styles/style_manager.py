"""Style manager for MP3Yap application."""

import os
from typing import Dict
from PyQt5.QtWidgets import QPushButton, QLabel
from PyQt5.QtCore import QFile, QTextStream
from .colors import Colors
from utils.config import Config


class StyleManager:
    """Manages application styles and themes."""
    
    def __init__(self):
        self.styles_dir = os.path.dirname(os.path.abspath(__file__))
        self._cache: Dict[str, str] = {}
        self.colors = Colors()
        
    def load_stylesheet(self, filename: str) -> str:
        """Load a QSS stylesheet from file."""
        if filename in self._cache:
            return self._cache[filename]
            
        filepath = os.path.join(self.styles_dir, filename)
        if not os.path.exists(filepath):
            return ""
            
        file = QFile(filepath)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            content = stream.readAll()
            file.close()
            self._cache[filename] = content
            return content
        return ""
    
    def get_combined_stylesheet(self) -> str:
        """Get combined stylesheet for the application."""
        config = Config()
        theme = config.get('theme', 'light')
        
        if theme == 'dark':
            return self.load_stylesheet("modern.qss")
        else:
            # Light theme - use base styles
            stylesheets = [
                self.load_stylesheet("base.qss"),
                self.load_stylesheet("buttons.qss"),
                self.load_stylesheet("status.qss")
            ]
            return "\n".join(stylesheets)
    
    def apply_button_style(self, button: QPushButton, style_type: str = "primary"):
        """Apply a specific style to a button."""
        style_map = {
            "primary": "primaryButton",
            "secondary": "secondaryButton",
            "danger": "dangerButton",
            "warning": "warningButton",
            "accent": "accentButton",
            "ghost": "ghostButton",
            "icon": "iconButton",
            "download": "downloadButton"
        }
        
        if style_type in style_map:
            button.setObjectName(style_map[style_type])
    
    def apply_status_style(self, label: QLabel, status_type: str):
        """Apply status styling to a label."""
        status_map = {
            "success": "statusSuccess",
            "warning": "statusWarning",
            "error": "statusError",
            "info": "statusInfo"
        }
        
        if status_type in status_map:
            label.setObjectName(status_map[status_type])
    
    
    def get_status_message_style(self, message_type: str) -> str:
        """Get style for status bar messages."""
        styles = {
            "success": f"""
                background-color: {self.colors.SUCCESS_LIGHT};
                color: {self.colors.SUCCESS_TEXT};
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid {self.colors.SUCCESS};
            """,
            "warning": f"""
                background-color: {self.colors.WARNING_LIGHT};
                color: {self.colors.WARNING_TEXT};
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid {self.colors.WARNING};
            """,
            "error": f"""
                background-color: {self.colors.ERROR_LIGHT};
                color: {self.colors.ERROR_TEXT};
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid {self.colors.ERROR};
            """,
            "info": f"""
                background-color: {self.colors.INFO_LIGHT};
                color: {self.colors.INFO_TEXT};
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid {self.colors.INFO};
            """
        }
        return styles.get(message_type, styles["info"])
    


# Global style manager instance
style_manager = StyleManager()