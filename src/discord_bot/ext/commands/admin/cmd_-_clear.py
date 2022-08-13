# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands, bridge
import asyncio
from datetime import datetime


# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
class Clear(commands.Cog, name='Clear', description='contains clear command'):
    """cog for clear command"""
    def __init__(self, client):
        self.client = client

    @bridge.bridge_command(name='clear', description='deletes a certain amount of messages')
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: bridge.BridgeContext, amount: str = '10', channel: discord.TextChannel = None):
        """deletes a certain amount of messages"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        # clear all messages
        if amount == 'all':
            # clear
            channel = channel or ctx.channel
            count = 0
            async for _ in channel.history(limit=None):
                count += 1
            amount = str(count)
            await ctx.channel.purge(limit=int(amount))
            await asyncio.sleep(1)

            # send embed
            embed = discord.Embed(title='Cleared!',
                                  description=f'All messages in channel `{channel}` were deleted (`{amount}` '
                                              f'messages).',
                                  color=embedColor)

        # clear the given amount of messages
        else:
            # clear
            await ctx.channel.purge(limit=int(amount) + 1)
            await asyncio.sleep(1)

            # send embed
            if int(amount) == 1:
                embed = discord.Embed(title='Cleared!',
                                      description='Cleared the message.',
                                      color=embedColor)
            else:
                embed = discord.Embed(title='Cleared!',
                                      description=f'Cleared `{amount}` messages.',
                                      color=embedColor)

        embed.set_footer(text=f'BerbBot - {formatted_time}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.respond(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Clear(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
