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
class Development(commands.Cog, name='Development', description='contains development command group and test commands'):
    """cog for bot management command group, test commands"""
    def __init__(self, client):
        self.client = client

    @commands.group(name='dev', description='command group containing development-related commands')
    @commands.is_owner()
    async def dev(self, ctx):
        """creates a command group "dev" for using subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @dev.command(name='shutdown', description='shuts down the bot')
    @commands.is_owner()
    async def shutdown(self, ctx):
        """shuts down the bot"""
        # send info/ embed
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        logger.info('shutting down...')

        embed = discord.Embed(title=f'Shutting down!',
                              description=f'`{self.client.user.display_name}` is being shut down!',
                              color=discord.Color.dark_gold())
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.send(embed=embed)

        # shut down client
        await ctx.bot.close()

    @dev.command(name='listext', description='sends a list of all available extensions')
    @commands.is_owner()
    async def listext(self, ctx):
        """sends a list of all available extensions (.py files in the /ext directory)"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # design embed
        embed = discord.Embed(title='Extensions',
                              description='a list of all available extensions (.py files in the /ext directory)\n',
                              color=embedColor)
        embed.set_author(name=f'Requested by: {ctx.message.author}',
                         icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        # add content
        extension_list = []

        for filename in os.listdir('./ext'):
            if filename.endswith('.py'):
                extension_list.append(filename)

        extensions = '\n'.join(extension_list)

        embed.add_field(name='Available Extensions:',
                        value=extensions,
                        inline=False)

        await ctx.send(embed=embed)

    @dev.command(name='reloadext', description='reloads an extension.py')
    @commands.is_owner()
    async def reloadext(self, ctx, extension_name):
        """reloads an extension.py"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        try:
            # unload extension and load it again
            self.client.unload_extension(f'ext.{extension_name[:-3]}')
            self.client.load_extension(f'ext.{extension_name[:-3]}')
            logger.info(f'successfully reloaded extension <{extension_name}>')

            # send embed
            embed = discord.Embed(title=f'Reloaded',
                                  description=f'`{extension_name}` has been reloaded successfully!',
                                  color=embedColor)
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

            await ctx.send(embed=embed)

        except Exception as error:
            # send error message/ embed
            logger.critical(f'failed reloading extension <{extension_name}>')
            logger.error(f'error: "{error}"')

            embed = discord.Embed(title='Failed',
                                  description=f'The extension `{extension_name}` was not reloaded successfully.\n',
                                  color=embedColor)
            embed.add_field(name='Error: ',
                            value=f'```{error}```',
                            inline=False)
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

            await ctx.send(embed=embed)

    @dev.command(name='loadext', description='loads an extension.py')
    @commands.is_owner()
    async def loadext(self, ctx, extension_name):
        """loads an extension.py"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        try:
            # load extension
            self.client.load_extension(f'ext.{extension_name[:-3]}')
            logger.info(f'successfully loaded extension <{extension_name}>')

            # send embed
            embed = discord.Embed(title=f'Loaded',
                                  description=f'`{extension_name}` has been loaded successfully!',
                                  color=embedColor)
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

            await ctx.send(embed=embed)

        except Exception as error:
            # send error message/ embed
            logger.critical(f'failed loading extension <{extension_name}>')
            logger.error(f'error: "{error}"')

            embed = discord.Embed(title='Failed',
                                  description=f'The extension `{extension_name}` was not loaded successfully.\n',
                                  color=embedColor)
            embed.add_field(name='Error: ',
                            value=f'```{error}```',
                            inline=False)
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

            await ctx.send(embed=embed)

    @dev.command(name='unloadext', description='unloads an extension.py')
    @commands.is_owner()
    async def unloadext(self, ctx, extension_name):
        """unloads an extension.py"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        try:
            # unload extension
            self.client.unload_extension(f'ext.{extension_name[:-3]}')
            logger.info(f'successfully unloaded extension <{extension_name}>')

            # send embed
            embed = discord.Embed(title=f'Unloaded',
                                  description=f'`{extension_name}` has been unloaded successfully!',
                                  color=embedColor)
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

            await ctx.send(embed=embed)

        except Exception as error:
            # send error message/ embed
            logger.critical(f'failed unloading extension <{extension_name}>')
            logger.error(f'error: "{error}"')

            embed = discord.Embed(title='Failed',
                                  description=f'The extension `{extension_name}` was not unloaded successfully.\n',
                                  color=embedColor)
            embed.add_field(name='Error: ',
                            value=f'```{error}```',
                            inline=False)
            embed.set_author(name=f'Requested by: {ctx.message.author}',
                             icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

            await ctx.send(embed=embed)

    @commands.command(name='testembed', description='sends an embed, therefore tests the bots functionality')
    async def testembed(self, ctx):
        """tests the functionality of the bot by sending an embed"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        embed = discord.Embed(title='Sample Embed',
                              url='https://www.google.com/',
                              description='This is the description of the title/ embed.\n',
                              color=embedColor)
        embed.add_field(name='Field 1',
                        value='This is the value for field 1. This is NOT an inline field.',
                        inline=False)
        embed.add_field(name='Field 2 Title',
                        value='It is inline with Field 3',
                        inline=True)
        embed.add_field(name='Field 3 Title',
                        value='It is inline with Field 2',
                        inline=True)
        embed.set_author(name=f'Requested by: {ctx.message.author}',
                         url='https://www.google.com/',
                         icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=f'BerbBot - {formatted_time}')

        await ctx.send(embed=embed)

    @commands.command(name='testmessage',
                      description='returns a simple message, therefore tests the bots functionality')
    async def testmessage(self, ctx):
        """tests the functionality of the bot by sending a message"""
        await ctx.send('I am alive!')

    @commands.command(name='testtyping', description='makes the typing animation play for a given amount of time')
    async def testtyping(self, ctx, seconds: int = 1):
        """tests the functionality of the bot by sending a message"""
        # play typing animation for x seconds
        async with ctx.typing():
            await asyncio.sleep(seconds)

        # kill typing animation by sending a message
        await ctx.send(f'Finished playing typing animation for `{seconds}s`.')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Development(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
