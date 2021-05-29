from typing import List

import validators
import youtube_dl

from .song import Song


class Youtuber:
    """Classe que encapsula youtube_dl"""

    def __init__(self, quiet=True):
        self.ydl_opts = {
            'quiet': quiet,
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
            'youtube_include_dash_manifest': False,
            'ignoreerrors': False,
        }

    def get_video_info(self, search_url: str, download=False) -> List[Song]:
        """Information for video(s) from a URL or search string.

        :param str search_url: A search string or URL for youtube.
        :param bool download: If the video should be downloaded.
        :returns: information on the video found.
        :rtype: dict
        """

        videos = []
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            result = ydl.extract_info(search_url, download=False)
            found_videos = []
            if validators.url(search_url) and 'entries' in result.keys():
                found_videos = result['entries']
            elif 'entries' in result.keys():
                # multiple videos from search string, take first
                found_videos = [result['entries'][0]]
            else:
                found_videos = [result]

            for video in found_videos:
                try:
                    song = Song(
                        video['formats'][0]['url'],
                        video['title'],
                        video['webpage_url'],
                        video['duration'],
                        video['thumbnail'],
                    )
                    videos.append(song)
                except Exception as e:
                    pass

        return videos
