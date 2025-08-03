"""
MP3Yap Version Information
"""

__version__ = "2.3.0"
__app_name__ = "YouTube MP3 İndirici"
__author__ = "Mehmet Yerli"
__github_repo__ = "mytsx/YtbMp3Indir"

def get_version():
    """Get the current version string"""
    return __version__

def get_app_info():
    """Get full application info"""
    return {
        "name": __app_name__,
        "version": __version__,
        "author": __author__,
        "repo": __github_repo__
    }