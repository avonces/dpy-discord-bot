# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands, bridge
import requests
from datetime import datetime


# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
class Meme(commands.Cog, name='Meme', description='contains meme command'):
    """cog for meme command"""
    def __init__(self, client):
        self.client = client

        self.request_session = requests.Session()

    @bridge.bridge_command(name='meme', description='sends a random meme')
    async def meme(self, ctx: bridge.BridgeContext):
        """sends a random meme"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        # do request
        request_url = f'https://apis.duncte123.me/meme'
        headers = {'User-Agent': str(self.client.user)}
        data = self.request_session.get(request_url, headers=headers).json()

        # if request succeeded, send embed with image
        if data['success']:
            meme_url = data['data']['url']
            title = data['data']['title']
            body = data['data']['body']
            image_url = data['data']['image']

            embed = discord.Embed(title=title,
                                  url=meme_url,
                                  description=body,
                                  color=embedColor)
            embed.set_image(url=image_url)

        else:
            embed = discord.Embed(title='Meme',
                                  description='Unfortunately, an api error occurred.',
                                  color=embedColor)

        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.respond(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Meme(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
