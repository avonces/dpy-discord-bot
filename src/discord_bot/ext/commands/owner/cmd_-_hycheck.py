# imports
import os
import logging
import dotenv
import discord
from datetime import datetime
from discord.ext import commands, tasks
import requests

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()

embedColor = int(os.getenv('EMBED_COLOR'))
hypixelApiKeyHycheck = os.getenv('HYPIXEL_API_KEY_HYCHECK')


# extension
class Hycheck(commands.Cog, name='Hycheck',
              description='contains commands for starting a hypixel player online check loop'):
    """cog for hycheck commands and functionality"""
    def __init__(self, client):
        self.client = client

        self.request_session = requests.Session()

        self.channel = None
        self.ignore_exceptions = False
        self.friends = {}

        # structure/ testing:
        # self.friends = {'8159687be31a4cbda70d9a446b22dd5f': {'name': 'Fireboerd', 'status': 'offline'}}

    # ------
    # check loop
    # ------

    @tasks.loop(seconds=300)
    async def get_online(self):
        for player_uuid in self.friends.keys():
            try:
                player_data_url = f'https://api.hypixel.net/player?key={hypixelApiKeyHycheck}&uuid={player_uuid}'
                player_data = self.request_session.get(player_data_url).json()

                if player_data['player'] is not None:
                    player_last_login = player_data['player']['lastLogin']
                    player_last_logout = player_data['player']['lastLogout']

                    if player_last_login > player_last_logout and self.friends[player_uuid]['status'] == 'offline':
                        # the player is online and was offline before
                        time = datetime.now()
                        formatted_time = time.strftime('%H:%M')

                        self.friends[player_uuid]['status'] = 'online'

                        embed = discord.Embed(title=f'{self.friends[player_uuid]["name"]} is online!',
                                              description=f'**{self.friends[player_uuid]["name"]}** '
                                                          'is now **`online`** on the Hypixel network!',
                                              color=discord.Color.dark_green())
                        embed.set_footer(text=f'BerbBot - {formatted_time}')
                        embed.set_author(name=f'{player_uuid}',
                                         # from the Twitter account of the hypixel owner
                                         icon_url='https://pbs.twimg.com/profile_images/'
                                                  '1346968969849171970/DdNypQdN_400x400.png')
                        embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player_uuid}')

                        await self.channel.send(embed=embed)

                    elif player_last_login < player_last_logout and self.friends[player_uuid]['status'] == 'online':
                        # the player is offline and was online before
                        time = datetime.now()
                        formatted_time = time.strftime('%H:%M')

                        self.friends[player_uuid]['status'] = 'offline'

                        embed = discord.Embed(title=f'{self.friends[player_uuid]["name"]} is offline!',
                                              description=f'**{self.friends[player_uuid]["name"]}** '
                                                          'is now **`offline`** and left the Hypixel network!',
                                              color=discord.Color.orange())
                        embed.set_footer(text=f'BerbBot - {formatted_time}')
                        embed.set_author(name=f'{player_uuid}',
                                         # from the Twitter account of the hypixel owner
                                         icon_url='https://pbs.twimg.com/profile_images/' 
                                                  '1346968969849171970/DdNypQdN_400x400.png')
                        embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player_uuid}')

                        await self.channel.send(embed=embed)

                else:
                    del self.friends[player_uuid]
                    await self.channel.send(f'The player {self.friends[player_uuid]["name"]} never played on hypixel '
                                            'and was therefore removed from the checklist')

            except Exception as e:
                logger.exception(e)

                if not self.ignore_exceptions:
                    self.get_online.cancel()

                    await self.channel.send(
                        'An API-Error occurred. The online check loop has been stopped.\n'
                        'You may want to disable this feature using the "ignore_exceptions" command.\n\n'
                        f'**Error:** {e}')

    # ------
    # commands
    # ------

    @commands.group(name='hycheck', description='command group containing hycheck commands')
    @commands.is_owner()
    async def hycheck(self, ctx: commands.Context):
        """creates a command group "hycheck" for using subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @hycheck.command(name='toggle_ignore_exceptions',
                     aliases=['toggleignoreexceptions', 'ignore_exceptions', 'ignoreexceptions'],
                     description='the loop keeps going, even if errors occur;\n'
                                 'errors will not be printed out for you')
    @commands.is_owner()
    async def toggle_ignore_exceptions(self, ctx: commands.Context):
        """the loop keeps going, even if errors occur; errors will not be printed out for you"""
        if self.ignore_exceptions:
            self.ignore_exceptions = False
            await ctx.send(f'Exceptions will no longer be ignored.')
        else:
            self.ignore_exceptions = True
            await ctx.send(f'From now on, exceptions will be ignored.')

    @hycheck.command(name='set_interval', aliases=['setinterval', 'change_interval', 'changeinterval'],
                     description='changes the interval of the check loop to the given time interval')
    @commands.is_owner()
    async def set_interval(self, ctx: commands.Context, hours: float, minutes: float, seconds: float):
        """changes the interval of the check loop"""
        self.get_online.change_interval(seconds=seconds, minutes=minutes, hours=hours)
        await ctx.send('The interval of the online check loop has been set to: '
                       f'**`{self.get_online.hours}` hours, '
                       f'`{self.get_online.minutes}` minutes, '
                       f'`{self.get_online.seconds}` seconds**.')

    @hycheck.command(name='start_requests', aliases=['startrequests'],
                     description='starts the online check loop')
    @commands.is_owner()
    async def start_requests(self, ctx: commands.Context):
        """starts the online check loop"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        if not self.get_online.is_running():
            self.channel = ctx.channel
            self.get_online.start()

            embed = discord.Embed(title='Started!',
                                  description='The online check loop has been started.',
                                  color=embedColor)
        else:
            embed = discord.Embed(title='Failed!',
                                  description='The online check loop is already running and logging in the channel: '
                                              f'{self.channel.name}.',
                                  color=embedColor)

        embed.set_footer(text=f'BerbBot - {formatted_time}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @hycheck.command(name='stop_requests', aliases=['stoprequests'],
                     description='stops the online check loop gracefully;\n'
                                 'the current iteration will be finished before stopping')
    @commands.is_owner()
    async def stop_requests(self, ctx: commands.Context):
        """stops the online check loop"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        if self.get_online.is_running():
            self.get_online.stop()

            embed = discord.Embed(title='Stopping!',
                                  description='The online check loop is now stopping.',
                                  color=embedColor)
        else:
            embed = discord.Embed(title='Failed!',
                                  description='The online check loop is currently not running.'
                                              f'{self.channel.name}.',
                                  color=embedColor)

        embed.set_footer(text=f'BerbBot - {formatted_time}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @hycheck.command(name='force_stop_requests', aliases=['forcestoprequests'],
                     description='forces the online check loop to stop')
    @commands.is_owner()
    async def force_stop_requests(self, ctx: commands.Context):
        """stops the online check loop"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        if self.get_online.is_running():
            self.get_online.cancel()

            embed = discord.Embed(title='Stopped!',
                                  description='The online check loop has been stopped forcefully.',
                                  color=embedColor)
        else:
            embed = discord.Embed(title='Failed!',
                                  description='The online check loop is currently not running.'
                                              f'{self.channel.name}.',
                                  color=embedColor)

        embed.set_footer(text=f'BerbBot - {formatted_time}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @hycheck.command(name='add_friend', aliases=['addfriend'],
                     description='adds a friend to the checklist for the next time the check is executed')
    @commands.is_owner()
    async def add_friend(self, ctx: commands.Context, player_name: str):
        """adds a friend to the checklist for the next time the check is executed"""
        player_name = str(player_name).strip()

        if player_name not in [data['name'] for data in [dataset for dataset in self.friends.values()]]:
            try:
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{player_name}'
                uuid_data = self.request_session.get(player_uuid_url).json()

                player_uuid = str(uuid_data['id'])

                self.friends[player_uuid] = {'name': player_name, 'status': 'offline'}
                await ctx.send(f'`{player_name}` has successfully been added to the online checklist!')

            except Exception as e:
                logger.exception(e)
                await ctx.send(f'The player "{player_name}" does not exist '
                               'and was therefore not added to the online checklist.')

        else:
            await ctx.send(f'`{player_name}` is already in the online checklist.')

    @hycheck.command(name='add_friends', aliases=['addfriends'],
                     description='adds multiple friends to the checklist for the next time the check is executed')
    @commands.is_owner()
    async def add_friends(self, ctx: commands.Context, *, player_names: str):
        player_name_list = player_names.split()

        for player_name in player_name_list:
            player_name = str(player_name).strip()

            if player_name not in [data['name'] for data in [dataset for dataset in self.friends.values()]]:
                try:
                    player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{player_name}'
                    uuid_data = self.request_session.get(player_uuid_url).json()

                    player_uuid = str(uuid_data['id'])

                    self.friends[player_uuid] = {'name': player_name, 'status': 'offline'}
                    await ctx.send(f'`{player_name}` has successfully been added to the online checklist!')

                except Exception as e:
                    logger.exception(e)
                    await ctx.send(f'The player "{player_name}" does not exist '
                                   'and was therefore not added to the online checklist.')

            else:
                await ctx.send(f'`{player_name}` is already in the online checklist.')

    @hycheck.command(name='remove_friend', aliases=['removefriend'],
                     description='removes a friend to the checklist for the next time the check is executed')
    @commands.is_owner()
    async def remove_friend(self, ctx: commands.Context, player_name: str):
        """removes a friend from the checklist for the next time the check is executed"""
        for player_uuid, player_data in self.friends.items():
            if player_data['name'] == player_name:
                del self.friends[player_uuid]
                await ctx.send(f'`{player_name}` has successfully been removed from the online checklist!')
                break

        else:
            await ctx.send('This player was never listed in the online checklist.')

    @hycheck.command(name='remove_friends', aliases=['removefriends'],
                     description='removes multiple friends from the checklist for the next time the check is executed')
    @commands.is_owner()
    async def remove_friends(self, ctx: commands.Context, *, player_names: str):
        player_name_list = player_names.split()

        for player_name in player_name_list:
            player_to_remove = ''

            for player_uuid, player_data in self.friends.items():
                if player_data['name'] == player_name:
                    player_to_remove = player_uuid
                    break
            else:
                await ctx.send(f'{player_name} was never listed in the online checklist.')

            if player_to_remove:
                del self.friends[player_to_remove]
                await ctx.send(f'`{player_name}` has successfully been removed from the online checklist!')

    @hycheck.command(name='checklist',
                     description='sends a list of all the players in the checklist and their current status')
    @commands.is_owner()
    async def checklist(self, ctx: commands.Context):
        """sends a list of all the players in the checklist and their current status"""
        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        embed = discord.Embed(title='Online Checklist',
                              description='all players in the checklist and their current status',
                              color=embedColor)
        embed.set_footer(text=f'BerbBot - {formatted_time}')
        embed.set_author(name=f'Requested by: {ctx.author}',
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        if self.friends:
            players_online_offline = {'online': [], 'offline': []}
            for player_data in self.friends.values():
                if player_data['status'] == 'online':
                    players_online_offline['online'].append(player_data['name'])
                else:
                    players_online_offline['offline'].append(player_data['name'])

            embed.add_field(name='Online',
                            value=',\n'.join(players_online_offline['online']) if players_online_offline['online']
                            else '-',
                            inline=True)
            embed.add_field(name='Offline',
                            value=',\n'.join(players_online_offline['offline']) if players_online_offline['offline']
                            else '-',
                            inline=True)

        else:
            embed.add_field(name='Online/ Offline', value='There are no players in the checklist.', inline=False)

        await ctx.send(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Hycheck(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
