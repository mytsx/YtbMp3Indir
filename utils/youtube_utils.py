import re
from typing import Optional, Tuple

def extract_video_id(url: str) -> Optional[str]:
    """YouTube URL'sinden video ID'sini çıkarır"""
    # YouTube URL regex pattern
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'm\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def extract_playlist_id(url: str) -> Optional[str]:
    """YouTube URL'sinden playlist ID'sini çıkarır"""
    # Playlist ID pattern
    match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None

def extract_ids(url: str) -> Tuple[Optional[str], Optional[str]]:
    """URL'den hem video ID hem playlist ID çıkarır"""
    video_id = extract_video_id(url)
    playlist_id = extract_playlist_id(url)
    return video_id, playlist_id

def normalize_youtube_url(url: str) -> Optional[str]:
    """YouTube URL'sini normalize eder (video ID bazlı)"""
    video_id = extract_video_id(url)
    if video_id:
        return f"https://youtube.com/watch?v={video_id}"
    return None