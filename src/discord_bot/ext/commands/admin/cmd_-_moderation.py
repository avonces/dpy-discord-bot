# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands
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
class Moderation(commands.Cog, name='Moderation', description='contains moderation-related commands'):
    """cog for moderation-related commands"""
    def __init__(self, client):
        self.client = client

    @commands.command(name='kick', description='kicks a server member')
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member, *, reason):
        """kicks a server member"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        async with ctx.typing():
            if member.id == ctx.author.id:
                embed = discord.Embed(title='Failed',
                                      description='You cannot kick yourself.',
                                      color=embedColor)
            elif member.top_role >= ctx.author.top_role:
                embed = discord.Embed(title='Failed',
                                      description='You can only moderate members that are blow you in the server '
                                                  'hierarchy.',
                                      color=embedColor)
            else:
                await member.kick(reason=reason)

                embed = discord.Embed(title='Kicked',
                                      description=f'{str(member)} has successfully been kicked from this discord server!'
                                                  f'Reason: ```{reason}```',
                                      color=embedColor)

            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='ban', description='bans a server member')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member, *, reason):
        """bans a server member"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        async with ctx.typing():
            if member.id == ctx.author.id:
                embed = discord.Embed(title='Failed',
                                      description='You cannot ban yourself.',
                                      color=embedColor)
            elif member.top_role >= ctx.author.top_role:
                embed = discord.Embed(title='Failed',
                                      description='You can only moderate members that are blow you in the server '
                                                  'hierarchy.',
                                      color=embedColor)
            else:
                await member.ban(reason=reason)

                embed = discord.Embed(title='Banned',
                                      description=f'{str(member)} has successfully been banned from this discord server!'
                                                  f'Reason: ```{reason}```',
                                      color=embedColor)

            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='unban', description='unbans a server member')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member, *, reason):
        """unbans a server member"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        async with ctx.typing():
            await ctx.guild.unban(member, reason)

            embed = discord.Embed(title='Unbanned',
                                  description=f'{str(member)} has successfully been unbanned from this discord server!'
                                              f'Reason: ```{reason}```',
                                  color=embedColor)
            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Moderation(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
