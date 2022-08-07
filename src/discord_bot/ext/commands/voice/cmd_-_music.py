# imports
import os
import logging
import dotenv
import discord
from datetime import datetime
from discord.ext import commands
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

        self.YDL_OPTIONS = {
            'format': 'bestaudio',
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
            url = self.music_queue[0][0]['source']
            # then remove it from the queue, so it won't be played forever
            self.music_queue.pop(0)

            if self.voice_client.is_connected():    # only try playing if the voice client is connected (recursion)
                self.voice_client.play(
                    discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS),
                    after=lambda e: self.play_next()  # recursion using lambda
                )

    async def play_music(self, ctx):
        """"""
        if self.music_queue:
            # get the first item (url) in the queue
            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await self.music_queue[0][1].connect()
                # can not connect
                if not self.voice_client:
                    await ctx.send(f'{ctx.author.mention}, I was not able to connect to the given voice channel.\n'
                                   f'(Voice Channel: `{self.music_queue[0][1]}`)')
                    return

            else:
                await self.voice_client.move_to(self.music_queue[0][1])

            # then remove the first item (url) in the queue, so it won't be played forever
            self.music_queue.pop(0)
            self.voice_client.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next()    # recursion using lambda
            )

    # ------
    # play, resume, pause, stop
    # ------

    @commands.command(name='play', help='appends the soundtrack of a youtube video to the queue and starts playing')
    async def play(self, ctx, *, query):
        if not ctx.author.voice.channel:
            # you need to be connected so that the bot knows where to go
            await ctx.send(f'{ctx.author.mention}, you need to be connected to a voice channel, to use this command!')

        else:
            song = self.search_yt(query)

            if song:
                self.music_queue.append([song, ctx.author.voice.channel])
                await ctx.send(f'Appended to the queue: **{song["title"]}**')

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
                await ctx.send(f'{ctx.author.mention}, I was not able to find a YouTube video corresponding to '
                               'the given search query. Maybe it is a livestream or playlist. I can not play those.')

    @commands.command(name='resume', help='if the bot has been paused, start playing from where it did')
    async def resume(self, ctx):
        if self.voice_client:
            if self.voice_client.is_paused():
                self.voice_client.resume()

    @commands.command(name='pause', help='if the bot is currently playing, pause it')
    async def pause(self, ctx):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.pause()

    @commands.command(name='stop', help='make the bot stop playing any music, '
                                        'clear the queue and leave the voice channel')
    async def stop(self, ctx):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.stop()

        self.music_queue = []

        await self.voice_client.disconnect()

    # ------
    # queue, skip, clear_queue, display_queue
    # ------

    @commands.command(name='queue', help='appends the soundtrack of a youtube video to the queue')
    async def queue(self, ctx, *, query):
        if not ctx.author.voice.channel:
            # you need to be connected so that the bot knows where to go
            await ctx.send(f'{ctx.author.mention}, you need to be connected to a voice channel, to use this command!')

        else:
            song = self.search_yt(query)

            if isinstance(song, bool):
                await ctx.send(f'{ctx.author.mention}, I was not able to find a YouTube video corresponding to '
                               'the given search query. Maybe it is a livestream or playlist. I can not play those.')

            else:
                self.music_queue.append([song, ctx.author.voice.channel])
                await ctx.send(f'Appended to the queue: **{song["title"]}**')

    @commands.command(name='skip', help='Skips the current song being played')
    async def skip(self, ctx):
        if self.voice_client:
            self.voice_client.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(name='clear_queue', aliases=['clearqueue'], help='Stops the music and clears the queue')
    async def clear_queue(self, ctx):
        self.music_queue = []

        await ctx.send('The queue has been cleared.')

    @commands.command(name='display_queue', aliases=['displayqueue'],
                      help='displays up to 10 songs that will be played next')
    async def display_queue(self, ctx):
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
        embed.set_author(name=f'Requested by: {ctx.message.author}',
                         icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Music(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
