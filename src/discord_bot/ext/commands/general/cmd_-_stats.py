# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands, bridge
import sqlite3
from datetime import datetime

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
class Statistics(commands.Cog, name='Statistics', description='contains statistic-related commands'):
    """cog for statistic-related commands"""
    def __init__(self, client):
        self.client = client

    @bridge.bridge_command(name='user_stats', aliases=['userstats'], description='sends the most important user '
                                                                                 'statistics for a given discord user '
                                                                                 'on this server')
    async def user_stats(self, ctx: bridge.BridgeContext, member: discord.Member):
        """sends user statistics for a given user"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        guild_id = ctx.guild.id
        user_id = member.id

        # get message count for user
        # connect to "databank.db" and create cursor
        connection = sqlite3.connect('../../data/databank.db')
        cursor = connection.cursor()

        # get needed information
        sql_command_query = f"""SELECT * FROM message_counter WHERE guild_id = {guild_id} AND user_id = {user_id}"""
        cursor.execute(sql_command_query)
        rows = cursor.fetchall()

        # close connection
        cursor.close()
        connection.close()

        # if there is an entry, get the message_count for the server member, otherwise it will be 0
        member_message_count = 0

        if rows:
            # there is an entry
            row = rows[0]
            member_message_count = row[2]

        # create embed
        embed = discord.Embed(title='User Statistics',
                              description=f'Overall discord user statistics for **{member.name}**\n',
                              color=embedColor)
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        # add content
        embed.add_field(name='Joined', value=f'Account Creation: \n`{member.created_at}`\n'
                                             f'Joined This Server At: \n`{member.joined_at}`',
                        inline=False)
        embed.add_field(name='Name', value=f'Mention: {member.mention}\n'
                                           f'Name: `{member}`\n'
                                           f'Nickname: `{member.nick}`',
                        inline=False)
        embed.add_field(name='ID', value=f'ID: `{member.id}`',
                        inline=False)
        embed.add_field(name='Activity/ Role', value=f'Activity: `{member.activities}`\n'
                                                     f'Top Role: `{member.top_role}`',
                        inline=False)
        embed.add_field(name='Discord', value=f'Represents Discord Officially: `{member.public_flags.system}`\n'
                                              f'Discord Partner: `{member.public_flags.partner}`\n'
                                              f'Discord Staff: `{member.public_flags.staff}`\n'
                                              f'Discord Bug Hunter: `{member.public_flags.bug_hunter}`\n'
                                              f'Discord Bug Hunter Level 2: `{member.public_flags.bug_hunter_level_2}`',
                        inline=False)
        embed.add_field(name='Bot', value=f'Bot: `{member.bot}`\n'
                                          f'Verified Bot: `{member.public_flags.verified_bot}`\n'
                                          f'Early Verified Bot Developer: '
                                          f'`{member.public_flags.early_verified_bot_developer}`',
                        inline=True)
        embed.add_field(name='Hypesquad', value=f'Hypesquad: `{member.public_flags.hypesquad}`\n'
                                                f'Hypesquad Bravery: `{member.public_flags.hypesquad_bravery}`\n'
                                                f'Hypesquad Brilliance: `{member.public_flags.hypesquad_brilliance}`\n'
                                                f'Hypesquad Balance: `{member.public_flags.hypesquad_balance}`',
                        inline=False)
        embed.add_field(name='Misc', value=f'Administrator Permission: `{member.guild_permissions.administrator}`\n'
                                           f'Nitro/ Premium: `{member.premium_since}`\n'
                                           f'Early Supporter: `{member.public_flags.early_supporter}`\n'
                                           f'Team User: `{member.public_flags.team_user}`',
                        inline=False)
        embed.add_field(name='Berb-Bot', value=f'Messages sent on this server: {member_message_count}',
                        inline=False)

        # send embed
        await ctx.respond(embed=embed)

    @bridge.bridge_command(name='server_stats', aliases=['serverstats'], description='sends the most important server '
                                                                                     'statistics for a this discord '
                                                                                     'server')
    @commands.guild_only()
    async def server_stats(self, ctx: bridge.BridgeContext):
        """sends user statistics for a given user"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.defer()

        # create embed
        embed = discord.Embed(title='Server Statistics',
                              description=f'Overall server statistics for **{ctx.guild.name}**\n',
                              color=embedColor)
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        # add content
        embed.add_field(name='Created at',
                        value=f'The server was created at `{ctx.guild.created_at}`.',
                        inline=True)
        embed.add_field(name='Server Owner',
                        value=f'The server owner is `{ctx.guild.owner}`.',
                        inline=True)
        embed.add_field(name='Server Region',
                        value=f'The server is located in `{ctx.guild.region}`.',
                        inline=True)
        embed.add_field(name='Server ID',
                        value=f'The servers id is: `{ctx.guild.id}`',
                        inline=True)
        embed.add_field(name='Users:',
                        value=f'There are `{ctx.guild.member_count}` members on this server.',
                        inline=True)
        embed.add_field(name='Channels:',
                        value=f' There are `{len(ctx.guild.channels)}` channels on this server.',
                        inline=True)

        # send embed
        await ctx.respond(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Statistics(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
