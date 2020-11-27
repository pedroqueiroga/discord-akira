import youtube_dl


class Youtuber:
    """Classe que encapsula youtube_dl"""

    def __init__(self, quiet=True):
        self.ydl_opts = {
            'quiet': quiet,
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
            'youtube_include_dash_manifest': False,
        }

    def get_video_info(self, search_url, download=False):
        """Information for a video from a URL or search string.

        :param str search_url: A search string or URL for youtube.
        :param bool download: If the video should be downloaded.
        :returns: information on the video found.
        :rtype: dict
        """

        video_info = {}
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            video = ydl.extract_info(search_url, download=False)

            if 'entries' in video.keys():
                # multiple videos, take first
                video = video['entries'][0]

            video_info['source_url'] = video['formats'][0]['url']
            video_info['title'] = video['title']
            video_info['webpage_url'] = video['webpage_url']
            video_info['duration'] = video['duration']
            video_info['thumbnail'] = video['thumbnail']

        return video_info
