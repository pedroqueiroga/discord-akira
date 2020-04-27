import asyncio
import functools
from collections import deque

import discord
from discord.ext.commands import Cog, command, guild_only

from ...translation import InfoMessages, pt_to_miau, send_with_reaction
from ...utils import seconds_human_friendly
from .youtuber import Youtuber


class Deejay(Cog):
    """Akira discotecando"""

    def __init__(self, bot):
        self.bot = bot
        self.setlists = {}
        self.current_songs = {}
        self.pula_votes = {}
        self.youtuber = Youtuber()

    @command()
    @guild_only()
    async def toca(self, ctx, *, args):
        """Toca música.
        Se não estiver conectada a um canal de voz, entra no canal de voz do
        invocador. Continua tocando no canal de voz em que estiver.
        Não aceita pedidos de quem não está no canal de voz.

        :param str args: URL ou string de busca no youtube.
        """

        await self.request(ctx, args)

    @command()
    @guild_only()
    async def fila(self, ctx):
        """Mostra a setlist atual."""

        current_song = self.current_songs.get(ctx.guild.id)
        if not current_song:
            meow = pt_to_miau(InfoMessages.EMPTY_QUEUE)
            await send_with_reaction(ctx.send, meow)
        else:
            await ctx.send(embed=self.get_fila_embed(ctx.guild.id))

    @command()
    @guild_only()
    async def pula(self, ctx):
        """Vota para pular a música atual.
        Pula com votos de 1/3 dos membros do canal de voz em que Akira está.
        Não aceita votos de quem não está no canal de voz.
        """

        current_song = self.current_songs.get(ctx.guild.id)
        # makes sense only if there is a song playing
        if not current_song:
            meow = pt_to_miau(InfoMessages.NOT_PLAYING)
            await send_with_reaction(ctx.send, meow)
            return

        # only accept requests from members in the same voice channel
        if (not ctx.author.voice) or (
            not ctx.author.voice.channel == ctx.voice_client.channel
        ):
            meow = pt_to_miau(InfoMessages.NOT_MY_VOICE_CHANNEL)
            await send_with_reaction(ctx.send, meow)
            return

        self.pula_votes[ctx.guild.id].add(ctx.author.id)

        n_members = len(ctx.voice_client.channel.members)
        required_votes = 1 / 3 * (n_members - 1)  # 1 is the bot

        if len(self.pula_votes[ctx.guild.id]) >= required_votes:
            # 1/3 plus of the voice channel members voted to skip the song
            ctx.voice_client.pause()
            self.play_next(ctx.guild)
            meow = pt_to_miau(InfoMessages.SKIPPED)
            await send_with_reaction(ctx.send, meow)

        else:
            n_to_skip = required_votes - len(self.pula_votes[ctx.guild.id])
            # TODO: logic for any number (right now works for 1-9 only)
            meow = pt_to_miau(n_to_skip)
            await send_with_reaction(ctx.send, meow)

    async def request(self, ctx, song):
        call_play = False
        if not ctx.guild.voice_client:
            # the bot does not have a VoiceClient on this guild
            voice_client = await self.get_voice_client(ctx)
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

        video_info = self.youtuber.get_video_info(song)
        self.setlists_append(ctx.guild.id, video_info)
        embed = self.get_toca_embed(ctx.author, video_info)
        await ctx.send(embed=embed)

        if call_play:
            self.play_next(ctx.guild)

    def setlists_append(self, guild_id, obj):
        if self.setlists.get(guild_id):
            # the guild has a non-empty setlist
            self.setlists[guild_id].append(obj)
        else:
            # the setlist is missing, or empty.
            self.setlists[guild_id] = deque([obj])

    def play_next(self, guild):
        voice_client = guild.voice_client
        if not voice_client:
            print('weirdly, i have no voice_client but I should have')
            self.setlists[guild.id].clear()
            self.current_songs[guild.id] = None
            return
        if len(self.setlists[guild.id]) == 0:
            # if the queue is empty, disconnect
            asyncio.run_coroutine_threadsafe(
                voice_client.disconnect(), self.bot.loop
            )
            self.current_songs[guild.id] = None
            return

        # get an AudioSource from next song in setlist
        next_song_info = self.setlists[guild.id].popleft()
        audio_source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                next_song_info['source_url'],
                before_options='-reconnect 1 -reconnect_streamed 1 '
                '-reconnect_delay_max 5',
            )
        )

        voice_client.play(audio_source, after=lambda _: self.play_next(guild))

        # create clean pula votes for this fresh song
        self.pula_votes[guild.id] = set()
        self.current_songs[guild.id] = next_song_info

    def is_playing_guild(self, guild):
        if guild.voice_client:
            return guild.voice_client.is_playing()
        else:
            return False

    async def get_voice_client(self, ctx):
        if ctx.author.voice:
            return await ctx.author.voice.channel.connect()

    def get_setlist_titles(self, guild_id, current=False, n=None):
        current_song = self.current_songs.get(guild_id)
        if current_song and current:
            titles = [current_song['title']]
        else:
            titles = []

        for song in self.setlists[guild_id]:
            titles.append(song['title'])
            if len(titles) == n:
                # if n is not given, will append all titles
                break
        return titles

    def get_setlist_titles_links_formatted(self, guild_id, current=False):
        """Gets the titles and links of the guild's setlist.

        Formats the links in markdown.

        :param int guild_id: id of a guild
        :param bool current: If should include the current song
        :returns: a list of markdown formatted strings
        :rtype: [str]

        """
        current_song = self.current_songs.get(guild_id)
        if current_song and current:
            titles = [
                f"[{current_song['title']}]({current_song['webpage_url']})"
            ]
        else:
            titles = []

        titles.extend(
            [
                f"[{s['title']}]({s['webpage_url']})"
                for s in self.setlists[guild_id]
            ]
        )
        return titles

    def get_toca_embed(self, author, video_info, n_titles=3):
        title = video_info['title']
        duration = seconds_human_friendly(video_info['duration'])
        thumbnail = video_info['thumbnail']
        webpage_url = video_info['webpage_url']

        titles = self.get_setlist_titles(
            author.guild.id, current=True, n=n_titles
        )
        total_songs = len(self.setlists[author.guild.id]) + 1  # + current song
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
                icon_url='https://raw.githubusercontent.com/pqueiroga/'
                'discord-terraplanista/master/icons/'
                'playlist_add_check_white_18dp_36.png',
            )
        )

        return embed

    def get_fila_embed(self, guild_id):
        titles_links = self.get_setlist_titles_links_formatted(
            guild_id, current=False
        )
        joined_titles_links = '\n'.join(titles_links)
        total_duration = seconds_human_friendly(
            self.total_setlist_duration(guild_id)
        )
        total_duration_str = f'Duração total: {total_duration}'
        current_song = self.current_songs.get(guild_id)
        current_song_duration_str = (
            f"**Duração:** {seconds_human_friendly(current_song['duration'])}"
        )

        next_str = (
            f'\n\n**Próximas:**\n{joined_titles_links}'
            if self.setlists[guild_id]
            else ''
        )

        embed = (
            discord.Embed(
                title=current_song['title'],
                url=current_song['webpage_url'],
                description=f'{current_song_duration_str}{next_str}',
            )
            .set_author(
                name=total_duration_str,
                icon_url='https://raw.githubusercontent.com/pqueiroga/'
                'discord-terraplanista/master/icons/'
                'queue_music_white_18dp_36.png',
            )
            .set_thumbnail(url=current_song['thumbnail'])
        )
        return embed

    def total_setlist_duration(self, guild_id):
        current_song = self.current_songs.get(guild_id)
        return functools.reduce(
            lambda x, y: {'duration': x['duration'] + y['duration']},
            self.setlists[guild_id],
            current_song,
        )['duration']
