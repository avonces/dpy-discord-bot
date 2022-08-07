# imports
import os
import logging
import dotenv
import asyncio
import discord
from discord.ext import commands
from datetime import datetime

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
class Guild(commands.Cog, name='Guild', description='contains guild command group'):
    """cog for bot management command group, test commands"""
    def __init__(self, client):
        self.client = client

    @commands.group(name='guild', description='command group containing guild-related commands')
    @commands.has_permissions(kick_members=True)
    async def guild(self, ctx):
        """creates a command group "dev" for using subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @guild.command(name='leave_current', aliases=['leavecurrent'],
                   description='makes the bot leave the guild which the command is send in')
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def leave_current(self, ctx):
        """makes the bot leave the guild which the command is sent in"""
        await ctx.send('**Leaving** this guild...')

        await self.client.leave_guild(ctx.guild)

    @guild.command(name='leave_by_id', aliases=['leavebyid'],
                   description='makes the bot leave the guild with the give id')
    @commands.is_owner()
    async def leave_by_id(self, ctx, guild_id: int):
        """makes the bot leave the guild with the give id"""
        try:
            guild = self.client.fetch_guild(guild_id=guild_id)

            if guild is None:
                await ctx.send('I do not recognize that guild.')
                return

            await self.client.leave_guild(guild)
            await ctx.send(f'Left guild: **{guild.name}** ({guild.id})')

        except Exception as e:
            logger.exception(e)
            await ctx.send('I do not recognize that guild.')

    @guild.command(name='leave_by_name', aliases=['leavebyname'],
                   description='makes the bot leave the guild with the given name')
    @commands.is_owner()
    async def leave_by_name(self, ctx, *, guild_name):
        """makes the bot leave the guild with the given name"""
        guild = discord.utils.get(self.client.guilds, name=str(guild_name))

        if guild is None:
            await ctx.send('I do not recognize that guild.')
            return

        await self.client.leave_guild(guild)
        await ctx.send(f'Left guild: **{guild.name}** ({guild.id})')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Guild(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
