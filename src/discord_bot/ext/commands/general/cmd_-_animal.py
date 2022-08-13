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
class Animal(commands.Cog, name='Animal', description='contains animal command'):
    """cog for animal command"""
    def __init__(self, client):
        self.client = client

        self.request_session = requests.Session()

    @bridge.bridge_command(name='animal', description='sends a random picture of a given animal type')
    async def animal(self, ctx: bridge.BridgeContext, animal_type: str):
        """sends a random picture of a given animal type"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        valid_animal_types = ['alpaca',
                              'bird',
                              'camel',
                              'cat',
                              'discord-monster',
                              'dog',
                              'duck',
                              'fox',
                              'lizard',
                              'llama',
                              'panda',
                              'seal',
                              'wolf']

        if animal_type in valid_animal_types:
            # do request
            request_url = f'https://apis.duncte123.me/animal/{animal_type}'
            headers = {'User-Agent': str(self.client.user)}
            data = self.request_session.get(request_url, headers=headers).json()

            # if request succeeded, send embed with image
            if data['success']:
                animal_type_capitalized = animal_type.capitalize()
                image_url = data['data']['file']

                embed = discord.Embed(title=animal_type_capitalized,
                                      color=embedColor)
                embed.set_image(url=image_url)

            else:
                embed = discord.Embed(title='Animal',
                                      description='Unfortunately, an API-Error occurred.',
                                      color=embedColor)

        else:
            embed = discord.Embed(title='Animal',
                                  description='Please enter a valid animal type!',
                                  color=embedColor)
            embed.add_field(name='Valid Animal Types',
                            value='alpaca, bird, camel, cat, discord-monster, dog, duck, fox, lizard, llama, '
                                  'panda, seal, wolf',
                            inline=False)

        # configure and send embed
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.respond(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Animal(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
