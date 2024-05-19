import random
import string
import time

import discord
from discord import option
from discord.ext import commands
from utils.database import Database
from utils.discord import generate_message_embed

LOWWORDS_LIST = [
    "birdy", "earl", "porky", "rizz",
    "gyat", "ohio", "sigma", "besse",
    "thirstys", "kroger", "kelei", "cammy",
    "extralifegaming", "brent",
]
SUPERLOW = [
    "gamerdog", "gdog", "jesse", "pottypoopoo", "<@188732205525106688>", "cope"
]

class LowHonorWordCounter(commands.Cog):
    """Commands for word count tracking"""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.low_honor_words = LOWWORDS_LIST
        self.super_low_words = SUPERLOW
        self.recent_low_messages = {}  # Dictionary to store recent low honor messages
        self.low_cooldowns = {}  # Dictionary to store low honor cooldowns

    def count_words(self, msg: str) -> int:
        """Return occurrences of low honor words in a given message"""
        count = 0
        msg = msg.lower().strip().split()
        for word in self.low_honor_words:
            count += msg.count(word)
        for word in self.super_low_words:
            if word in msg:
                count += 100  # Add 100 for the specific term
        return count if count >= 0 else 0

    async def get_member_word_count(self, guild_id, member_id) -> int:
        """Return number of low honor words said by member if tracked in database"""
        member = await self.db.member_in_database(guild_id, member_id)
        if not member:
            return 0
        return member["low_honor_word_count"]

    def get_msg_response(self, word_count: int) -> str:
        """Return bot message response"""
        if word_count < 1:
            return "<:LowHonor:1199342578085154886>"
        elif word_count < 3:
            return "<:LowHonor:1199342578085154886><:LowHonor:1199342578085154886>"
        elif word_count < 5:
            return "<:LowHonor:1199342578085154886><:LowHonor:1199342578085154886><:LowHonor:1199342578085154886>"
        else:
            return "<:LowHonor:1199342578085154886>"

    @commands.Cog.listener()
    async def on_message(self, message):
        """Detect low honor words"""
        if message.author == self.bot.user:  # Ignore reading itself.
            return
        if message.author.bot:  # Ignore spammy bots.
            return
        if message.webhook_id:  # Ignore webhooks.
            return

        guild_id = message.guild.id
        author_id = message.author.id
        msg = message.content
        current_time = time.time()

        # Check for low honor words in the message
        num_words = self.count_words(msg)

        # If no low honor words found, no further action is needed
        if num_words <= 0:
            return

        # Check if user is on cooldown for low honor words
        if author_id in self.low_cooldowns and current_time < self.low_cooldowns[author_id]:
            await message.reply("You are on cooldown for spamming low honor words. Please wait before sending more messages.")
            return

        # Check if guild has its own place in the database.
        if not await self.db.guild_in_database(guild_id):
            await self.db.create_database(guild_id, message.guild.name)

        # Spam prevention check for low honor words
        if author_id not in self.recent_low_messages:
            self.recent_low_messages[author_id] = []

        # Remove old messages
        self.recent_low_messages[author_id] = [
            (t, c) for t, c in self.recent_low_messages[author_id] if current_time - t <= 5
        ]

        self.recent_low_messages[author_id].append((current_time, num_words))

        if len(self.recent_low_messages[author_id]) > 5:
            self.low_cooldowns[author_id] = current_time + 300  # 5 minute cooldown
            await message.reply("You are sending messages too quickly. You are now on a 5-minute cooldown.")
            return

        # Database operations only if not on cooldown and message count is valid
        if not await self.db.member_in_database(guild_id, author_id):
            await self.db.create_member(guild_id, author_id, message.author.name)

        await self.db.increment_low_honor_word_count(guild_id, author_id, num_words)

        response = self.get_msg_response(word_count=num_words)
        await message.reply(f"{response}")

    def verify_mentions(self, mentions: discord.Member, ctx: discord.ApplicationContext) -> str:
        """Check if mention being passed into command is valid."""
        guild = ctx.guild
        if not guild.get_member(mentions.id):
            return "User not in server"
        else:
            return ""

    @commands.slash_command(
        name="count_low",
        description="Get a person's total low honor word count")
    @option(name="user", description="User to get count of", required=False)
    async def count(self, ctx, user: discord.Member = None):
        """Get a person's total low honor word count"""
        await ctx.defer()
        user = user if user else ctx.author

        # Validate mention.
        invalid_mention_msg = self.verify_mentions(user, ctx)
        if invalid_mention_msg:
            await ctx.respond(invalid_mention_msg)
            return

        # Fetch low honor word count of user if they have a count.
        word_count = await self.get_member_word_count(ctx.guild.id, user.id)
        await ctx.respond(embed=await generate_message_embed(
            f"**{user.display_name}** has said low honor words **{word_count:,}** time{'' if word_count == 1 else 's'}",
            type="info", ctx=ctx), ephemeral=True)

def setup(bot):
    bot.add_cog(LowHonorWordCounter(bot))
