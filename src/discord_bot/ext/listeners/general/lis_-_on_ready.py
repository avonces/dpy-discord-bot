# imports
import os
import logging
import discord
from discord.ext import commands

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# extension
class OnReadyListener(commands.Cog, name='On Ready Listener', description='contains the on_ready listener'):
    """cog for on_ready event"""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """custom on_ready event"""
        # change the status of the bot
        await self.client.change_presence(activity=discord.Streaming(
            platform='twitch', url='https://twitch.tv/avoncess',
            name='.help'))

        # send a message when the bot was initialized successfully
        logging.info('\n------\n'
                     'The Bot is now up and running!\n'
                     '...\n'
                     'Logged in as: \n'
                     f'>>> Name:  {str(self.client.user)}\n'
                     f'>>> ID:    {self.client.user.id}'
                     '\n------\n')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(OnReadyListener(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
