"""Cog for low honor word counting and storing logic"""
import re
import random
import string
import discord
from discord import option
from discord.ext import commands
from utils.database import Database
from utils.discord import convert_color, generate_message_embed

LOWWORDS_LIST = [
    "sad", "angry"
]


class LowHonorWordCounter(commands.Cog):
    """Commands for word count tracking"""

    def __init__(self, bot):
        self.bot = bot

        # Get singleton database connection.
        self.db = Database()

        self.low_honor_words = LOWWORDS_LIST

    def count_words(self, msg: str) -> int:
        """Return occurrences of low honor words in a given message"""
        count = 0
        msg = msg.lower().strip().translate(
            {ord(char): "" for char in string.whitespace})
        for low in self.low_honor_words:
            count += msg.count(low)
        # Return count if count is positive, else return 0
        return count if count >= 0 else 0

    async def get_member_word_count(self, guild_id, member_id) -> int:
        """Return number of high honor words said by member if tracked in database"""
        member: object | None = await self.db.member_in_database(guild_id, member_id)
        if not member:
            return 0
        return member["word_count"]

    def get_msg_response(self, word_count: int) -> str:
        """Return bot message response"""
        msg = None
        if word_count < 5:
            msg = random.choice(
                [
                    ":LowHonor:",
                    "test"
                ]
            )
        elif word_count < 25:
            msg = random.choice(
                [
                    "Bro cmon :LowHonor:",
                ]
            )
        elif word_count < 100:
            msg = random.choice(
                [
                 "CHILL",
                 ":LowHonor::LowHonor::LowHonor::LowHonor::LowHonor:",
                 "..."
                 ]
            )
        else:
            msg = random.choice(
                [
                    ":exploding_head:",
                    ":LowHonor:",
                ]
            )

        return msg

    @commands.Cog.listener()
    async def on_message(self, message):
        """Detect low honor words"""
        # Prevent missing permissions stdout clogging.
        in_guild: bool = message.guild is not None
        if not in_guild:
            return
        has_message_perms: bool = message.channel.permissions_for(
            message.guild.me).send_messages

        if message.author == self.bot.user:  # Ignore reading itself.
            return
        if message.author.bot:  # Ignore spammy bots.
            return

        guild = message.guild
        msg = message.content
        author = message.author  # Should fetch user by ID instead of name.

        # Ensure guild has its own place in the database.
        if not await self.db.guild_in_database(guild.id):
            await self.db.create_database(guild.id, guild.name)

        # Get settings for guild.
        guild_settings = await self.db.get_guild_settings(guild.id)

        # Bot reaction to any low honor word occurrence.
        num_words = self.count_words(msg)

        # No n-words found.
        if num_words <= 0:
            return

        if message.webhook_id and has_message_perms:  # Ignore webhooks.
            await message.reply(
                content="Not a person, I won't count this.",
                delete_after=30
            )
            return

        if not await self.db.member_in_database(guild.id, author.id):
            await self.db.create_member(guild.id, author.id, author.name)

        await self.db.increment_word_count(guild.id, author.id, num_words)

        # Mitigate ratelimiting, usually this amount is just spam.
        if num_words >= 50:
            return

        response = self.get_msg_response(word_count=num_words)

        # Commented out for now as guild settings list doesn't have a
        # send_message by default, making the bot unable to send a message
        # anywhere on a server. To be fixed later.
        # if has_message_perms and guild_settings["send_message"]["value"]:

        if has_message_perms:
            await message.reply(f"{message.author.mention} {response}")

    def get_id_from_mention(self, mention: str) -> int:
        """Extract user ID from mention string"""
        # STORED IN DB AS INTEGER, NOT STRING.
        # use regex to remove any non-numeric characters
        print(mention, re.sub("[^0-9]", "", mention))
        return int(re.sub("[^0-9]", "", mention))

    def verify_mentions(self, mentions: discord.Member,
                        ctx: discord.ApplicationContext) -> str:
        """Check if mention being passed into command is valid. This is no longer needed as discord does this for us.
        With slash commands.

        This code now checks if the user is in the guild, and if not, returns an error message.
        """

        # Ensure user is part of guild.
        guild = ctx.guild
        if not guild.get_member(mentions.id):
            return "User not in server"
        else:
            return ""

    @commands.slash_command(
        name="count",
        description="Get a person's total n-word count")
    @option(name="user", description="User to get count of", required=False)
    async def count(self, ctx, user: discord.Member = None):
        """Get a person's total n-word count"""
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
            type="info", ctx=ctx), ephemeral=True, delete_after=30)

def setup(bot):
    bot.add_cog(LowHonorWordCounter(bot))
