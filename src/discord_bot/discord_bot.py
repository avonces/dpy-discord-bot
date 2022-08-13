# imports
import os
from datetime import datetime
import logging
from logging import config
import dotenv
import discord
from discord.ext import commands, bridge
from custom_help_command import CustomHelpCommand
import sqlite3
import ast


# logging
"""configure .log file name"""
logFileName = f'logs/log_-_{datetime.now().isoformat().replace(":", "-")}.log'

"""configure root logger; set up basic logger"""
logging.config.fileConfig('../logging.conf', defaults={'logfilename': logFileName})
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()

defaultPrefixes = ast.literal_eval(os.getenv('DEFAULT_PREFIXES'))   # string needs to be converted to list


def get_prefix(client, message):
    """custom function for getting the prefixes from "databank.db" so custom prefixes can be set for guilds"""
    guild = message.guild

    # only allow custom prefixes in guilds
    if guild:
        # needed data
        guild_id = guild.id

        # connect to "databank.db" and create cursor
        connection = sqlite3.connect('../../data/databank.db')
        cursor = connection.cursor()

        # create table if it does not exist
        sql_command_query = """CREATE TABLE IF NOT EXISTS 
        prefix_assignment(guild_id INTEGER, guild_prefix TEXT)"""
        cursor.execute(sql_command_query)

        # get needed information
        sql_command_query = f"""SELECT * FROM prefix_assignment WHERE guild_id = {guild_id}"""
        cursor.execute(sql_command_query)
        rows = cursor.fetchall()

        # close connection
        cursor.close()
        connection.close()

        # check if there are entries for the guild id, if there are, return custom prefixes
        if rows:
            prefix_list = []

            # there are entries, add all the prefixes to the prefix_list and return the list
            for row in rows:
                prefix = row[1]
                prefix_list.append(prefix)

            return commands.when_mentioned_or(*prefix_list)(client, message)

        else:
            # there aren't any entries, therefore, return the default prefixes
            return commands.when_mentioned_or(*defaultPrefixes)(client, message)

    else:
        return commands.when_mentioned_or(*defaultPrefixes)(client, message)


# create bot
"""create the client (bot)"""
intents = discord.Intents.all()
client = bridge.Bot(
    command_prefix=get_prefix,
    strip_after_prefix=True,
    case_insensitive=True,
    intents=intents,
    help_command=CustomHelpCommand(),
    debug_guilds=[967030034240012328]
)


# define main function for running bot
def main():
    """runs the code and starts the client"""
    logger.info('loading extensions...')
    """load all the available extensions from "ext" folder"""
    # initialize dictionary for saving path.to.files: [filenames]
    dir_name_filenames_dict = {}

    # get all files from directories and subdirectories
    for (dir_path, dir_name, file_names) in os.walk('./ext'):
        dotted_dir_path = dir_path.replace('./', '').replace('\\', '.')
        dir_name_filenames_dict[dotted_dir_path] = file_names

    # try loading all the files that end on .py
    for dotted_dir_path in dir_name_filenames_dict.keys():
        for file_name in dir_name_filenames_dict[dotted_dir_path]:
            if file_name.endswith('.py'):
                try:
                    if not file_name == 'discord_subbot.py':
                        client.load_extension(f'{dotted_dir_path}.{file_name[:-3]}')
                        logger.info(f'successfully loaded extension {dotted_dir_path}.{file_name[:-3]}')
                except Exception as error:
                    logger.critical(f'failed loading extension {dotted_dir_path}.{file_name[:-3]}')
                    logger.error(f'error: "{error}"')

    # run
    logger.info('executing...')
    """run the code and start the client"""
    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()
