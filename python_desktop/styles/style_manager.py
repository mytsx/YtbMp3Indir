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
        self._config = Config()
        self._current_theme = self._config.get('theme', 'light')
        
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
    
    def get_current_theme(self) -> str:
        """Get the cached current theme name."""
        return self._current_theme
    
    def set_theme(self, theme: str):
        """Set the current theme and update cache."""
        self._current_theme = theme
        self._config.set('theme', theme)
        self._config.save()
    
    def get_combined_stylesheet(self) -> str:
        """Get combined stylesheet for the application."""
        theme = self.get_current_theme()
        
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
    
    def apply_button_style(self, button: QPushButton, style_type: str = "primary", refresh: bool = False):
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
            if refresh:
                button.style().unpolish(button)
                button.style().polish(button)
    
    def apply_status_style(self, label: QLabel, status_type: str, refresh: bool = False):
        """Apply status styling to a label."""
        status_map = {
            "success": "statusSuccess",
            "warning": "statusWarning",
            "error": "statusError",
            "info": "statusInfo"
        }
        
        if status_type in status_map:
            label.setObjectName(status_map[status_type])
            if refresh:
                label.style().unpolish(label)
                label.style().polish(label)
    
    def apply_alert_style(self, label: QLabel, alert_type: str, refresh: bool = True):
        """Apply alert styling to a label (convenience method).
        
        This is a specialized method for alert messages that automatically refreshes styles.
        
        Args:
            label: The label widget to style
            alert_type: The type of alert ('success', 'warning', 'error', 'info')
            refresh: Whether to refresh the widget's style (default: True)
        """
        alert_map = {
            "success": "alertSuccess",
            "warning": "alertWarning", 
            "error": "alertError",
            "info": "alertInfo"
        }
        
        if alert_type in alert_map:
            label.setObjectName(alert_map[alert_type])
            if refresh:
                label.style().unpolish(label)
                label.style().polish(label)
    
    def set_widget_property(self, widget, property_name: str, property_value: str, refresh: bool = True):
        """Set a custom property on a widget and optionally refresh its style.
        
        This allows for dynamic styling without overwriting the objectName,
        preserving the base styles while adding additional styling based on properties.
        
        Args:
            widget: The widget to set the property on
            property_name: The name of the property
            property_value: The value of the property
            refresh: Whether to refresh the widget's style after setting the property
        """
        widget.setProperty(property_name, property_value)
        if refresh:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
    


# Global style manager instance
style_manager = StyleManager()