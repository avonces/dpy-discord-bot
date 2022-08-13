# imports
import os
import logging
import dotenv
from discord.ext import commands, bridge
import ast
from multiprocessing.connection import Listener


# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
subbotIDs = ast.literal_eval(os.getenv('BOT_SUBBOT_IDS'))   # string needs to be converted to list


# connection handler
class ConnectionHandler:
    global subbotIDs

    def __init__(self):
        self.listener = Listener(('localhost', 9999), authkey=None)

        self.unauthenticated_subbot_ids = subbotIDs
        # dictionary containing all connections with the subbot ids as keys
        self.connections = {}

    def establish_connection(self) -> bool:
        connection = self.listener.accept()
        logger.info('connection accepted...')

        authentication_id = int(connection.recv())
        logger.info('authentication message received...')

        if authentication_id in self.unauthenticated_subbot_ids:
            self.connections[self.listener.last_accepted] = connection
            self.unauthenticated_subbot_ids.remove(authentication_id)
            connection.send('authentication succeeded')
            logger.info('Subbot authentication succeeded!')
            return True
        else:
            connection.send('authentication failed')
            logger.info('Subbot authentication failed.')
            connection.close()
            return False

    def receive_by_id(self, subbot_id) -> str:
        message = self.connections[int(subbot_id)].recv()
        return message

    def send_by_id(self, subbot_id, message) -> None:
        self.connections[int(subbot_id)].send(message)

    def send_amount(self, amount, message) -> None:
        subbots = self.connections.values()

        if amount == 'all' or int(amount) >= len(self.connections):
            for subbot in subbots:
                subbot.send(message)
        else:
            for i in range(int(amount)):
                list(subbots)[i].send(message)


# extension
class BotCommunication(commands.Cog, name='Bot Communication',
                       description='allows you to communicate with the BerbGoons (subbots)'):
    """cog for subbot command"""
    global subbotIDs

    def __init__(self, client):
        self.client = client
        self.connection_handler = ConnectionHandler()

    @bridge.bridge_command(name='establish_connection', aliases=['estconn'],
                      description='establish a connection to available subbots')
    @commands.is_owner()
    async def establish_connection(self, ctx: bridge.BridgeContext):
        await ctx.defer()

        if self.connection_handler.establish_connection():
            await ctx.respond('connection established')
        else:
            await ctx.respond('failed establishing connection')

    @bridge.bridge_command(name='send_subbot_command', aliases=['sendsbcmd'],
                           description='send commands to the subbots')
    @commands.is_owner()
    async def send_subbot_command(self, ctx: bridge.BridgeContext, amount: str = '1', *, command: str):
        await ctx.defer()

        subbot_command = f'{ctx.channel.id} {ctx.author.id} {command}'
        self.connection_handler.send_amount(amount, subbot_command)

        await ctx.respond(f'The subbot command `{command}` has been send to **`{amount}`** subbots.')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(BotCommunication(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
