"""Translation module for Akira's miaus.

This module contains utilities to ease the use of Akira's language.

.. class:: InfoMessages
.. function:: miau_to_pt(miau)
.. function:: pt_to_miau(phrase)
.. function:: send_with_reaction(message_send, content)
"""

from bidict import bidict
from enum import Enum
from .utils import is_int


class InfoMessages(Enum):
    """Messages that can be sent by Akira

    Enum class representing messages that Akira can send to the user.
    Typically translated to a miau before sending. It is useful to keep
    only one source of truth for Akira's messages.

    :attribute str LATER: Akira's feeling lazy.
    :attribute str NO_VOICE_CHANNEL: The user needs to be in a voice channel but isn't.
    :attribute str NOT_MY_VOICE_CHANNEL: The user needs to be in Akira's voice channel but isn't.
    :attribute str SKIPPED: Akira skipped a song.
    :attribute str EMPTY_QUEUE: The setlist is empty.
    :attribute str NOT_PLAYING: Akira's not playing anything.
    """

    LATER = 'Talvez mais tarde.'
    NO_VOICE_CHANNEL = 'Você não está em nenhum canal de voz.'
    NOT_MY_VOICE_CHANNEL = 'Você não está no meu canal de voz.'
    SKIPPED = 'Pulei.'
    EMPTY_QUEUE = 'Setlist vazia.'
    NOT_PLAYING = 'Não estou tocando nada.'
    

_translation_book = bidict({
    'miaau.': InfoMessages.LATER,
    'MIAAAU!!!': InfoMessages.NO_VOICE_CHANNEL,
    'Miau...': InfoMessages.NOT_MY_VOICE_CHANNEL,
    'Miau.': InfoMessages.SKIPPED,
    '...': InfoMessages.EMPTY_QUEUE,
    '...?': InfoMessages.NOT_PLAYING,
    'Meow.': 0,
    'miau?': 1,
    'miiau!': 2,
    'miiiau!!': 3,
    'mivau.': 4,
    'MVAU.': 5,
    'mviau.': 6,
    'mviiau.': 7,
    'MViiIAU!': 8,
    'mixau.': 9,
})

def miau_to_pt(miau):
    """Translate a miau into a portuguese phrase.

    :param str miau: The miau to be translated.
    :returns: a miau written in portuguese.
    :rtype: str
    :raises TypeError: if miau is not a string.
    :raises KeyError: if miau is not a valid Akira miau.
    """

    if type(miau) != str:
        raise TypeError('miau should be a string.')

    if is_int(_translation_book[miau]):
        n = int(_translation_book[miau])
        plural = 's' if n > 1 else ''
        translation = f'Preciso de mais {n} voto{plural} para pular.'
        return translation
    
    return _translation_book[miau].value
    
def pt_to_miau(infomessage):
    """Translate an InfoMessage into a miau.

    :param phrase: The phrase to be translated.
    :type phrase: InfoMessage instance.
    :returns: a portuguese phrase written in miau.
    :rtype: str
    :raises TypeError: if the phrase is not a string.
    :raises KeyError: if the phrase can't be translated.
    """

    if not isinstance(infomessage, InfoMessages):
        raise TypeError('infomessage should be a InfoMessages instance.')

    return _translation_book.inverse[infomessage]

async def send_with_reaction(message_send, content):
    """Add translation reaction to a message after sending it.

    This auxiliary function is used a lot to keep up with Akira's
    message-reaction-control-panel.
    
    :param method message_send: A method that sends a message and returns a message.
    :param str content: The content the message should have.
    """
    
    message = await message_send(content)
    await message.add_reaction('❔')
