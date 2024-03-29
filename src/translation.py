"""Translation module for Akira's miaus.

This module contains utilities to ease the use of Akira's language.

.. class:: InfoMessages
.. function:: miau_to_pt(miau)
.. function:: pt_to_miau(phrase)
.. function:: send_with_reaction(message_send, content)
"""

from enum import Enum

from bidict import bidict

from .roman import fromRoman, toRoman
from .utils import is_int


class InfoMessages(Enum):
    """Messages that can be sent by Akira

    Enum class representing messages that Akira can send to the user.
    Typically translated to a miau before sending. It is useful to keep
    only one source of truth for Akira's messages.

    :attribute str LATER: Akira's feeling lazy.
    :attribute str NO_VOICE_CHANNEL: The user needs to be in a voice channel
    but isn't.
    :attribute str NOT_MY_VOICE_CHANNEL: The user needs to be in Akira's voice
    channel but isn't.
    :attribute str SKIPPED: Akira skipped a song.
    :attribute str SKIPPED_SPECIFIC: Akira skipped a song that is not current.
    :attribute str EMPTY_QUEUE: The setlist is empty.
    :attribute str NOT_PLAYING: Akira's not playing anything.
    :attribute str INVALID_VOLUME: Requested volume is not a volume.
    :attribute str INCREASED_VOLUME: Volume successfully increased.
    :attribute str DECREASED_VOLUME: Volume successfully decreased.
    :attribute str NO_VOLUME_CHANGE: Requested volume was current volume.
    :attribute str VOLUME_TOO_LOUD: Requested volume is higher than ceil.
    :attribute str VOLUME_TOO_LOW: Requested volume is lower than floor.
    :attribute str COMMAND_MISUSE: Command was used incorrectly.
    :attribute str ZERO: Represents zero, for type safety.
    :attribute str NEED_MORE_VOTES: More votes are needed to skip a song.
    :attribute str INVALID_QUEUE_POSITION: Queue position specified is not available.
    :attribute str INVALID_URL: Requested URL is a bad URL, could be a site other than youtube.
    :attribute str NO_VIDEO_FOUND: Video search returned no results.
    :attribute str VIDEO_UNAVAILABLE: Video download failed for some reason or another.
    :attribute str NO_TRANSMOGRIFY: Queue doesn't have enough elements for transmogrify to make sense.
    """

    LATER = 'Talvez mais tarde.'
    NO_VOICE_CHANNEL = 'Você não está em nenhum canal de voz.'
    NOT_MY_VOICE_CHANNEL = 'Você não está no meu canal de voz.'
    SKIPPED = 'Pulei.'
    SKIPPED_SPECIFIC = 'Removi:'
    EMPTY_QUEUE = 'Setlist vazia.'
    NOT_PLAYING = 'Não estou tocando nada.'
    INVALID_VOLUME = 'Esse volume não fez sentido para mim.'
    INCREASED_VOLUME = 'Aumentei o volume em'
    DECREASED_VOLUME = 'Abaixei o volume em'
    NO_VOLUME_CHANGE = 'Não alterei o volume.'
    VOLUME_TOO_LOUD = 'Não posso aumentar o volume tanto assim.'
    VOLUME_TOO_LOW = 'Não posso diminuir o volume para abaixo de zero.'
    COMMAND_MISUSE = 'Não consegui te entender. (tente $help <comando>)'
    ZERO = '0'
    NEED_MORE_VOTES = 'Preciso de mais votos para pular:'
    INVALID_QUEUE_POSITION = 'Posição na fila inválida...'
    INVALID_URL = 'URL INVÁLIDA!!'
    NO_VIDEO_FOUND = 'Nenhum vídeo encontrado.'
    VIDEO_UNAVAILABLE = 'Vídeo encontrado está indisponível. Tente modificar a busca, ou usar uma URL.'
    NO_TRANSMOGRIFY = 'A fila não tem elementos o suficiente.'


_translation_book: bidict[str, InfoMessages] = bidict(
    {
        'miaau.': InfoMessages.LATER,
        'MIAAAU!!!': InfoMessages.NO_VOICE_CHANNEL,
        'Miau...': InfoMessages.NOT_MY_VOICE_CHANNEL,
        'Miau.': InfoMessages.SKIPPED,
        'Mierrrh!': InfoMessages.SKIPPED_SPECIFIC,
        '...': InfoMessages.EMPTY_QUEUE,
        '...?': InfoMessages.NOT_PLAYING,
        'rrrr.': InfoMessages.INVALID_VOLUME,
        'RRRR!!': InfoMessages.VOLUME_TOO_LOUD,
        'rrrr...': InfoMessages.VOLUME_TOO_LOW,
        'Mrrau!!': InfoMessages.INCREASED_VOLUME,
        'Mrrau...': InfoMessages.DECREASED_VOLUME,
        'Mrrau.': InfoMessages.NO_VOLUME_CHANGE,
        '????': InfoMessages.COMMAND_MISUSE,
        'Meow.': InfoMessages.ZERO,
        'Miauau.': InfoMessages.NEED_MORE_VOTES,
        'mierr?': InfoMessages.INVALID_QUEUE_POSITION,
        'AUAU!!': InfoMessages.INVALID_URL,
        'mmmm...': InfoMessages.NO_VIDEO_FOUND,
        'miauauaua!': InfoMessages.VIDEO_UNAVAILABLE,
        'miaumiau.': InfoMessages.NO_TRANSMOGRIFY,
    }
)


def miau_to_pt(miau: str):
    """Translate a miau into a portuguese phrase.

    :param str miau: The miau to be translated.
    :returns: a miau written in portuguese.
    :rtype: str
    :raises TypeError: if miau is not a string.
    :raises KeyError: if miau is not a valid Akira miau.
    """

    if type(miau) != str:
        raise TypeError('miau should be a string.')

    splitted = miau.split(' ')
    if len(splitted) == 2:
        # then we are dealing with a miau numeral
        miau = splitted[0]
        n_miau = splitted[1]
        n = miau_to_number(n_miau)
        translation = _translation_book[miau].value
        return f'{translation} {n}'
    elif len(splitted) == 1:
        try:
            translation = _translation_book[miau].value
        except (KeyError, AttributeError):
            # could be a miau numeral
            translation = miau_to_number(miau)

    return translation


def pt_to_miau(phrase: InfoMessages, n=None):
    """Translates a phrase [and number] into a miau.

    :param phrase: The phrase to be translated.
    :type phrase: InfoMessages instance.
    :param int n: optional. a number to be translated into miau
    :returns: a portuguese phrase written in miau.
    :rtype: str
    :raises TypeError: if the phrase is not a string.
    :raises KeyError: if the phrase can't be translated.
    """

    if not (isinstance(phrase, InfoMessages) or is_int(phrase)):
        raise TypeError(
            'infomessage should be an int or InfoMessages instance.'
        )

    translation = _translation_book.inverse[phrase]
    if n is not None:
        n_miau = number_to_miau(int(n))
        return f'{translation} {n_miau}'
    return translation


def number_to_miau(n: int):
    """Translates a number into a miau.

    :param int n: The number to be translated.
    :returns: n written in miau
    :rtype: str
    """
    if n == 0:
        return _translation_book.inverse[InfoMessages.ZERO]
    roman = toRoman(n)
    return f'M{roman}AU.'


def miau_to_number(miau: str):
    """Translates a miau into a number.

    :param str miau: The miau to be translated.
    :returns: miau as an intenger.
    :rtype: int
    """
    # remove M and AU.
    if miau == _translation_book.inverse[InfoMessages.ZERO]:
        return 0
    roman = miau[1:-3]
    n = fromRoman(roman)
    return n


async def send_with_reaction(message_send, content):
    """Add translation reaction to a message after sending it.

    This auxiliary function is used a lot to keep up with Akira's
    message-reaction-control-panel.

    :param method message_send: A method that sends a message and returns
    a message.
    :param str content: The content the message should have.
    """

    message = await message_send(content)
    await message.add_reaction('❔')
