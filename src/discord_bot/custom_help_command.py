# imports
import os
import logging
import dotenv
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


# class fpr custom help command
class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        self.name = 'help'
        self.description = 'shows command names, descriptions and usages'
        self.usage = '.help [cog_name/ group_name/ command_name]'

        super().__init__()

    async def send_bot_help(self, mapping):
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # design embed
        embed = discord.Embed(title='Help - Bot',
                              description='An overview of all available commands\n',
                              color=embedColor)

        embed.set_footer(text=f'BerbBot - {formatted_time}')

        # add content
        for cog in mapping:
            if cog is not None:
                if 'listener' in cog.qualified_name.lower():
                    break

                cog_name = cog.qualified_name
                cog_commands = '\n'.join(command.name for command in mapping[cog])

                embed.add_field(name=cog_name,
                                value=cog_commands,
                                inline=False)

        # send embed
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # create embed
        embed = discord.Embed(title='Help - Cog',
                              description=f'{cog.description}\n',
                              color=embedColor)

        cog_commands = '\n'.join(command.name for command in cog.get_commands())
        embed.add_field(name=cog.qualified_name,
                        value=cog_commands,
                        inline=False)

        embed.set_footer(text=f'BerbBot - {formatted_time}')

        # send embed
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # create embed
        embed = discord.Embed(title='Help - Group',
                              description=f'{group.description}\n',
                              color=embedColor)

        group_commands = '\n'.join(command.name for index, command in enumerate(group.commands))
        embed.add_field(name=group.name,
                        value=group_commands,
                        inline=False)

        embed.set_footer(text=f'BerbBot - {formatted_time}')

        # send embed
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        # create embed
        # include help for the help command itself
        if command.qualified_name == 'help':
            embed = discord.Embed(title=f'Help - Command',
                                  description=f'{self.description}\n',
                                  color=embedColor)

            embed.add_field(name=self.name,
                            value=f'`{self.usage}`',
                            inline=False)

            embed.set_footer(text=f'BerbBot - {formatted_time}')

        else:
            embed = discord.Embed(title=f'Help - Command',
                                  description=f'{command.description}\n',
                                  color=embedColor)

            embed.add_field(name=command.name,
                            value=f'`{self.get_command_signature(command)}`',
                            inline=False)

            embed.set_footer(text=f'BerbBot - {formatted_time}')

        # send embed
        await self.get_destination().send(embed=embed)
