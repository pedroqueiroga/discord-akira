import asyncio
import datetime
import functools
import math
import re
import time
from random import shuffle
from typing import Any, Dict, List, Tuple, Union

import discord
from discord.ext.commands import (BadArgument, Bot, Cog, Context, command,
                                  guild_only)
from youtube_dl.utils import DownloadError

from ...translation import (InfoMessages, number_to_miau, pt_to_miau,
                            send_with_reaction)
from ...utils import is_int, seconds_human_friendly
from .guild import Guild
from .guilds import Guilds
from .song import Song
from .youtuber import Youtuber


class Deejay(Cog):
    """Akira discotecando"""

    bot: Bot
    youtuber: Youtuber = Youtuber()
    guilds: Guilds = Guilds()

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @guild_only()
    async def toca(self, ctx: Context, *, args) -> None:
        """Toca música.
        Se não estiver conectada a um canal de voz, entra no canal de voz do
        invocador. Continua tocando no canal de voz em que estiver.
        Não aceita pedidos de quem não está no canal de voz.

        :param str args: URL ou string de busca no youtube.
        """

        await self.request(ctx, args)

    @command()
    @guild_only()
    async def fila(self, ctx: Context) -> None:
        """Mostra a setlist atual."""

        guild = self.guilds[ctx.guild.id]
        current_song = guild.current_song

        if not current_song:
            meow = pt_to_miau(InfoMessages.EMPTY_QUEUE)
            await send_with_reaction(ctx.send, meow)
        else:
            fila_embed = self.get_fila_embed(guild)
            await ctx.send(embed=fila_embed)

    @command()
    @guild_only()
    async def pula(self, ctx: Context, position=0) -> None:
        """Vota para pular uma música da fila.
        Pula com votos de 1/3 dos membros do canal de voz em que Akira está.
        Não aceita votos de quem não está no canal de voz.
        Sem argumentos, pula a música atual.

        :param int position: Posição da música na fila
        """
        guild = self.guilds[ctx.guild.id]
        current_song = guild.current_song
        # makes sense only if there is a song playing
        if not current_song:
            meow = pt_to_miau(InfoMessages.NOT_PLAYING)
            await send_with_reaction(ctx.send, meow)
            return

        setlist = guild.setlist

        if position < 0 or position > len(setlist):
            meow = pt_to_miau(InfoMessages.INVALID_QUEUE_POSITION)
            await send_with_reaction(ctx.send, meow)
            return

        # only accept requests from members in the same voice channel
        # except if whoever wants to skip requested the song
        if (
            (not ctx.author.voice)
            or (not ctx.author.voice.channel == ctx.voice_client.channel)
        ) and (current_song.requester_id != ctx.author.id):
            meow = pt_to_miau(InfoMessages.NOT_MY_VOICE_CHANNEL)
            await send_with_reaction(ctx.send, meow)
            return

        song_to_skip: Song
        if position == 0:
            song_to_skip = current_song
        else:
            # position-1 because user will input as 1-indexed list
            song_to_skip = setlist[position - 1]
            song_to_skip.pula_votes.add(ctx.author.id)

        n_members = len(ctx.voice_client.channel.members)
        required_votes = math.floor(1 / 3 * (n_members - 1))  # 1 is the bot

        if (
            len(song_to_skip.pula_votes) >= required_votes
            or current_song.requester_id == ctx.author.id
        ):
            meow = None
            if position > 0:
                meow = pt_to_miau(InfoMessages.SKIPPED_SPECIFIC)
                del setlist[position - 1]
            else:
                ctx.voice_client.pause()
                self.play_next(ctx.guild)
                meow = pt_to_miau(InfoMessages.SKIPPED)
            await send_with_reaction(ctx.send, meow)

        else:
            n_to_skip = required_votes - len(song_to_skip.pula_votes)

            meow = pt_to_miau(InfoMessages.NEED_MORE_VOTES, n_to_skip)
            await send_with_reaction(ctx.send, meow)

    @command()
    @guild_only()
    async def limpa(self, ctx: Context) -> None:
        """Limpa a fila.
        Este comando limpa a fila e pronto."""
        self.guilds[ctx.guild.id].setlist.clear()
        # TODO
        await ctx.send('miau legal')

    @command()
    @guild_only()
    async def trans(self, ctx: Context, *args) -> None:
        """Forma curta para "transmogrifar"."""
        await self.transmogrifar(ctx, *args)

    @command()
    @guild_only()
    async def transmogrifar(self, ctx: Context, *args) -> None:
        """Altera o estado da fila.

        Quatro sintaxes são permitidas.
        Primeira sintaxe:
          $transmogrifar a b c d e f: Os números (a,b,c,d,e,f) precisam estar contidos num intervalo contínuo. Cria uma nova ordem para a lista.
        Segunda sintaxe:
          $transmogrifar a -> b: Empurra a música da posição a para a posição b.
        Terceira sintaxe:
          $transmogrifar a <- b: Empurra a música da posição b para a posição a.
        Quarta sintaxe:
          $transmogrifar a <-> b: Troca duas músicas de lugar.

        Exemplos:       1    2       3        4     5       6
          sendo a fila: a maconha proibida, mata somente minoria
          "$transmogrifar 3 1 2 4 6 5" resulta em: proibida, a maconha mata minoria somente
          "$transmogrifar 6 5" resulta em: a maconha proibida, mata minoria somente
          "$transmogrifar 5 4" resulta em: a maconha proibida, somente mata minoria
          "$transmogrifar 3 -> 6" resulta em: a maconha mata somente minoria proibida,
          "$transmogrifar 3 <- 4" resulta em: a maconha mata proibida, somente minoria
          "$transmogrifar 3 <-> 5" resula em: a maconha somente mata proibida, minoria
        """
        setlist = self.guilds[ctx.guild.id].setlist

        if len(setlist) < 2:
            meow = pt_to_miau(InfoMessages.NO_TRANSMOGRIFY)
            await send_with_reaction(ctx.send, meow)
            return

        if len(args) == 0:
            self.shuffle(setlist)
            await ctx.invoke(self.bot.get_command('fila'))
            return

        if len(args) < 2:
            raise BadArgument(None)

        arglist = list(args)

        rearrange = None
        try:
            rearrange = list(map(lambda x: int(x) - 1, arglist))
            self.raise_if_invalid_range(
                max(rearrange),
                min(rearrange),
                len(setlist),
            )
        except ValueError:
            pass
        except:
            raise BadArgument(None)

        if rearrange is not None:
            try:
                self.reorder_list(setlist, rearrange)
                await ctx.invoke(self.bot.get_command('fila'))
                return
            except:
                raise BadArgument(None)

        if len(arglist) != 3:
            raise BadArgument(None)

        arglist = list(map(lambda x: self.try_subtract_one(x), arglist))
        try:
            self.raise_if_invalid_range(arglist[0], arglist[2], len(setlist))
        except:
            raise BadArgument(None)

        if arglist[1] == '<-':
            arglist[1] = '->'
            arglist[0], arglist[2] = arglist[2], arglist[0]

        if arglist[1] == '->':
            self.reorder_single(
                setlist,
                arglist[0],
                arglist[2],
            )
            await ctx.invoke(self.bot.get_command('fila'))
            return

        if arglist[1] == '<->':
            self.reorder_swap(
                setlist,
                arglist[0],
                arglist[2],
            )
            await ctx.invoke(self.bot.get_command('fila'))
            return

        raise BadArgument(None)
        return

    async def request(self, ctx: Context, search_url: str) -> None:
        call_play = False
        voice_client = ctx.guild.voice_client
        if not voice_client:
            # the bot does not have a VoiceClient on this guild
            voice_client = await self.connect_to_user_voice_client(ctx.author)
            if not voice_client:
                meow = pt_to_miau(InfoMessages.NO_VOICE_CHANNEL)
                await send_with_reaction(ctx.send, meow)
                return

            # should call play because isn't playing yet
            call_play = True
        elif (not ctx.author.voice) or (
            not ctx.author.voice.channel == ctx.voice_client.channel
        ):
            # only accept requests from members in the same voice channel
            meow = pt_to_miau(InfoMessages.NOT_MY_VOICE_CHANNEL)
            await send_with_reaction(ctx.send, meow)
            return

        try:
            videos = self.youtuber.get_video_info(search_url)
        except AttributeError:
            meow = pt_to_miau(InfoMessages.INVALID_URL)
            await send_with_reaction(ctx.send, meow)
            return
        except IndexError:
            meow = pt_to_miau(InfoMessages.NO_VIDEO_FOUND)
            await send_with_reaction(ctx.send, meow)
            return
        except DownloadError as err:
            print(datetime.datetime.today().timestamp(), err)
            meow = pt_to_miau(InfoMessages.VIDEO_UNAVAILABLE)
            await send_with_reaction(ctx.send, meow)
            return

        for song in videos:
            setlist = self.guilds[ctx.guild.id].setlist
            song.requester_id = ctx.author.id
            setlist.append(song)
        embed = self.get_toca_embed(ctx.author, videos[0])
        await ctx.send(embed=embed)

        if self.should_start_playing(voice_client):
            self.play_next(ctx.guild)

    def play_next(self, dd_guild: discord.Guild) -> None:
        voice_client = dd_guild.voice_client
        guild = self.guilds[dd_guild.id]
        setlist = guild.setlist

        if not voice_client:
            print('weirdly, i have no voice_client but I should have')
            setlist.clear()
            guild.current_song = None
            return
        if len(setlist) == 0:
            guild.stopped_playing_timestamp = time.monotonic()
            # if the queue is empty, disconnect after 10 minutes
            asyncio.run_coroutine_threadsafe(
                self._trigger_disconnect(voice_client, guild), self.bot.loop
            )
            guild.current_song = None
            return

        # get an AudioSource from next song in setlist
        next_song_info = setlist.pop(0)
        audio_source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                next_song_info.source_url,
                before_options='-reconnect 1 -reconnect_streamed 1 '
                '-reconnect_delay_max 5',
            )
        )

        audio_source.volume = guild.loudness

        try:
            voice_client.play(
                audio_source, after=lambda _: self.play_next(dd_guild)
            )

            guild.stopped_playing_timestamp = None

            guild.current_song = next_song_info
        except discord.ClientException:
            if voice_client.is_playing():
                print(
                    f'tried to play {next_song_info}, but i am already playing {guild.current_song}'
                )

    def is_playing_guild(self, guild: discord.Guild) -> bool:
        """Decides if the Akira is playing an Audio Source in this guild.

        :param discord.Guild guild: Guild to check
        :returns: True if Akira is playing in guild.
        :rtype: bool

        """
        if guild.voice_client:
            return guild.voice_client.is_playing()
        else:
            return False

    async def connect_to_user_voice_client(
        self, user: discord.abc.User
    ) -> discord.VoiceClient:
        if user.voice:
            return await user.voice.channel.connect()

    def get_setlist_titles(
        self, guild: Guild, current=False, n=None
    ) -> List[str]:
        current_song = guild.current_song
        if current_song and current:
            titles = [current_song.title]
        else:
            titles = []

        for song in guild.setlist:
            titles.append(song.title)
            if len(titles) == n:
                # if n is not given, will append all titles
                break
        return titles

    def get_setlist_titles_links_formatted(
        self, guild: Guild, current=False
    ) -> List[str]:
        """Gets the titles and links of the guild's setlist.

        Formats the links in markdown.

        :param int guild_id: id of a guild
        :param bool current: If should include the current song
        :returns: a list of markdown formatted strings
        :rtype: [str]

        """
        current_song = guild.current_song
        if current_song and current:
            titles = [f"[{current_song.title}]({current_song.webpage_url})"]
        else:
            titles = []

        titles.extend(
            [
                f"{idx+1}. [{s.title}]({s.webpage_url})"
                for idx, s in enumerate(guild.setlist)
            ]
        )
        return titles

    def get_toca_embed(
        self, author: discord.abc.User, song: Song, n_titles=3
    ) -> discord.Embed:
        guild = self.guilds[author.guild]

        title = song.title
        duration = seconds_human_friendly(song.duration)
        thumbnail = song.thumbnail
        webpage_url = song.webpage_url

        titles = self.get_setlist_titles(guild, current=True, n=n_titles)
        total_songs = len(guild.setlist) + 1  # + current song
        footer = ', '.join(titles) + ('...' if total_songs > n_titles else '')

        embed = (
            discord.Embed(
                title=title,
                url=webpage_url,
                description=f'**Duração:** {duration}',
            )
            .set_author(name=author.display_name, icon_url=author.avatar_url)
            .set_thumbnail(url=thumbnail)
            .set_footer(
                text=footer,
                icon_url='https://raw.githubusercontent.com/pedroqueiroga/'
                'discord-akira/master/icons/'
                'playlist_add_check_white_18dp_36.png',
            )
        )

        return embed

    def get_fila_embed(self, guild: Guild) -> discord.Embed:
        titles_links = self.get_setlist_titles_links_formatted(
            guild, current=False
        )
        titles_links_included = []
        total_len = 0
        for tl in titles_links:
            if total_len > 1500:
                break

            total_len += len(tl)
            titles_links_included.append(tl)

        joined_titles_links = '\n'.join(titles_links_included)
        total_duration = seconds_human_friendly(
            self.total_setlist_duration(guild)
        )
        total_duration_str = f'Duração total: {total_duration}'
        current_song = guild.current_song

        if current_song is None:
            raise Exception('current_song is None')

        current_song_duration_str = (
            f"**Duração:** {seconds_human_friendly(current_song.duration)}"
        )

        next_str = (
            f'\n\n**Próximas:**\n{joined_titles_links}'
            if guild.setlist
            else ''
        )

        listed_songs_diff = len(titles_links) - len(titles_links_included)

        if listed_songs_diff > 0:
            next_str += f'\n... e mais {listed_songs_diff}'

        description = f'{current_song_duration_str}{next_str}'

        embed = (
            discord.Embed(
                title=current_song.title,
                url=current_song.webpage_url,
                description=description,
            )
            .set_author(
                name=total_duration_str,
                icon_url='https://raw.githubusercontent.com/pqueiroga/'
                'discord-terraplanista/master/icons/'
                'queue_music_white_18dp_36.png',
            )
            .set_thumbnail(url=current_song.thumbnail)
        )
        return embed

    def total_setlist_duration(self, guild: Guild) -> int:
        current_song = guild.current_song

        if current_song is None:
            raise Exception('current_song is None')

        return (
            sum(map(lambda x: x.duration, guild.setlist))
            + current_song.duration
        )

    @command()
    @guild_only()
    async def volume(self, ctx: Context, requested_volume=None) -> None:
        """Dita o volume da discotecagem de Akira.

        Aceita apenas um argumento, o volume, que deve ser de 0 a 11.
        0 muta o bot, 10 coloca no volume original, 11 coloca no dobro do
        volume original. Alternativemente, se for da forma +x, ou -x, aumenta
        ou diminui o volume em x. Vai até 11.

        :param str args: mudança de volume
        """

        if not self.is_playing_guild(ctx.guild):
            miau = pt_to_miau(InfoMessages.NOT_PLAYING)
            return await send_with_reaction(ctx.send, miau)

        audio_source = ctx.voice_client.source
        current_volume = audio_source.volume

        if requested_volume is None:
            # if no volume is requested, print current volume human-friendly
            whole_current_volume = self.from_decimal_volume(current_volume)
            miau = number_to_miau(whole_current_volume)
            return await send_with_reaction(ctx.send, miau)

        if not is_int(requested_volume):
            miau = pt_to_miau(InfoMessages.INVALID_VOLUME)
            return await send_with_reaction(ctx.send, miau)

        new_volume, diff_volume = self.get_new_volume(
            current_volume,
            int(requested_volume),
            self.is_requested_volume_diff(requested_volume),
        )

        # validating new volume against maximum and minimum volumes
        if new_volume > 2:
            miau = pt_to_miau(InfoMessages.VOLUME_TOO_LOUD)
            return await send_with_reaction(ctx.send, miau)
        if new_volume < 0:
            miau = pt_to_miau(InfoMessages.VOLUME_TOO_LOW)
            return await send_with_reaction(ctx.send, miau)

        # new volume ok, finally commit the change
        guild = self.guilds[ctx.guild.id]
        guild.loudness = new_volume
        audio_source.volume = guild.loudness

        if diff_volume > 0:
            miau = pt_to_miau(InfoMessages.INCREASED_VOLUME, abs(diff_volume))
        elif diff_volume < 0:
            miau = pt_to_miau(InfoMessages.DECREASED_VOLUME, abs(diff_volume))
        else:
            miau = pt_to_miau(InfoMessages.NO_VOLUME_CHANGE)

        # this method is quite long, it is mostly verifications
        return await send_with_reaction(ctx.send, miau)

    def get_new_volume(
        self, current_volume: float, volume: float, diff=False
    ) -> Tuple[float, float]:
        whole_current_volume = self.from_decimal_volume(current_volume)
        if diff:
            new_volume = whole_current_volume + volume
        else:
            new_volume = volume

        diff_volume = new_volume - whole_current_volume

        return (
            self.to_decimal_volume(new_volume),
            diff_volume,
        )

    def is_requested_volume_diff(self, requested_volume: str) -> bool:
        return requested_volume.startswith('+') or requested_volume.startswith(
            '-'
        )

    def from_decimal_volume(self, volume: float) -> int:
        whole_volume = round(volume * 10)
        if whole_volume < 20 and whole_volume > 11:
            raise Exception("Invalid Volume")
        return 11 if whole_volume == 20 else whole_volume

    def to_decimal_volume(self, volume: float) -> float:
        return ((volume + 9) if volume > 10 else volume) / 10

    async def _trigger_disconnect(
        self, voice_client: discord.VoiceClient, guild: Guild
    ):
        ten_minutes = 600  # seconds

        await asyncio.sleep(ten_minutes)

        if len(guild.setlist) > 0 or (guild.stopped_playing_timestamp is None):
            return

        time_since_stop = time.monotonic() - guild.stopped_playing_timestamp

        if time_since_stop >= ten_minutes:
            await voice_client.disconnect()
            guild.stopped_playing_timestamp = None

    def should_start_playing(self, voice_client: discord.VoiceClient) -> bool:
        return not voice_client.is_playing()

    def get_list_range(self, l: List[int]) -> Dict[str, int]:
        """Takes a list and returns the range it comprehends.
        If some numbers are skipped, errors out"""

        sorted_list = sorted(l)

        for (i, j) in zip(sorted_list, sorted_list[1:]):
            if i != j - 1:
                raise Exception('epa')

        return {'start': sorted_list[0], 'end': sorted_list[-1]}

    def reorder_list(self, l: List[Any], new_order: List[int]) -> None:
        """Reorders a list in place according to a new order"""
        ordering_range = self.get_list_range(new_order)

        l[ordering_range['start'] : ordering_range['end'] + 1] = [
            l[i] for i in new_order
        ]

    def reorder_single(
        self, l: List[Any], current_index: int, new_index: int
    ) -> None:
        """Repositions in place a single element in a list, pushing around the
        other elements"""

        element = l[current_index]

        del l[current_index]

        l.insert(new_index, element)

    def reorder_swap(self, l: List[Any], index1: int, index2: int) -> None:
        """Swaps two elements of a list, in place"""
        l[index1], l[index2] = l[index2], l[index1]

    def try_subtract_one(self, value: str) -> Union[int, str]:
        try:
            return int(value) - 1
        except (ValueError, TypeError):
            return value

    def raise_if_invalid_position(self, index: int, length: int) -> None:
        if index > length or index < 0:
            raise Exception

    def raise_if_invalid_range(
        self, index1: int, index2: int, length: int
    ) -> None:
        self.raise_if_invalid_position(index1, length)
        self.raise_if_invalid_position(index2, length)

    def shuffle(self, l: List[Any]) -> None:
        """Shuffles a list in place until it is really shuffled!
        Time complexity should be about 1/e"""

        original_list = l.copy()

        really_shuffled = False

        while not really_shuffled:
            shuffle(l)
            repeated_positions = 0
            for a, b in zip(l, original_list):
                if a == b:
                    repeated_positions += 1
                if repeated_positions > len(original_list) / 2:
                    break
            else:
                really_shuffled = True
