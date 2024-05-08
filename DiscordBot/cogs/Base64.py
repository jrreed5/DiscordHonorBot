import base64
import discord
from discord import option
from discord.ext import commands, tasks


class Base64(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.slash_command(
    name="b64",
    description="Encode and decode in base64"
)
@option(name="task",description="Task to perform (encode or decode)",required=True)
@option(name="string",description="String to encode or decode",required=True)
async def b64(self, ctx, task, string=None, user: discord.Member = None):
    """Encode and decode in base64"""
    await ctx.defer()

    username = user.display_name if user else ctx.author.display_name
    user_info = f"for {username}"

    if task == 'encode':
        string_bytes = string.encode("ascii")
        b64bytes = base64.b64encode(string_bytes)
        b64string = b64bytes.decode("ascii")

        embed_title = f"Encoded string {user_info}:"
        embed_description = b64string

    elif task == 'decode':
        b64bytes = string.encode("ascii")
        string_bytes = base64.b64decode(b64bytes)
        decoded_string = string_bytes.decode("ascii")

        embed_title = f"Decoded string {user_info}:"
        embed_description = decoded_string

    await ctx.respond(
        embed=discord.Embed(
            title=embed_title,
            description=embed_description,
            colour=discord.Colour.green()
        ),
        ephemeral=True
    )

def setup(bot):
    bot.add_cog(Base64(bot))
