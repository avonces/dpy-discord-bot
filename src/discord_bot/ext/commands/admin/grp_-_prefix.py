# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands
import sqlite3
import ast
from datetime import datetime

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()

defaultPrefixes = ast.literal_eval(os.getenv("DEFAULT_PREFIXES"))
embedColor = int(os.getenv('EMBED_COLOR'))


# extension
class Prefix(commands.Cog, name='Prefix', description='contains prefix command group'):
    """cog for custom prefix command group"""
    def __init__(self, client):
        self.client = client

    @commands.group(name='prefix', description='command group containing prefix-related commands')
    async def prefix(self, ctx):
        """creates command group "prefix" for using subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @prefix.command(name='get', description='gets berb-bot prefixes for the current server and prints them out')
    @commands.guild_only()
    async def get(self, ctx):
        """gets prefix entries for a certain guild and prints it out"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # get bot prefixes for embed
        complete_prefix_list = self.client.command_prefix(self.client, ctx.message)
        prefix_string = '`' + '`\n`'.join(complete_prefix_list) + '`'

        # create and send embed
        embed = discord.Embed(title='Prefixes',
                              description='All valid Berb-Bot prefixes for this discord server\n',
                              color=embedColor)
        embed.add_field(name='Berb-Bot Prefixes:',
                        value=prefix_string,
                        inline=False)
        embed.set_author(name=f'Requested by: {ctx.message.author}',
                         icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.send(embed=embed)

    @prefix.command(name='set', description='sets custom berb-bot prefixes for the current discord server')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set(self, ctx, *, prefixes_seperated_by_spaces):
        """sets custom prefixes for certain guild"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # needed data
        guild_id = ctx.guild.id
        prefix_list = prefixes_seperated_by_spaces.split(' ')

        # connect to "databank.db" and create cursor
        connection = sqlite3.connect('../../data/databank.db')
        cursor = connection.cursor()

        # delete existing prefix assignments
        sql_command_query = f"""DELETE FROM prefix_assignment WHERE guild_id = {guild_id}"""
        cursor.execute(sql_command_query)

        # make a new entry for every prefix with the corresponding guild id
        for prefix in prefix_list:
            sql_command_query = f"""INSERT INTO prefix_assignment(guild_id, guild_prefix) 
            VALUES({guild_id}, "{prefix}"); """
            cursor.execute(sql_command_query)

        # commit changes and close connection
        cursor.close()

        connection.commit()
        connection.close()

        # get bot prefixes for embed
        complete_prefix_list = self.client.command_prefix(self.client, ctx.message)
        prefix_string = '`' + '`\n`'.join(complete_prefix_list) + '`'

        # create and send embed
        embed = discord.Embed(title='New Prefixes',
                              description='The Berb-Bot prefixes for this discord server have changed!\n',
                              color=embedColor)
        embed.add_field(name='New Berb-Bot Prefixes:',
                        value=prefix_string,
                        inline=False)
        embed.set_author(name=f'Requested by: {ctx.message.author}',
                         icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.send(embed=embed)

    @prefix.command(name='reset', description='deletes any custom berb-bot prefixes for the current discord server')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset(self, ctx):
        """deletes prefix entries for a certain guild"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # needed data
        guild_id = ctx.guild.id

        # connect to "databank.db" and create cursor
        connection = sqlite3.connect('../../data/databank.db')
        cursor = connection.cursor()

        # delete existing prefix assignments
        sql_command_query = f"""DELETE FROM prefix_assignment WHERE guild_id = {guild_id}"""
        cursor.execute(sql_command_query)

        # commit changes and close connection
        cursor.close()

        connection.commit()
        connection.close()

        # get bot prefixes for embed
        complete_prefix_list = self.client.command_prefix(self.client, ctx.message)
        prefix_string = '`' + '`\n`'.join(complete_prefix_list) + '`'

        # create and send embed
        embed = discord.Embed(title='New Prefixes',
                              description='The Berb-Bot prefixes for this discord server have changed! '
                                          'They were reset!\n',
                              color=embedColor)
        embed.add_field(name='Default Berb-Bot Prefixes:',
                        value=prefix_string,
                        inline=False)
        embed.set_author(name=f'Requested by: {ctx.message.author}',
                         icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.send(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Prefix(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
