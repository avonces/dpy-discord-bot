# imports
import os
import sys
import dotenv
import traceback
import logging
import discord
from discord.ext import commands
from datetime import datetime


# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
errorEmbedColor = int(os.getenv('ERROR_EMBED_COLOR'))


# extension
class CommandErrorHandler(commands.Cog, name='On Command Error Listener',
                          description='catches any occurring command errors, '
                                      'tells the user what he did wrong (if he did something wrong)'):
    """cog for on_command_error event"""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """"handle occurring command errors"""
        global errorEmbedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # prevent any commands with local handlers being handled here
        if hasattr(ctx.command, 'on_error'):
            return

        # prevent any cogs with overwritten cog_command_error being handled here
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        # anything in ignored will return
        ignored = ()    # currently empty, every type of error will be handled
        if isinstance(error, ignored):
            return

        async with ctx.typing():
            # initialize error embed
            embed = discord.Embed()
            # initialize formatted traceback
            formatted_traceback = ''

            # handle occurring errors: prepare error embed
            # bot-related errors
            if isinstance(error, commands.CommandNotFound):
                embed = discord.Embed(title='Error',
                                      description='This command does not exist',
                                      color=errorEmbedColor)
                embed.add_field(name='Help',
                                value='For a list of valid commands use: \n'
                                      f'`{self.client.command_prefix(self.client, ctx.message)[2]}help`',
                                inline=False)

            elif isinstance(error, commands.DisabledCommand):
                embed = discord.Embed(title='Error',
                                      description=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}` has been disabled.',
                                      color=errorEmbedColor)

            elif isinstance(error, commands.BotMissingPermissions):
                embed = discord.Embed(title='Error',
                                      description='I am missing permission to execute '
                                                  f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}`.',
                                      color=errorEmbedColor)

            elif isinstance(error, commands.BotMissingRole):
                embed = discord.Embed(title='Error',
                                      description='I do not have the required role to execute '
                                                  f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}`.',
                                      color=errorEmbedColor)

            # user-related errors
            elif isinstance(error, commands.MissingPermissions):
                embed = discord.Embed(title='Error',
                                      description='You do not have the required permission to execute '
                                                  f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}`.',
                                      color=errorEmbedColor)

            elif isinstance(error, commands.NotOwner):
                embed = discord.Embed(title='Error',
                                      description='You need to be my owner to execute '
                                                  f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}`.',
                                      color=errorEmbedColor)

            elif isinstance(error, commands.NoPrivateMessage):
                try:
                    embed = discord.Embed(title='Error',
                                          description=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                      f'{ctx.command}` can **NOT** be used in Direct Messages.',
                                          color=errorEmbedColor)
                except discord.HTTPException:
                    pass

            elif isinstance(error, commands.PrivateMessageOnly):
                await ctx.send(f'`{self.client.command_prefix(self.client, ctx.message)[2]}{ctx.command}`')
                try:
                    embed = discord.Embed(title='Error',
                                          description=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                      f'{ctx.command}` can **EXCLUSIVELY** be used in Direct Messages.',
                                          color=errorEmbedColor)
                except discord.HTTPException:
                    pass

            elif isinstance(error, commands.CommandOnCooldown):
                embed = discord.Embed(title='Error',
                                      description=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}` is currently on cooldown. Try again later.',
                                      color=errorEmbedColor)

            elif isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(title='Error',
                                      description='I am missing required arguments to execute '
                                                  f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}`. \n',
                                      color=errorEmbedColor)
                embed.add_field(name='Usage',
                                value=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                      f'{ctx.command.qualified_name} {ctx.command.signature}`',
                                inline=False)

            elif isinstance(error, commands.TooManyArguments):
                embed = discord.Embed(title='Error',
                                      description=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}` uses less arguments. \n',
                                      color=errorEmbedColor)
                embed.add_field(name='Usage',
                                value=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                      f'{ctx.command.qualified_name} {ctx.command.signature}`',
                                inline=False)

            elif isinstance(error, commands.BadArgument):
                embed = discord.Embed(title='Error',
                                      description=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}` uses a different kind of arguments. '
                                                  f'You passed an invalid argument\n',
                                      color=errorEmbedColor)
                embed.add_field(name='Usage',
                                value=f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                      f'{ctx.command.qualified_name} {ctx.command.signature}`',
                                inline=False)

            # print traceback for all errors not returned
            else:
                # print traceback
                logger.error(f'ignoring exception in command {ctx.command}: {sys.stderr}')
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

                # get traceback as string
                formatted_traceback = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

                # configure embed
                embed = discord.Embed(title='Error',
                                      description=f'Ignoring exception in command '
                                                  f'`{self.client.command_prefix(self.client, ctx.message)[2]}'
                                                  f'{ctx.command}`: `{sys.stderr}`',
                                      color=errorEmbedColor)

            # format embed
            embed.set_author(name=f'Requested by: {ctx.author}',
                             icon_url=ctx.author.avatar.url)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text=f'BerbBot - {formatted_time}')

        # finally, send error embed
        # if the traceback is too long for one, send multiple embeds
        if len(formatted_traceback) > 1024:
            split_traceback = []

            n = 1024
            for index in range(0, len(formatted_traceback), n):
                split_traceback.append(formatted_traceback[index: index + n])

            for part in split_traceback:
                embed.remove_field(0)
                embed.add_field(name='Traceback',
                                value=part,
                                inline=False)

                await ctx.send(embed=embed)

        else:
            await ctx.send(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(CommandErrorHandler(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
