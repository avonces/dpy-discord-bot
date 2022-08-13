# imports
import os
import logging
import dotenv
import discord
from datetime import datetime
from discord.ext import commands, bridge
from discord.commands import Option
from youtube_dl import YoutubeDL

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
class Music(commands.Cog, name='Music', description='contains commands for playing music in a voice channel'):
    """cog for music commands"""
    def __init__(self, client):
        self.client = client

        self.voice_client = None

        self.music_queue = []    # [[{'source': url, 'title': title}, channel], ...]
        self.volume = 1.0    # floating point percentage

        self.valid_file_types = [
            '.mp3',
            '.wav'
        ]

        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': 'True'
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    def search_yt(self, query):
        """searches YouTube for a query and returns playback url and title if successful, else False"""
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info('ytsearch:%s' % query, download=False)['entries'][0]
                return {'source': info['formats'][0]['url'], 'title': info['title']}

            except Exception as e:
                logger.exception(e)
                return False

    def play_next(self):
        """plays the next song in the queue; if no songs are queued, nothing will be played"""
        if self.music_queue:
            # get the first item (url) in the queue
            source = self.music_queue[0][0]['source']
            # then remove it from the queue, so it won't be played forever
            self.music_queue.pop(0)

            if self.voice_client.is_connected():    # only try playing if the voice client is connected (recursion)

                # do not try to reconnect to a stream when playing local files
                if source.startswith('http://') or source.startswith('https://'):
                    self.voice_client.play(
                        discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS),
                            self.volume
                        ),
                        after=lambda e: self.play_next()    # recursion using lambda
                    )

                else:
                    self.voice_client.play(
                        discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio(source),
                            self.volume
                        ),
                        after=lambda e: self.play_next()    # recursion using lambda
                    )

    async def play_music(self, ctx):
        """"""
        if self.music_queue:
            # get the first item (url) in the queue
            source = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await self.music_queue[0][1].connect()
                # can not connect
                if not self.voice_client:
                    await ctx.respond(f'{ctx.author.mention}, I was not able to connect to the given voice channel.\n'
                                      f'(Voice Channel: `{self.music_queue[0][1]}`)')
                    return

            else:
                await self.voice_client.move_to(self.music_queue[0][1])

            # then remove the first item (url) in the queue, so it won't be played forever
            self.music_queue.pop(0)

            # do not try to reconnect to a stream when playing local files
            if source.startswith('http://') or source.startswith('https://'):
                self.voice_client.play(
                    discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS),
                        self.volume
                    ),
                    after=lambda e: self.play_next()
                )

            else:
                self.voice_client.play(
                    discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(source),
                        self.volume
                    ),
                    after=lambda e: self.play_next()
                )

    # ------
    # play_local
    # ------

    @bridge.bridge_command(name='play_local', help='appends a local audio file to the queue and starts playing')
    @commands.guild_only()
    @commands.is_owner()
    async def play_local(self, ctx: bridge.BridgeContext, *, path_to_audio_file: str):
        if not ctx.author.voice.channel:
            # you need to be connected so that the bot knows where to go
            await ctx.respond(
                f'{ctx.author.mention}, you need to be connected to a voice channel, to use this command!')

        else:
            if os.path.exists(path_to_audio_file) and os.path.splitext(path_to_audio_file)[-1] in self.valid_file_types:
                song = {'source': path_to_audio_file, 'title': os.path.basename(path_to_audio_file)}

                self.music_queue.append([song, ctx.author.voice.channel])
                await ctx.respond(f'Appended to the queue: **{song["title"]}**')

                if self.voice_client:
                    if self.voice_client.is_paused():
                        # resume if paused
                        await self.resume(ctx)
                    elif self.voice_client.is_playing():
                        pass

                    else:
                        await self.play_music(ctx)
                else:
                    await self.play_music(ctx)

            else:
                await ctx.respond(f'{ctx.author.mention}, I was not able to find a valid audio file '
                                  'in the given location.')

    # ------
    # play, resume, pause, stop
    # ------

    @bridge.bridge_command(name='play', help='appends the soundtrack of a youtube video to the queue and starts playing'
                           )
    @commands.guild_only()
    async def play(self, ctx: bridge.BridgeContext, *, query: str):
        if not ctx.author.voice.channel:
            # you need to be connected so that the bot knows where to go
            await ctx.respond(f'{ctx.author.mention}, you need to be connected to a voice channel, to use this command!'
                              )

        else:
            song = self.search_yt(query)

            if song:
                self.music_queue.append([song, ctx.author.voice.channel])
                await ctx.respond(f'Appended to the queue: **{song["title"]}**')

                if self.voice_client:
                    if self.voice_client.is_paused():
                        # resume if paused
                        await self.resume(ctx)
                    elif self.voice_client.is_playing():
                        pass

                    else:
                        await self.play_music(ctx)
                else:
                    await self.play_music(ctx)

            else:
                await ctx.respond(f'{ctx.author.mention}, I was not able to find a YouTube video corresponding to '
                                  'the given search query. Maybe it is a livestream or playlist. I can not play those.')

    @bridge.bridge_command(name='resume', help='if the bot has been paused, start playing from where it did')
    @commands.guild_only()
    async def resume(self, ctx: bridge.BridgeContext):
        if self.voice_client:
            if self.voice_client.is_paused():
                self.voice_client.resume()

    @bridge.bridge_command(name='pause', help='if the bot is currently playing, pause it')
    @commands.guild_only()
    async def pause(self, ctx: bridge.BridgeContext):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.pause()

    @bridge.bridge_command(name='stop', help='make the bot stop playing any music, '
                                             'clear the queue and leave the voice channel')
    @commands.guild_only()
    async def stop(self, ctx: bridge.BridgeContext):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.stop()

        self.music_queue = []

        await self.voice_client.disconnect()

    # ------
    # queue, skip, clear_queue, display_queue
    # ------

    @bridge.bridge_command(name='queue', help='appends the soundtrack of a youtube video to the queue')
    @commands.guild_only()
    async def queue(self, ctx: bridge.BridgeContext, *, query: str):
        if not ctx.author.voice.channel:
            # you need to be connected so that the bot knows where to go
            await ctx.respond(f'{ctx.author.mention}, you need to be connected to a voice channel, to use this command!')

        else:
            song = self.search_yt(query)

            if isinstance(song, bool):
                await ctx.respond(f'{ctx.author.mention}, I was not able to find a YouTube video corresponding to '
                                  'the given search query. Maybe it is a livestream or playlist. I can not play those.')

            else:
                self.music_queue.append([song, ctx.author.voice.channel])
                await ctx.respond(f'Appended to the queue: **{song["title"]}**')

    @bridge.bridge_command(name='skip', help='Skips the current song being played')
    @commands.guild_only()
    async def skip(self, ctx: bridge.BridgeContext):
        if self.voice_client:
            self.voice_client.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @bridge.bridge_command(name='clear_queue', aliases=['clearqueue'], help='clears the queue')
    @commands.guild_only()
    async def clear_queue(self, ctx: bridge.BridgeContext):
        self.music_queue = []

        await ctx.respond('The queue has been cleared.')

    @bridge.bridge_command(name='display_queue', aliases=['displayqueue'],
                           help='displays up to 10 songs that will be played next')
    @commands.guild_only()
    async def display_queue(self, ctx: bridge.BridgeContext):
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        queued_songs = []

        for i in range(len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if i >= 9:
                if len(self.music_queue) > 10:
                    queued_songs.append('...')
                break

            queued_songs.append(self.music_queue[i][0]['title'])

        if queued_songs:
            queue_string = ", \n".join(queued_songs)
            embed = discord.Embed(title='Queue',
                                  description=f'The `{len(queued_songs)}` '
                                              f'{"song" if len(queued_songs) == 1 else "songs"} that will be '
                                              'played next.',
                                  color=embedColor)
            embed.add_field(name='About to be played: ', value=queue_string, inline=False)

        else:
            embed = discord.Embed(title='Queue',
                                  description='The **queue** is **empty**.',
                                  color=embedColor)

        embed.set_footer(text=f'BerbBot - {formatted_time}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.respond(embed=embed)

    # ------
    # volume
    # ------

    @bridge.bridge_command(name='volume', help='changes the audio sources volume')
    @commands.guild_only()
    async def volume(self, ctx: bridge.BridgeContext, new_volume: int):
        """changes the audio sources volume"""
        if self.voice_client:
            if self.voice_client.source:
                if 0 <= new_volume <= 100:
                    new_volume_float = new_volume / 100

                    self.volume = new_volume_float
                    self.voice_client.source.volume = new_volume_float

                    await ctx.respond(f'Set the volume to **{new_volume}%**.')

                else:
                    await ctx.respond('Please enter a volume between 0 and 100.')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Music(client))


def teardown(client):
    """respond information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
