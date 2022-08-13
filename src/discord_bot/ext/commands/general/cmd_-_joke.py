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
class Joke(commands.Cog, name='Joke', description='contains joke command'):
    """cog for joke command"""
    def __init__(self, client):
        self.client = client

        self.request_session = requests.Session()

    # @commands.command(name='joke', description='sends a random joke')
    @bridge.bridge_command(name='joke', description='sends a random joke')
    async def joke(self, ctx: bridge.BridgeContext):
        """sends a random joke"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        # do request
        request_url = 'https://apis.duncte123.me/joke'
        headers = {'User-Agent': str(self.client.user)}
        data = self.request_session.get(request_url, headers=headers).json()

        # if request succeeded, send embed with image
        if data['success']:
            joke_url = data['data']['url']
            title = data['data']['title']
            body = data['data']['body']

            embed = discord.Embed(title='Joke',
                                  url=joke_url,
                                  color=embedColor)
            embed.add_field(name=f'------\n'
                                 f'{title}',
                            value=f'------\n'
                                  f'{body}',
                            inline=False)

        else:
            embed = discord.Embed(title='Joke',
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
    client.add_cog(Joke(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
