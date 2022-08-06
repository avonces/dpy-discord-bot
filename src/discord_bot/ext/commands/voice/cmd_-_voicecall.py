# imports
import os
import logging
import dotenv
from discord.ext import commands
import asyncio

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = os.getenv('EMBED_COLOR')


# extension
class VoiceCall(commands.Cog, name='VoiceCall',
                description='contains commands for managing the bot regarding voice calls'):
    """cog for voice call commands"""
    def __init__(self, client):
        self.client = client

    @commands.group(name='vc', aliases=['voice_call', 'voicecall'],
                    description='command group containing commands for managing the bot regarding voice calls')
    async def vc(self, ctx):
        """command group containing commands for managing the bot regarding voice calls"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @vc.command(name='join', aliases=['connect'],
                description='makes the bot join the voice channel that the author is currently connected to')
    async def join(self, ctx):
        """makes the bot join the voice channel that the author is currently connected to"""
        if ctx.author.voice and ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(f'{ctx.author.mention}, I am already connected to a voice channel.')
        else:
            await ctx.send(f'{ctx.author.mention}, you are not connected to a voice channel.')

    @vc.command(name='leave', aliases=['disconnect'],
                description='makes the bot leave any voice channel it is connected to')
    async def leave(self, ctx):
        """makes the bot leave any voice channel it is connected to"""
        if ctx.guild.voice_client:
            if ctx.guild.voice_client.is_connected():
                if ctx.author.voice.channel == ctx.guild.voice_client.channel:
                    await ctx.guild.voice_client.disconnect()
                else:
                    await ctx.send(f'{ctx.author.mention}, you need to be in the same voice channel as me '
                                   'to make me leave.')
            else:
                await ctx.send(f'{ctx.author.mention}, I am not connected to a voice channel.')
        else:
            await ctx.send(f'{ctx.author.mention}, I am not connected to a voice channel.')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(VoiceCall(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
