# SPDX-FileCopyrightText: 2018-2025 Joonas Rautiola <mail@joinemm.dev>
# SPDX-License-Identifier: MPL-2.0
# https://git.joinemm.dev/miso-bot

import html
import io
import json
import random
from time import time
from typing import Optional
from urllib.parse import quote
from zoneinfo import ZoneInfo

import arrow
import discord
import orjson
from discord.ext import commands, tasks
from loguru import logger

from modules import emojis, exceptions, queries, util
from modules.misobot import MisoBot
from modules.ui import BaseButtonPaginator, Compliance, RowPaginator




class Utility(commands.Cog):
    """Utility commands"""

    def __init__(self, bot):
        self.bot: MisoBot = bot
        self.icon = "🔧"
        self.cache_needs_refreshing = True





    @commands.command()
    async def define(self, ctx: commands.Context, *, word):
        """Get definitions for a given word"""
        API_BASE_URL = "wordsapiv1.p.rapidapi.com"
        COLORS = ["226699", "f4900c", "553788"]

        headers = {
            "X-RapidAPI-Key": self.bot.keychain.RAPIDAPI_KEY,
            "X-RapidAPI-Host": API_BASE_URL,
        }
        url = f"https://{API_BASE_URL}/words/{word}"
        async with self.bot.session.get(url, headers=headers) as response:
            data = await response.json(loads=orjson.loads)

        if data.get("results") is None:
            raise exceptions.CommandWarning(f"No definitions found for `{word}`")

        content = discord.Embed(
            title=f":books: {word.capitalize()}",
            color=int(random.choice(COLORS), 16),
        )

        if data.get("pronunciation") is not None:
            if isinstance(data["pronunciation"], str):
                content.description = f"`{data['pronunciation']}`"
            elif data["pronunciation"].get("all") is not None:
                content.description = f"`{data['pronunciation'].get('all')}`"
            else:
                content.description = "\n".join(
                    f"{wt}: `{pro}`" for wt, pro in data["pronunciation"].items()
                )

        results = {}
        for result in data["results"]:
            word_type = result["partOfSpeech"]
            try:
                results[word_type].append(result)
            except KeyError:
                results[word_type] = [result]

        for category, definitions in results.items():
            category_definitions = []
            for n, category_result in enumerate(definitions, start=1):
                parts = [f"**{n}.** {category_result['definition'].capitalize()}"]

                if category_result.get("examples") is not None:
                    parts.append(f'> *"{category_result.get("examples")[0]}"*')

                if category_result.get("synonyms") is not None:
                    quoted_synonyms = [f"`{x}`" for x in category_result["synonyms"]]
                    parts.append(f"> Similar: {' '.join(quoted_synonyms)}")

                category_definitions.append("\n".join(parts))

            content.add_field(
                name=category.upper(),
                value="\n".join(category_definitions)[:1024],
                inline=False,
            )

        await ctx.send(embed=content)

    @commands.command()
    async def urban(self, ctx: commands.Context, *, word):
        """Get Urban Dictionary entries for a given word"""
        API_BASE_URL = "https://api.urbandictionary.com/v0/define"
        async with self.bot.session.get(
            API_BASE_URL, params={"term": word}
        ) as response:
            data = await response.json(loads=orjson.loads)

        if data["list"]:
            pages = []
            for entry in data["list"]:
                definition = entry["definition"].replace("]", "**").replace("[", "**")
                example = entry["example"].replace("]", "**").replace("[", "**")
                timestamp = entry["written_on"]
                content = discord.Embed(colour=discord.Colour.from_rgb(254, 78, 28))
                content.description = f"{definition}"

                if example != "":
                    content.add_field(name="Example", value=example)

                content.set_footer(
                    text=f"by {entry['author']} • "
                    f"{entry.get('thumbs_up')} 👍 {entry.get('thumbs_down')} 👎"
                )
                content.timestamp = arrow.get(timestamp).datetime
                content.set_author(
                    name=entry["word"],
                    icon_url="https://i.imgur.com/yMwpnBe.png",
                    url=entry.get("permalink"),
                )
                pages.append(content)

            await util.page_switcher(ctx, pages)

        else:
            await ctx.send(f"No definitions found for `{word}`")

    @commands.command(
        aliases=["tr", "trans"], usage="[source_lang]/[target_lang] <text>"
    )
    async def translate(self, ctx: commands.Context, *, text):
        """
        Papago and Google translator

        You can specify language pairs or let them be automatically detected.
        Default target language is english.

        You can also use '->' in place of '/' for language specification.

        Usage:
            >translate <sentence>
            >translate xx/yy <sentence>
            >translate /yy <sentence>
            >translate xx/ <sentence>
        """
        source = ""
        target = ""
        parts = text.split(" ", 1)
        if len(parts) > 1:
            languages, text = parts
            for separator in ["/", "->"]:
                if separator in languages:
                    source, target = languages.split(separator)
                    if source or target:
                        break
            else:
                # nothing was found, reconstruct the full text
                text = languages + " " + text

        # default target to english
        if not target:
            target = "en"

        # get the detected language if one was not supplied
        if not source:
            source = await self.detect_language(text)

        if source == target:
            raise exceptions.CommandInfo(
                f"Nothing to translate! Source and target languages match ({source})"
            )

        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            "key": self.bot.keychain.GCS_DEVELOPER_KEY,
            "target": target,
            "source": source,
            "q": text.split("\n"),
        }
        if source:
            params["source"] = source

        async with self.bot.session.get(url, params=params) as response:
            data = await response.json(loads=orjson.loads)

        # check for errors and raise if any are present
        error = data.get("error")
        if error:
            logger.error(error)
            raise exceptions.CommandError("Error: " + error["message"])

        translations = [
            "> " + html.unescape(trans["translatedText"])
            for trans in data["data"]["translations"]
        ]

        await ctx.send(f"`{source}->{target}`\n" + "\n".join(translations))

    async def detect_language(self, string: str):
        url = "https://translation.googleapis.com/language/translate/v2/detect"
        params = {"key": self.bot.keychain.GCS_DEVELOPER_KEY, "q": string[:1000]}

        async with self.bot.session.get(url, params=params) as response:
            data = await response.json(loads=orjson.loads)
            language = data["data"]["detections"][0][0]["language"]

        return language



    @commands.group(case_insensitive=True)
    async def steam(self, ctx: commands.Context):
        """Steam commands"""
        await util.command_group_help(ctx)

    @steam.command()
    async def market(self, ctx: commands.Context, *, search_term: str):
        """Search the steam community market"""
        MARKET_SEARCH_URL = "https://steamcommunity.com/market/search/render"

        headers = {"User-Agent": util.random_user_agent()}
        params = {"norender": 1, "count": 99, "query": search_term}
        async with self.bot.session.get(
            MARKET_SEARCH_URL, params=params, headers=headers
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if not data["results"]:
            raise exceptions.CommandInfo(
                f"No steam market listings found for `{search_term}`"
            )

        await MarketPaginator(data["results"]).run(ctx)

async def setup(bot):
    await bot.add_cog(Utility(bot))


class MarketPaginator(BaseButtonPaginator):
    MARKET_LISTING_URL = "https://steamcommunity.com/market/listings/"
    IMAGE_BASE_URL = "https://community.akamai.steamstatic.com/economy/image/"

    def __init__(self, entries: list[dict], **kwargs):
        super().__init__(entries=entries, per_page=1, **kwargs)

    async def format_page(self, entries: list[dict]):
        # entries should be a list with length of one so just grab the first element
        result = entries[0]
        asset = result["asset_description"]
        item_hash = quote(asset["market_hash_name"])
        market_link = f"{self.MARKET_LISTING_URL}{asset['appid']}/{item_hash}"
        return {
            "embed": discord.Embed(
                description=asset["type"],
                color=int("68932f", 16),
            )
            .set_author(
                name=result["name"],
                url=market_link,
            )
            .set_thumbnail(url=self.IMAGE_BASE_URL + asset["icon_url"])
            .add_field(name="Starting at", value=result["sell_price_text"])
            .add_field(name="Listings", value=str(result["sell_listings"]))
            .set_footer(icon_url=result["app_icon"], text=result["app_name"])
        }




