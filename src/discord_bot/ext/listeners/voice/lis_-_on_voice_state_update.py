# imports
import os
import logging
from discord.ext import commands
import asyncio

# logging
"""create logger by inheriting configuration from root logger"""
logger = logging.getLogger(__name__)


# extension
class OnVoiceStateUpdateListener(commands.Cog, name='OnVoiceStateUpdateListener',
                                 description='contains the on_voice_state_update listener'):
    """cog for on_voice_state_update event"""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """makes the bot leave any voice channel if it is alone in there for over 30 seconds"""
        if not member.guild.voice_client:
            # Exit if the bot is not connected to a voice channel
            return

        on_leave_cooldown = False
        if len(member.guild.voice_client.channel.members) == 1:
            # The bot is the only one in the voice channel
            # Wait 30 seconds before checking again, then leave the voice channel
            if not on_leave_cooldown:    # do not try leaving multiple times, it could cause errors
                on_leave_cooldown = True
                await asyncio.sleep(30)

                if len(member.guild.voice_client.channel.members) == 1:
                    if member.guild.voice_client:
                        if member.guild.voice_client.is_connected():
                            member.guild.voice_client.stop()
                            await member.guild.voice_client.disconnect()
                            on_leave_cooldown = False
                            await member.send('I left the voice channel as you were the last person in it and left.')


# cog related functions
def setup(client):
    """load extensions"""
    logger.info(f'loading extension: {os.path.basename(__file__)}')
    client.add_cog(OnVoiceStateUpdateListener(client))


def teardown(client):
    """send information when extension is being unloaded"""
    logger.info(f'unloading extension: {os.path.basename(__file__)}')
