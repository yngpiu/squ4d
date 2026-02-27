# SPDX-FileCopyrightText: 2018-2025 Joonas Rautiola <mail@joinemm.dev>
# SPDX-License-Identifier: MPL-2.0
# https://git.joinemm.dev/miso-bot

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from modules.misobot import MisoBot


class Cache:
    def __init__(self, bot):
        self.bot: MisoBot = bot
        self.log_emoji = False
        self.prefixes = {}
        self.rolepickers = set()
        self.autoresponse = {}
        self.blacklist = {}
        self.marriages = []



    async def initialize_settings_cache(self):
        logger.info("Caching settings...")


        guild_settings = await self.bot.db.fetch(
            "SELECT guild_id, autoresponses FROM guild_settings"
        )
        if guild_settings:
            for guild_id, autoresponses in guild_settings:
                self.autoresponse[str(guild_id)] = autoresponses

        self.blacklist = {
            "global": {
                "user": set(
                    await self.bot.db.fetch_flattened(
                        "SELECT user_id FROM blacklisted_user"
                    )
                ),
                "guild": set(
                    await self.bot.db.fetch_flattened(
                        "SELECT guild_id FROM blacklisted_guild"
                    )
                ),
                "channel": set(
                    await self.bot.db.fetch_flattened(
                        "SELECT channel_id FROM blacklisted_channel"
                    )
                ),
            }
        }

        pairs = await self.bot.db.fetch(
            "SELECT first_user_id, second_user_id FROM marriage"
        )
        self.marriages = [set(pair) for pair in pairs] if pairs else []

        blacklisted_members = await self.bot.db.fetch(
            "SELECT guild_id, user_id FROM blacklisted_member"
        )
        if blacklisted_members:
            for guild_id, user_id in blacklisted_members:
                try:
                    self.blacklist[str(guild_id)]["member"].add(user_id)
                except KeyError:
                    self.blacklist[str(guild_id)] = {
                        "member": {user_id},
                        "command": set(),
                    }
        blacklisted_commands = await self.bot.db.fetch(
            "SELECT guild_id, command_name FROM blacklisted_command"
        )
        if blacklisted_commands:
            for guild_id, command_name in blacklisted_commands:
                try:
                    self.blacklist[str(guild_id)]["command"].add(command_name.lower())
                except KeyError:
                    self.blacklist[str(guild_id)] = {
                        "member": set(),
                        "command": {command_name.lower()},
                    }


