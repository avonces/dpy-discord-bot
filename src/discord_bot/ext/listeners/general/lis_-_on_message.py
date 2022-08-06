# imports
import os
import logging
from discord.ext import commands
import sqlite3


# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# extension
class OnMessageListener(commands.Cog, name='On Message Listener', description='contains the on_message listener'):
    """cog for on_message event"""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        """"custom on_ready event"""
        """count messages sent by users on discord servers"""
        # only count messages in guild
        guild = message.guild

        if guild:
            # needed data
            guild_id = message.guild.id
            user_id = message.author.id

            # connect to "databank.db" and create cursor
            connection = sqlite3.connect('../../data/databank.db')
            cursor = connection.cursor()

            # create table if it does not exist
            sql_command_query = """CREATE TABLE IF NOT EXISTS 
                                            message_counter(guild_id INTEGER, user_id INTEGER, message_count INTEGER DEFAULT 1, 
                                            UNIQUE(guild_id, user_id))"""
            cursor.execute(sql_command_query)

            # insert new count for user into table or update it if it already exists (add 1)
            sql_command_query = f"""INSERT INTO message_counter(guild_id, user_id) 
                                        VALUES({guild_id}, {user_id}) 
                                        ON CONFLICT(guild_id, user_id) DO UPDATE SET message_count = message_count + 1"""
            cursor.execute(sql_command_query)

            # commit changes and close connection
            cursor.close()

            connection.commit()
            connection.close()

        # do not process the following for messages sent by the bot itself
        if message.author == self.client.user:
            return


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(OnMessageListener(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
