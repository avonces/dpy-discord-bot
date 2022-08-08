# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands
from datetime import datetime, timedelta


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

    @commands.command(name='timeout', aliases=['mute'], description='timeouts/ mutes a server member')
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def timeout(self, ctx, member: discord.Member, days: int = 0, hours: int = 0, minutes: int = 15,
                      seconds: int = 0, *, reason):
        """timeouts a server member"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        async with ctx.typing():
            if member.id == ctx.author.id:
                embed = discord.Embed(title='Failed',
                                      description='You cannot timeout yourself.',
                                      color=embedColor)
            elif member.top_role >= ctx.author.top_role:
                embed = discord.Embed(title='Failed',
                                      description='You can only moderate members that are blow you in the server '
                                                  'hierarchy.',
                                      color=embedColor)
            else:
                duration = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

                await member.timeout_for(duration=duration, reason=reason)

                embed = discord.Embed(title='Timeouted',
                                      description=f'{str(member)} has successfully been timed out for '
                                                  f'{days} days, {hours} hours, {minutes} minutes, {seconds} seconds!'
                                                  f'Reason: \n```{reason}```',
                                      color=embedColor)

            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='kick', description='kicks a server member')
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason):
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
                                                  f'Reason: \n```{reason}```',
                                      color=embedColor)

            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='ban', description='bans a server member')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason):
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
                                                  f'Reason: \n```{reason}```',
                                      color=embedColor)

            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='unban', description='unbans a server member')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: discord.Member, *, reason):
        """unbans a server member"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        async with ctx.typing():
            await ctx.guild.unban(member, reason)

            embed = discord.Embed(title='Unbanned',
                                  description=f'{str(member)} has successfully been unbanned from this discord server!'
                                              f'Reason: \n```{reason}```',
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
