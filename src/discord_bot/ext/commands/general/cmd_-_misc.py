# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands, bridge
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

        return data_list


class Misc(commands.Cog, name='Miscellaneous', description='contains a variety of a many kinds of commands'):
    """cog for miscellaneous commands"""
    def __init__(self, client):
        self.client = client

        self.topic_list = get_list_from_file('../../data/lists/list-topic.txt')

    # file command
    @bridge.bridge_command(name='sendfile', description='sends a local file using the given path')
    @commands.is_owner()
    async def sendfile(self, ctx: bridge.BridgeContext, path_to_file: str):
        """sends a local file using the given path"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        # get file
        filename = os.path.basename(path_to_file)
        file = discord.File(f'../../data/{path_to_file}', filename=filename)

        # create and send embed
        embed = discord.Embed(title='File',
                              description=filename,
                              color=embedColor)
        embed.set_image(url=f'attachment://{filename}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.respond(file=file, embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Misc(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
