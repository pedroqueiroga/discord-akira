import asyncio
from collections import deque
import discord
from discord.ext.commands import command, Cog
import youtube_dl
import datetime
import functools


class Deejay(Cog):

    def __init__(self, bot):
        self.setlist = deque([])
        self.current_song = None
        self.ydl_opts = {
            'quiet': False,
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
        }
        self.pula_votes = set()
        self.bot = bot

    @command()
    async def toca(self, ctx, *, args):
        """
        Toca a música no canal de voz do invocador. Continua tocando no canal de voz
        em que estiver.
        """

        await self.request(ctx, args)

    @command()
    async def fila(self, ctx):
        """
        Mostra a fila de músicas.
        """
        
        if not self.current_song:
            await ctx.send('Fila vazia.')
        else:
            await ctx.send(embed=self.get_fila_embed())

    @command()
    async def pula(self, ctx):
        """
        Vota para pular a música atual.
        """

        self.pula_votes.add(ctx.author.id)

        n_members = len(ctx.voice_client.channel.members)
        required_votes = 1/3 * (n_members-1) # 1 is the bot

        if len(self.pula_votes) >= required_votes:
            # 1/3 plus of the voice channel members voted to skip the song
            ctx.voice_client.pause()
            self.play_next(ctx.guild)
            await ctx.send('Pulei.')

        else:
            n_to_skip = required_votes - len(self.pula_votes)
            plural = 's' if n_to_skip > 1 else ''
            await ctx.send(f'Preciso de mais {n_to_skip} voto{plural} para pular.')
            
    async def request(self, ctx, song):
        call_play = False
        if not ctx.guild.voice_client:
            # the bot does not have a VoiceClient on this guild
            voice_client = await self.get_voice_client(ctx)
            if not voice_client:
                await ctx.send('Você não está em nenhum chat de voz seu LADRÃO')
                return

            # should call play because isn't playing yet
            call_play = True
        
        # get video source url using youtube_dl
        video_info = {}
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            video = ydl.extract_info(song,
                                  download=False)

            if 'entries' in video.keys():
                # multiple videos, take first
                # probably came from a video search instead of video url
                video = video['entries'][0]
                
            video_info['source_url'] = video['formats'][0]['url']
            video_info['title'] = video['title']
            video_info['webpage_url'] = video['webpage_url']
            video_info['duration'] = video['duration']
            video_info['thumbnail'] = video['thumbnail']

        embed = self.get_toca_embed(ctx.author, video_info)
        await ctx.send(embed=embed)
        self.setlist.append(video_info)

        if call_play:
            self.play_next(ctx.guild)


    def play_next(self, guild):
        voice_client = guild.voice_client
        if not voice_client:
            print('weirdly, i have no voice_client but I should have')
            self.setlist.clear()
            self.current_song = None
            return
        if len(self.setlist) == 0:
            # if the queue is empty, disconnect
            asyncio.run_coroutine_threadsafe(voice_client.disconnect(),
                                             self.bot.loop)
            self.current_song = None
            return
        
        # get an AudioSource from next song in setlist
        next_song_info = self.setlist.popleft()
        audio_source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(next_song_info['source_url'],
                                   before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))

        voice_client.play(audio_source,
                          after=lambda _: self.play_next(guild))

        # clear pula votes for this fresh song
        self.pula_votes.clear()
        self.current_song = next_song_info

    def is_playing_guild(self, guild):
        if guild.voice_client:
            return guild.voice_client.is_playing()
        else:
            return False
            
    async def get_voice_client(self, ctx):
        if ctx.author.voice:
            return await ctx.author.voice.channel.connect()

    def get_setlist_titles(self, current=False, n=None):
        if self.current_song and current:
            titles = [self.current_song['title']]
        else:
            titles = []

        for song in self.setlist:
            titles.append(song['title'])
            if len(titles) == n:
                # if n is not given, will append all titles
                break
        return titles

    def get_setlist_titles_links_formatted(self, current=False):
        if self.current_song and current:
            titles = [
                f"[{self.current_song['title']}]({self.current_song['webpage_url']})"
                ]
        else:
            titles = []

        titles.extend([ f"[{s['title']}]({s['webpage_url']})" for s in self.setlist ])
        return titles
            

    def get_toca_embed(self, author, video_info):
        title = video_info['title']
        duration = self.seconds_human_friendly(video_info['duration'])
        thumbnail = video_info['thumbnail']
        webpage_url = video_info['webpage_url']
        titles = self.get_setlist_titles(current=True, n=3)

        embed = discord.Embed(title=title,
                              url=webpage_url,
                              description=f'**Duração:** {duration}') \
                       .set_author(name=author.display_name,
                                   icon_url=author.avatar_url) \
                       .set_thumbnail(url=thumbnail) \
                       .set_footer(text=', '.join(titles),
                                   icon_url='https://raw.githubusercontent.com/pqueiroga/discord-terraplanista/master/icons/queue_music_white_18dp_36.png')

        return embed

    def get_fila_embed(self):
        titles_links = self.get_setlist_titles_links_formatted(current=False)
        joined_titles_links = '\n'.join(titles_links)
        total_duration = self.seconds_human_friendly(self.total_setlist_duration())
        total_duration_str=f'Duração total: {total_duration}'

        current_song_duration_str = f"**Duração:** {self.seconds_human_friendly(self.current_song['duration'])}"

        next_str = f'\n\n**Próximas:**\n{joined_titles_links}' if self.setlist else ''
        
        embed = discord.Embed(title=self.current_song['title'],
                              url=self.current_song['webpage_url'],
                              description=f'{current_song_duration_str}{next_str}') \
                              .set_author(name=total_duration_str,
                                          icon_url='https://raw.githubusercontent.com/pqueiroga/discord-terraplanista/master/icons/queue_music_white_18dp_36.png') \
                              .set_thumbnail(url=self.current_song['thumbnail'])
        return embed

    def total_setlist_duration(self):
        return functools.reduce(lambda x, y: {'duration': x['duration'] + y['duration']},
                                self.setlist,
                                self.current_song)['duration']

    def seconds_human_friendly(self, seconds):
        if seconds < 60:
            return str(seconds) + ' segundos'
        
        readable = str(datetime.timedelta(seconds=seconds))

        if readable.startswith('0:'):
            return readable[2:]
        if 'day' in readable:
            return readable.replace('day', 'dia')

        return readable
