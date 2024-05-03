"""Cog for storing low honor word count stats and bot meta code"""
import discord
from discord.ext import commands
from discord import option
from utils.database import Database
from utils.paginator import paginator
from utils.discord import convert_color, generate_message_embed, generate_color
from discord.ext.pages import Paginator
from discord.ui import Button, View
import platform
import os

HEX_OG_BLURPLE = 0x7289DA


class Meta(commands.Cog):
    """Commands for bot stats and other meta stuff"""

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot

        # Get singleton database connection.
        self.db = Database()

        self.MAX_PER_PAGE = 10

    top = discord.SlashCommandGroup(
        name="guild", description="View scoreboards for the current guild")

    @option(name="limit", description="The number of users to show", type=int,
            required=False, default=10)
    async def top_guild_user(self, ctx: discord.ApplicationContext, limit: int = 10):
        await ctx.defer()
        if limit < 10:
            await ctx.respond(embed=await generate_message_embed("Limit should be at least 10!", type="error", ctx=ctx),
                              ephemeral=True, delete_after=5)
            return
        elif limit > 100:
            await ctx.respond(
                embed=await generate_message_embed("Limit cannot exceed 100!", type="error", ctx=ctx),
                ephemeral=True, delete_after=5)
            return

        top_members = await self.db.get_member_list(ctx.guild.id)
        server_low_honor_word_total = await self.db.get_nword_server_total(ctx.guild.id)
        embed_data = {
            "title": f"Top users in {ctx.guild.name}",
            "description": f"I have seen **{server_low_honor_word_total}** low honor words in this server!\n"
                           f"That's **{round(server_low_honor_word_total / await self.db.get_global_low_honor_word_count() * 100, 3)}%**"
                           f" of all low honor words.",
            "color": HEX_OG_BLURPLE
        }
        data_vals = {"type": "rankings"}
        pages = paginator(limit, self.MAX_PER_PAGE, embed_data,
                          top_members, data_vals)
        page_iterator = Paginator(pages=pages, loop_pages=True)
        await page_iterator.respond(ctx.interaction)

    @option(name="limit", description="The number of users to show", type=int,
            required=False, default=10)
    async def top_global_user(self, ctx: discord.ApplicationContext, limit: int = 10):
        await ctx.defer()
        if limit < 10:
            await ctx.respond(embed=await generate_message_embed("Limit should be at least 10!", type="error", ctx=ctx),
                              ephemeral=True, delete_after=5)
            return
        elif limit > 100:
            await ctx.respond(
                embed=await generate_message_embed("Limit cannot exceed 100!", type="error", ctx=ctx),
                ephemeral=True, delete_after=5)
            return

def setup(bot):
    bot.add_cog(Meta(bot))
