"""Icon Manager for MP3Yap application"""

import os
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, QFile, QTextStream
from PyQt5.QtSvg import QSvgRenderer


class IconManager:
    """Manages SVG icons for the application"""
    
    def __init__(self):
        self.icons_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'assets', 
            'icons'
        )
        self._cache = {}
    
    def get_icon(self, icon_name: str, color: str = None) -> QIcon:
        """Get an icon by name, optionally with a custom color"""
        cache_key = f"{icon_name}:{color or 'default'}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        icon_path = os.path.join(self.icons_dir, f"{icon_name}.svg")
        if not os.path.exists(icon_path):
            return QIcon()
        
        if color:
            # Load SVG and change color
            pixmap = self._load_svg_with_color(icon_path, color)
            icon = QIcon(pixmap)
        else:
            # Load SVG as-is
            icon = QIcon(icon_path)
        
        self._cache[cache_key] = icon
        return icon
    
    def has_icon(self, icon_name: str) -> bool:
        """Check if an icon exists"""
        icon_path = os.path.join(self.icons_dir, f"{icon_name}.svg")
        return os.path.exists(icon_path)
    
    def _load_svg_with_color(self, svg_path: str, color: str, size: int = 24) -> QPixmap:
        """Load SVG with a custom color"""
        # Read SVG content
        file = QFile(svg_path)
        if not file.open(QFile.ReadOnly | QFile.Text):
            return QPixmap()
        
        stream = QTextStream(file)
        svg_content = stream.readAll()
        file.close()
        
        # Replace currentColor with the specified color
        svg_content = svg_content.replace('currentColor', color)
        
        # Create QSvgRenderer from modified content
        renderer = QSvgRenderer()
        renderer.load(svg_content.encode('utf-8'))
        
        # Render to QPixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    def get_pixmap(self, icon_name: str, color: str = None, size: int = 24) -> QPixmap:
        """Get a pixmap by icon name"""
        icon_path = os.path.join(self.icons_dir, f"{icon_name}.svg")
        if not os.path.exists(icon_path):
            return QPixmap()
        
        if color:
            return self._load_svg_with_color(icon_path, color, size)
        else:
            pixmap = QPixmap(icon_path)
            if pixmap.width() != size or pixmap.height() != size:
                pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return pixmap


# Global icon manager instance
icon_manager = IconManager()