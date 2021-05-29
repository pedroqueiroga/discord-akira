from typing import List

from .song import Song


class Guild:
    """Guild class that Deejay Akira uses to keep track of what is
    going on at each guild she is invited to play on."""

    _setlist: List[Song] = []
    _current_song: Song
    _stopped_playing_timestamp: float
    _loudness: float

    def __init__(self, loudness: float = 1):
        self._loudness = loudness

    @property
    def setlist(self):
        return self._setlist

    @property
    def current_song(self):
        return self._current_song

    @current_song.setter
    def current_song(self, current_song: Song):
        self._current_song = current_song

    @property
    def stopped_playing_timestamp(self):
        return self._stopped_playing_timestamp

    @stopped_playing_timestamp.setter
    def stopped_playing_timestamp(self, timestamp: float):
        self._stopped_playing_timestamp = timestamp

    @property
    def loudness(self):
        return self._loudness

    @loudness.setter
    def loudness(self, loudness: float):
        self._loudness = loudness
