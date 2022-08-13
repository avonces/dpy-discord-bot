# imports
import os
import logging
import discord
from discord.ext import commands, bridge

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# extension
class Spam(commands.Cog, name='Spam', description='contains commands for spamming users'):
    """cog for spam commands"""
    def __init__(self, client):
        self.client = client

    @bridge.bridge_command(name='spam_user', aliases=['spamuser'],
                           description='spams a given user with a given amount of a given message')
    @commands.is_owner()
    async def spam_user(self, ctx: bridge.BridgeContext, member: discord.Member, amount: int = 5, *, message: str):
        """spams a given user with a given amount of a given message"""
        async with member.typing():
            for i in range(0, amount):
                await member.send(message)

        await ctx.respond(f'Successfully spammed {member.mention} `{amount}` times with your message.')

    @bridge.bridge_command(name='spam_channel', aliases=['spamchannel'],
                           description='spams a given message a given amount in the current channel')
    @commands.is_owner()
    async def spam_channel(self, ctx: bridge.BridgeContext, amount: int = 5, *, message: str):
        """spams a given user with a given amount of a given message"""
        await ctx.defer()

        for i in range(0, amount):
            await ctx.send(message)

        await ctx.respond(f'Successfully spammed {ctx.channel.mention} `{amount}` times with your message.')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Spam(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
