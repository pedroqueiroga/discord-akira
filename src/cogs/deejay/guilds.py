from typing import Dict

from .guild import Guild


class Guilds(Dict[int, Guild]):
    """Guilds is a dictionary from guild ids (int) to Guild objects
    If a user attempts to access a missing guild id it will create
    a new entry and return it, so he can use it seamlessly.
    It doesn't allow resetting properties."""

    def __setitem__(self, key: int, value: Guild) -> None:
        if key in self:
            raise KeyError('Chave já está presente.', key)

        super().__setitem__(key, value)

    def __missing__(self, key: int) -> Guild:
        self[key] = Guild()
        return self[key]
