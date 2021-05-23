import validators
import youtube_dl


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

    def get_video_info(self, search_url, download=False):
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
                # multiple videos from search sting, take first
                found_videos = [result['entries'][0]]
            else:
                found_videos = [result]

            for video in found_videos:
                video_info = {}
                try:
                    video_info['source_url'] = video['formats'][0]['url']
                    video_info['title'] = video['title']
                    video_info['webpage_url'] = video['webpage_url']
                    video_info['duration'] = video['duration']
                    video_info['thumbnail'] = video['thumbnail']
                    videos.append(video_info)
                except Exception as e:
                    pass

        return videos
