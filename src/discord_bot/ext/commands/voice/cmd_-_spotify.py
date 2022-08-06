# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = os.getenv('EMBED_COLOR')


# extension
class Music(commands.Cog, name='Music', description='contains commands for playing music in a voice channel'):
    """cog for music commands"""
    def __init__(self, client):
        self.client = client

    @commands.command(name='preset', aliases=['placeholder'], description='sits around')
    async def preset(self, ctx):
        """preset"""
        async with ctx.typing():
            pass

        await ctx.send('preset')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Music(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
