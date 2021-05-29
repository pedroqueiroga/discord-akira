from typing import Dict, overload

import discord

from .guild import Guild


class Guilds(Dict[int, Guild]):
    """Guilds is a dictionary from guild ids (int) to Guild objects
    If a user attempts to access a missing guild id, it won't work,
    but if he tries it with a discord guild, then it will create
    a new entry and return it, so he can use it seamlessly."""

    def __missing__(self, key: discord.Guild) -> Guild:
        if type(key) != discord.Guild:
            raise AttributeError('Chave inválida')

        self.__setitem__(key.id, Guild())
        return self[key.id]
