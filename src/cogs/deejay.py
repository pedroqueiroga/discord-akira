import asyncio
from collections import deque
import discord
from discord.ext.commands import command, Cog
import youtube_dl


class Deejay(Cog):

    def __init__(self, bot):
        self.setlist = deque([])
        self.ydl_opts = {
            'quiet': False,
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
        }
        self.bot = bot

    @command()
    async def toca(self, ctx, *, args):
        """
        Toca a música no canal de voz do invocador. Continua tocando no canal de voz
        em que estiver.
        """

        await self.request(ctx, args)

    async def request(self, ctx, song):
        # get video source url using youtube_dl
        video_info = {}
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            videos = ydl.extract_info(song,
                                  download=False)

            video = videos['entries'][0]
            video_info['source_url'] = video['formats'][0]['url']
            video_info['title'] = video['title']
            yt_prefix = 'https://www.youtube.com/watch?v='
            video_info['youtube_url'] = yt_prefix + video['id']

        self.setlist.append(video_info)
        await ctx.send(f"adicionei: {video_info['youtube_url']}")
        if not ctx.guild.voice_client:
            # the bot does not have a VoiceClient on this guild
            voice_client = await self.get_voice_client(ctx)
            if not voice_client:
               await ctx.send('Você não está em nenhum chat de voz')
            else:
                self.play_next(ctx.guild)

    def play_next(self, guild):
        voice_client = guild.voice_client
        if not voice_client:
            print('weirdly, i have no voice_client but I should have')
            self.setlist.clear()
            return
        if len(self.setlist) == 0:
            # if the queue is empty, disconnect
            asyncio.run_coroutine_threadsafe(voice_client.disconnect(),
                                             self.bot.loop)
            return
        
        # get an AudioSource from next song in setlist
        next_song_info = self.setlist.popleft()
        audio_source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(next_song_info['source_url'],
                                   before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))
        print('starting to play', next_song_info)
        print('song queue:', self.setlist)

        voice_client.play(audio_source,
                          after=lambda _: self.play_next(guild))

    def is_playing_guild(self, guild):
        if guild.voice_client:
            return guild.voice_client.is_playing()
        else:
            return False
            
    async def get_voice_client(self, ctx):
        if ctx.author.voice.channel:
            return await ctx.author.voice.channel.connect()
