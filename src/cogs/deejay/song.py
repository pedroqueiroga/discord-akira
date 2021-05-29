from typing import Set

from .exceptions import RequesterIdAlreadySet


class Song:
    _source_url: str
    _title: str
    _webpage_url: str
    _duration: int
    _thumbnail: str
    _requester_id: int
    _pula_votes: Set[int] = set()

    def __init__(
        self,
        source_url,
        title,
        webpage_url,
        duration,
        thumbnail,
        requester_id=None,
    ):
        self._source_url = source_url
        self._title = title
        self._webpage_url = webpage_url
        self._duration = duration
        self._thumbnail = thumbnail
        self._requester_id = requester_id

    @property
    def source_url(self):
        return self._source_url

    @property
    def title(self):
        return self._title

    @property
    def webpage_url(self):
        return self._webpage_url

    @property
    def duration(self):
        return self._duration

    @property
    def thumbnail(self):
        return self._thumbnail

    @property
    def requester_id(self):
        return self._requester_id

    @requester_id.setter
    def requester_id(self, req_id):
        if self._requester_id is None:
            self._requester_id = req_id
        else:
            raise RequesterIdAlreadySet()

    @property
    def pula_votes(self):
        return self._pula_votes
