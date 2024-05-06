import random
import string
import discord
from discord import option
from discord.ext import commands
from utils.database import Database
from utils.discord import convert_color, generate_message_embed

class TotalHonor(commands.Cog):
    async def generate_honor_bar(self, total_honor):
        """Generate a bar with 5 points to represent honor, with zero in the middle."""
        # Calculate the distance from zero
        distance_from_zero = min(2, max(-2, total_honor // 10000))

        # Initialize the bar string
        honor_bar = "0---------------0"

        # Replace the appropriate dash with "⬤" for the middle point
        middle_point_index = 2 + distance_from_zero * 2
        honor_bar = honor_bar[:middle_point_index] + "⬤" + honor_bar[middle_point_index + 1:]

        return honor_bar

    @commands.slash_command(
        name="count_total",
        description="Get a user's total honor word count")
    @option(name="user", description="User to get count of", required=False)
    async def count_total(self, ctx, user: discord.Member = None):
        """Get a person's total high honor word count"""
        await ctx.defer()
        user = user if user else ctx.author
        # Validate mention.
        invalid_mention_msg = self.verify_mentions(user, ctx)
        if invalid_mention_msg:
            await ctx.respond(invalid_mention_msg)
            return

        # Fetch total honor word count of user if they have a count.
        total_honor = await Database.total_honor(ctx.guild.id, user.id)
        honor_bar = await self.generate_honor_bar(total_honor)
        embed = await generate_message_embed(
            f"**{user.display_name}**'s total honor: {total_honor}\n\n{honor_bar}",
            type="info", ctx=ctx)
        await ctx.respond(embed=embed, ephemeral=True, delete_after=30)

def setup(bot):
    bot.add_cog(TotalHonor(bot))
