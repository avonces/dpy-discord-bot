# imports
import os
import logging
import dotenv
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from requests_cache import CachedSession
import math
from re import findall

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# dotenv
"""import secrets and vars from .env file because of security and configuration reasons"""
dotenv.load_dotenv()
embedColor = int(os.getenv('EMBED_COLOR'))
hypixelApiKey = os.getenv('HYPIXEL_API_KEY')


# extension
class Minecraft(commands.Cog, name='Hypixel', description='contains hypixel related commands'):
    """cog for hypixel command group"""
    def __init__(self, client):
        self.client = client

        self.cached_request_session = CachedSession(
            'birb-bot_-_hypixel_request_cache',
            use_cache_dir=True,                     # Save files in the default user cache dir
            cache_control=True,                     # Use Cache-Control headers for expiration, if available
            expire_after=timedelta(minutes=10),     # Otherwise, expire responses after ten minutes
            allowable_methods=['GET', 'POST'],      # Cache POST requests to avoid sending the same data twice
            allowable_codes=[200, 400],             # Cache 400 responses as a solemn reminder of your failures
            ignored_parameters=['api_key', 'key'],  # Don't match this param or save it in the cache
            match_headers=True,                     # Match all request headers
            stale_if_error=True,                    # In case of request errors, use stale cache data if possible
        )

    # TODO: Bridge groups not working
    @commands.group(name='render_skin', aliases=['renderskin', 'rnsn'],
                    description='command group containing commands for rendering parts of a minecraft skin')
    async def render_skin(self, ctx: commands.Context):
        """creates a command group "renderskin" for using subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @render_skin.command(name='face', description='render the face of a minecraft player')
    async def face(self, ctx: commands.Context, player_name: str):
        """send a picture of a minecraft player's face"""
        try:
            async with ctx.typing():
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()
                player_uuid = uuid_data['id']

            await ctx.send(f'https://crafatar.com/avatars/{player_uuid}?size=128&overlay')
        except Exception as e:
            await ctx.send('This player does not exist or an API-Error occurred.')
            logger.exception(e)

    @render_skin.command(name='head', description='render the head of a minecraft player')
    async def head(self, ctx: commands.Context, player_name: str):
        """send a picture of a minecraft player's head"""
        try:
            async with ctx.typing():
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()
                player_uuid = uuid_data['id']

            await ctx.send(f'https://crafatar.com/renders/head/{player_uuid}?size=512&overlay')
        except Exception as e:
            await ctx.send('This player does not exist or an API-Error occurred.')
            logger.exception(e)

    @render_skin.command(name='body', description='render the body of a minecraft player')
    async def body(self, ctx: commands.Context, player_name: str):
        """send a picture of a minecraft player's body"""
        try:
            async with ctx.typing():
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()
                player_uuid = uuid_data['id']

            await ctx.send(f'https://crafatar.com/renders/body/{player_uuid}?size=512&overlay')
        except Exception as e:
            await ctx.send('This player does not exist or an API-Error occurred.')
            logger.exception(e)

    # TODO: Bridge groups not working
    @commands.group(name='hypixel', aliases=['hypx'],
                    description='command group containing commands for displaying hypixel player stats')
    async def hypixel(self, ctx: commands.Context):
        """creates a command group "hypixel" for using subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Please pass a valid subcommand.')

    @hypixel.command(name='general', aliases=['overall'], description='sends general statistics for a hypixel player')
    async def general(self, ctx: commands.Context, hypixel_player_name: str):
        """sends an embed containing general statistics for a hypixel player"""

        global hypixelApiKey

        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.send('In Work! Give me a few seconds to load the data!')

        async with ctx.typing():
            embed = discord.Embed(title='Overall Hypixel Stats',
                                  description=f'Overall hypixel player statistics for "{hypixel_player_name}"',
                                  color=embedColor)
            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar.url)

            try:
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{hypixel_player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()

                player_uuid = uuid_data['id']
                embed.add_field(name='UUID', value=f'UUID: {player_uuid}', inline=False)
                embed.set_thumbnail(url=f"https://crafatar.com/avatars/{player_uuid}")

                """
                player-head-render as thumbnail: embed.set_thumbnail(url=f'https://crafatar.com/renders/head/{player_uuid}')
                """

                try:
                    player_data_url = f'https://api.hypixel.net/player?key={hypixelApiKey}&uuid={player_uuid}'
                    player_data = self.cached_request_session.get(player_data_url).json()

                    if player_data['player'] is not None:
                        if 'rank' in player_data['player'] and player_data['player']['rank'] != 'NORMAL':
                            player_rank = player_data['player']['rank']
                        elif 'newPackageRank' in player_data['player']:
                            player_rank = player_data['player']['newPackageRank']
                        elif 'packageRank' in player_data['player']:
                            player_rank = player_data['player']['packageRank']
                        else:
                            player_rank = 'Non'
                        embed.add_field(name='Rank', value=f"{hypixel_player_name}'s Rank: `{player_rank}`",
                                        inline=True)

                        network_exp = player_data['player']['networkExp']
                        player_level_exact = (math.sqrt((2 * network_exp) + 30625) / 50) - 2.5
                        player_level_rounded = round(player_level_exact, 2)
                        embed.add_field(name='Hypixel Level',
                                        value=f"{hypixel_player_name}'s Level: `{player_level_rounded}`",
                                        inline=True)

                        player_karma = player_data['player']['karma'] if 'karma' in player_data['player'] else 0
                        embed.add_field(name='Karma', value=f"{hypixel_player_name}'s Karma: `{str(player_karma)}`",
                                        inline=True)

                        if 'socialMedia' in player_data['player'].keys():
                            player_twitter = player_data['player']['socialMedia']['links']['TWITTER'] \
                                if 'TWITTER' in player_data['player']['socialMedia']['links'].keys() \
                                else 'No Twitter linked.'
                            embed.add_field(name='Twitter',
                                            value=f"{hypixel_player_name}'s Twitter: `{player_twitter}`",
                                            inline=True)
                            player_discord = player_data['player']['socialMedia']['links']['DISCORD'] \
                                if 'DISCORD' in player_data['player']['socialMedia']['links'].keys() \
                                else 'No Discord linked.'
                            embed.add_field(name='Discord',
                                            value=f"{hypixel_player_name}'s Discord: `{player_discord}`",
                                            inline=True)

                        player_last_login = player_data['player']['lastLogin']
                        player_last_logout = player_data['player']['lastLogout']
                        player_online_status = 'True' if player_last_login > player_last_logout else 'False'
                        embed.add_field(name='Online', value=f'Online: `{player_online_status}`', inline=True)

                        try:
                            guild_url = f'https://api.hypixel.net/guild?player={player_uuid}&key={hypixelApiKey}'
                            guild_data = self.cached_request_session.get(guild_url).json()

                            if guild_data['guild'] is not None:
                                guild_name = guild_data['guild']['name']
                                guild_id = guild_data['guild']['_id']
                                embed.add_field(name='Guild', value=f'Name: `{guild_name}`\n'
                                                                    f'ID: `{guild_id}`',
                                                inline=True)
                            else:
                                embed.add_field(name='Guild', value=f'{hypixel_player_name} is not in a guild',
                                                inline=True)
                        except Exception as e:
                            embed.add_field(name='Guild', value='An API-Error occurred. Please try again later.',
                                            inline=True)
                            logger.exception(e)
                    else:
                        embed.add_field(name='Player/ Error', value='This player never played on hypixel.',
                                        inline=False)

                except Exception as e:
                    embed.add_field(name='Error', value='An API-Error occurred.\nPlease try again later.', inline=False)
                    logger.exception(e)
            except Exception as e:
                embed.add_field(name='Player/ Error', value='This Player does not exist or an API-Error occurred.',
                                inline=False)
                logger.exception(e)

        await ctx.send(embed=embed)

    @hypixel.command(name='guild_member', aliases=['guildmember', 'gm'],
                     description='sends statistics for a hypixel guild member')
    async def guild_member(self, ctx: commands.Context, hypixel_player_name: str):
        """sends an embed containing statistics for a hypixel guild member"""
        global hypixelApiKey

        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.send('In Work! Give me a few seconds to load the data!')

        async with ctx.typing():
            embed = discord.Embed(title='Hypixel Guild Member Stats',
                                  description=f'Overall hypixel guild-member statistics for **"{hypixel_player_name}"**',
                                  color=embedColor)
            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar.url)

            try:
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{hypixel_player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()

                player_uuid = uuid_data['id']
                embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player_uuid}')
                """
                player-head-render as thumbnail: embed.set_thumbnail(url=f'https://crafatar.com/renders/head/{player_uuid}')
                """

                try:
                    guild_url = f'https://api.hypixel.net/guild?key={hypixelApiKey}&player={player_uuid}'
                    guild_data = self.cached_request_session.get(guild_url).json()

                    if guild_data['guild'] is not None:

                        guild_name = guild_data['guild']['name']
                        guild_id = guild_data['guild']['_id']
                        embed.add_field(name='Guild Name', value=f'Guild Name: `{guild_name}`', inline=False)
                        embed.add_field(name='Guild ID', value=f'Guild ID: `{guild_id}`', inline=False)

                        for member in range(len(guild_data['guild']['members'])):
                            uuid = guild_data['guild']['members'][member]['uuid']
                            if uuid == player_uuid:
                                player_guild_rank = guild_data['guild']['members'][member]['rank']
                                player_guild_quest_participation = guild_data['guild']['members'][member][
                                    'questParticipation']
                                exp_history_sum = '{:,}'.format(
                                    sum(guild_data['guild']['members'][member]['expHistory']
                                        .values()))
                                embed.add_field(name='Quests', value=f'{hypixel_player_name} participated in '
                                                                     f'**`{player_guild_quest_participation}` quests**.',
                                                inline=False)
                                embed.add_field(name='Rank', value=f"{hypixel_player_name}'s Rank: "
                                                                   f'**`{player_guild_rank}`**',
                                                inline=False)
                                embed.add_field(name='Overall Guild EXP',
                                                value=f'**{hypixel_player_name}** has gained '
                                                      f'**`{exp_history_sum}`** '
                                                      'GEXP in the last 7 days.',
                                                inline=False)

                                exp_history_days = {}
                                num_day = 0
                                for key, value in guild_data['guild']['members'][member]['expHistory'].items():
                                    exp_history_days[num_day] = f'{key}: {value}'
                                    num_day += 1
                                embed.add_field(name="Guild EXP In Days",
                                                value=f"**{hypixel_player_name}** has gained:\n"
                                                      f'`{exp_history_days[0]}`\n'
                                                      f'`{exp_history_days[1]}`\n'
                                                      f'`{exp_history_days[2]}`\n'
                                                      f'`{exp_history_days[3]}`\n'
                                                      f'`{exp_history_days[4]}`\n'
                                                      f'`{exp_history_days[5]}`\n'
                                                      f'`{exp_history_days[6]}`\n',
                                                inline=False)
                    else:
                        embed.add_field(name='Guild', value=f'{hypixel_player_name} is not in a guild', inline=True)

                except Exception as e:
                    embed.add_field(name='Error', value='An API-Error occurred.\nPlease try again later.', inline=False)
                    logger.exception(e)
            except Exception as e:
                embed.add_field(name='Player/ Error', value='This Player does not exist or an API-Error occurred.',
                                inline=False)
                logger.exception(e)

        await ctx.send(embed=embed)

    @hypixel.command(name='bed_wars', aliases=['bedwars', 'bw'],
                     description='sends bedwars statistics for a hypixel player')
    async def bed_wars(self, ctx: commands.Context, hypixel_player_name: str):
        """sends an embed containing general statistics for a hypixel player"""
        global hypixelApiKey

        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.send('In Work! Give me a few seconds to load the data!')

        async with ctx.typing():
            embed = discord.Embed(title='Hypixel Bedwars Stats',
                                  description=f'Overall hypixel bedwars statistics for {hypixel_player_name}',
                                  color=embedColor)
            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar.url)

            try:
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{hypixel_player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()

                player_uuid = uuid_data['id']
                embed.add_field(name='UUID', value=f'UUID: {player_uuid}', inline=False)
                embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player_uuid}')

                """
                player-head-render as thumbnail: embed.set_thumbnail(url=f'https://crafatar.com/renders/head/{player_uuid}')
                """

                try:
                    player_data_url = f'https://api.hypixel.net/player?key={hypixelApiKey}&uuid={player_uuid}'
                    player_data = self.cached_request_session.get(player_data_url).json()

                    if player_data['player'] is not None:
                        try:
                            player_stats_achievments = player_data['player']['achievements']
                            player_bedwars_level = player_stats_achievments['bedwars_level']

                            player_bedwars_stats = player_data['player']['stats']['Bedwars']
                            player_bedwars_games = player_bedwars_stats['games_played_bedwars']
                            player_bedwars_wins = player_bedwars_stats['wins_bedwars']
                            player_bedwars_losses = player_bedwars_stats['losses_bedwars']
                            player_bedwars_winstreak = player_bedwars_stats['winstreak']
                            player_bedwars_bed_breaks = player_bedwars_stats['beds_broken_bedwars']
                            player_bedwars_bed_losses = player_bedwars_stats['beds_lost_bedwars']
                            player_bedwars_kills = player_bedwars_stats['kills_bedwars']
                            player_bedwars_final_kills = player_bedwars_stats['final_kills_bedwars']
                            player_bedwars_deaths = player_bedwars_stats['deaths_bedwars']
                            player_bedwars_final_deaths = player_bedwars_stats['final_deaths_bedwars']
                            player_bedwars_coins = player_bedwars_stats['coins']

                            player_bedwars_win_loss_rate = round(player_bedwars_wins / player_bedwars_losses, 2)
                            player_bedwars_kill_death_rate = round(player_bedwars_kills / player_bedwars_deaths, 2)
                            player_bedwars_final_kill_death_rate = round(player_bedwars_final_kills /
                                                                         player_bedwars_final_deaths, 2)

                            embed.add_field(name='Bedwars Level',
                                            value=f"{hypixel_player_name}'s Stars: `{player_bedwars_level}`",
                                            inline=True)
                            embed.add_field(name='Games', value=f'Games: `{player_bedwars_games}`', inline=True)
                            embed.add_field(name='Wins', value=f'Wins: `{player_bedwars_wins}`\n'
                                                               f'Win Streak: `{player_bedwars_winstreak}`',
                                            inline=True)
                            embed.add_field(name='Losses', value=f'Losses: `{player_bedwars_losses}`', inline=True)
                            embed.add_field(name='Win/Loss Rate', value=f'WLR: `{player_bedwars_win_loss_rate}`',
                                            inline=True)
                            embed.add_field(name='Beds', value=f'Beds Broken: `{player_bedwars_bed_breaks}`\n'
                                                               f'Beds Lost: `{player_bedwars_bed_losses}`', inline=True)
                            embed.add_field(name='Kills', value=f'Kills: `{player_bedwars_kills}`\n'
                                                                f'Final Kills: `{player_bedwars_final_kills}`',
                                            inline=True)
                            embed.add_field(name='Deaths', value=f'Deaths: `{player_bedwars_deaths}`\n'
                                                                 f'Final Deaths: `{player_bedwars_final_deaths}`',
                                            inline=True)
                            embed.add_field(name='Kill/Death Rates',
                                            value=f'KDR: `{player_bedwars_kill_death_rate}`\n'
                                                  f'FKDR: `{player_bedwars_final_kill_death_rate}`',
                                            inline=True)
                            embed.add_field(name='Coins', value=f'Coins: `{player_bedwars_coins}`', inline=True)
                        except Exception as e:
                            embed.add_field(name='Player/ Error',
                                            value='This Player never played bedwars or an API-Error occurred.'
                                                  'If so, please try again later.',
                                            inline=False)
                            logger.exception(e)
                    else:
                        embed.add_field(name='Player/ Error', value='This player never played on hypixel.',
                                        inline=False)

                except Exception as e:
                    embed.add_field(name='Error', value='An API-Error occurred.\nPlease try again later.', inline=False)
                    logger.exception(e)
            except Exception as e:
                embed.add_field(name='Player/ Error', value='This Player does not exist or an API-Error occurred.',
                                inline=False)
                logger.exception(e)

        await ctx.send(embed=embed)

    @hypixel.command(name='sky_wars', aliases=['skywars', 'sw'],
                     description='sends skywars statistics for a hypixel player')
    async def sky_wars(self, ctx: commands.Context, hypixel_player_name: str):
        """sends an embed containing general statistics for a hypixel player"""
        global hypixelApiKey

        global embedColor
        time = datetime.now()
        formatted_time = time.strftime('%H:%M')

        await ctx.send('In Work! Give me a few seconds to load the data!')

        async with ctx.typing():
            embed = discord.Embed(title='Hypixel Skywars Stats',
                                  description=f'Overall hypixel skywars statistics for {hypixel_player_name}',
                                  color=embedColor)
            embed.set_footer(text=f'BerbBot - {formatted_time}')
            embed.set_author(name=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar.url)

            try:
                player_uuid_url = f'https://api.mojang.com/users/profiles/minecraft/{hypixel_player_name}'
                uuid_data = self.cached_request_session.get(player_uuid_url).json()

                player_uuid = uuid_data['id']
                embed.add_field(name='UUID', value=f'UUID: {player_uuid}', inline=False)
                embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player_uuid}')

                """
                player-head-render as thumbnail: embed.set_thumbnail(url=f'https://crafatar.com/renders/head/{player_uuid}')
                """

                try:
                    player_data_url = f'https://api.hypixel.net/player?key={hypixelApiKey}&uuid={player_uuid}'
                    player_data = self.cached_request_session.get(player_data_url).json()

                    if player_data['player'] is not None:
                        try:
                            player_skywars_stats = player_data['player']['stats']['SkyWars']
                            player_skywars_level = str(findall(r'\d+', player_skywars_stats['levelFormatted'])[0])
                            player_skywars_games = player_skywars_stats['games_played_skywars']
                            player_skywars_wins = player_skywars_stats['wins']
                            player_skywars_losses = player_skywars_stats['losses']
                            player_skywars_winstreak = player_skywars_stats['win_streak']
                            player_skywars_kills = player_skywars_stats['melee_kills']
                            player_skywars_killstreak = player_skywars_stats['killstreak']
                            player_skywars_deaths = player_skywars_stats['deaths']
                            player_skywars_arrows_shot = player_skywars_stats['arrows_shot']
                            player_skywars_arrows_hit = player_skywars_stats['arrows_hit']
                            player_skywars_coins = player_skywars_stats['coins']

                            player_skywars_win_loss_rate = round(player_skywars_wins / player_skywars_losses, 2)
                            player_skywars_kill_death_rate = round(player_skywars_kills / player_skywars_deaths, 2)

                            embed.add_field(name='Skywars Level',
                                            value=f"{hypixel_player_name}'s Level: `{player_skywars_level}`",
                                            inline=True)
                            embed.add_field(name='Games', value=f'Games: `{player_skywars_games}`', inline=True)
                            embed.add_field(name='Wins', value=f'Wins: `{player_skywars_wins}`\n'
                                                               f'Win Streak: `{player_skywars_winstreak}`', inline=True)
                            embed.add_field(name='Losses', value=f'Losses: `{player_skywars_losses}`', inline=True)
                            embed.add_field(name='Win/Loss Rate', value=f'WLR: `{player_skywars_win_loss_rate}`',
                                            inline=True)
                            embed.add_field(name='Kills', value=f'Kills: `{player_skywars_kills}`\n'
                                                                f'Kill Streak: `{player_skywars_killstreak}`',
                                            inline=True)
                            embed.add_field(name='Deaths', value=f'Deaths: `{player_skywars_deaths}`', inline=True)
                            embed.add_field(name='Kill/Death Rate',
                                            value=f'KDR: `{player_skywars_kill_death_rate}`',
                                            inline=True)
                            embed.add_field(name='Bow', value=f'Arrows Shot: `{player_skywars_arrows_shot}`\n'
                                                              f'Arrows Hit: `{player_skywars_arrows_hit}`', inline=True)
                            embed.add_field(name='Coins', value=f'Coins: `{player_skywars_coins}`', inline=True)
                        except Exception as e:
                            embed.add_field(name='Player/ Error',
                                            value='This Player never played skywars or an API-Error occurred.'
                                                  'If so, please try again later.',
                                            inline=False)
                            logger.exception(e)
                    else:
                        embed.add_field(name='Player/ Error', value='This player never played on hypixel.',
                                        inline=False)

                except Exception as e:
                    embed.add_field(name='Error', value='An API-Error occurred.\nPlease try again later.', inline=False)
                    logger.exception(e)
            except Exception as e:
                embed.add_field(name='Player/ Error', value='This Player does not exist or an API-Error occurred.',
                                inline=False)
                logger.exception(e)

        await ctx.send(embed=embed)


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(Minecraft(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
