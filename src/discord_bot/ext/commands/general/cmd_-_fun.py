# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands, bridge
import random
from datetime import datetime


# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
def get_list_from_file(path_to_file):
    with open(path_to_file, 'r') as read_file:
        data = read_file.read()
        data_list = data.split('\n')
        read_file.close()

        return data_list


class Entertainment(commands.Cog, name='Entertainment',
                    description='contains commands that could possibly make you less bored'):
    """cog for entertainment commands"""
    def __init__(self, client):
        self.client = client

        self.topic_list = get_list_from_file('../../data/lists/list-topic.txt')

    @bridge.bridge_command(name='topic', description='totally not a reference to the Kurzgesagt discord')
    async def topic(self, ctx: bridge.BridgeContext):
        """sends a random, very accurate and totally not offensice topic"""
        topic = random.choice(self.topic_list)
        await ctx.respond(topic)

    @bridge.bridge_command(name='roll', description='roll a dice')
    async def roll(self, ctx: bridge.BridgeContext, sides: int = 6):
        """sends a random, very accurate and totally not offensice topic"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # determine number
        number = random.randint(1, sides)

        # send embed
        embed = discord.Embed(title='Rolled',
                              description=f'{ctx.message.author.mention} rolled a dice with {sides} sides.',
                              color=embedColor)
        embed.add_field(name='Number',
                        value=f'||`-{number}-`||',
                        inline=False)
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')
        await ctx.respond(embed=embed)

    @bridge.bridge_command(name='coinflip', description='just like flipping a coin, but digital')
    async def coinflip(self, ctx: bridge.BridgeContext):
        """""flips" a coin"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # determine side
        number = random.randint(0, 1)
        side = ''

        if number:
            side = 'Heads'
        else:
            side = 'Tails'

        # send embed
        embed = discord.Embed(title='Flipped',
                              description=f'{ctx.message.author.mention} flipped a coin.',
                              color=embedColor)
        embed.add_field(name='Side',
                        value=f'||`{side}`||',
                        inline=False)
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')
        await ctx.respond(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Entertainment(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
