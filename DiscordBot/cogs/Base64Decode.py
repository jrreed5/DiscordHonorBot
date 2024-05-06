import base64
import discord
from discord.ext import commands, tasks

class Base64Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="base64", description="Encode and decode in base64")
    async def b64(self, ctx, task, string=None):
        if ctx.author.nick is None:
            username = ctx.author.name
        else:
            username = ctx.author.nick

        if task == 'encode':
            string_bytes = string.encode("ascii")

            b64bytes = base64.b64encode(string_bytes)
            b64string = b64bytes.decode("ascii")

            embed = discord.Embed(title=f"Encoded string for {username}:",
                                  description=b64string, colour=discord.Colour.green())
            await ctx.send(embed=embed)

        if task == 'decode':
            b64bytes = string.encode("ascii")

            string_bytes = base64.b64decode(b64bytes)
            decoded_string = string_bytes.decode("ascii")

            embed = discord.Embed(title=f"Decoded string for {username}:",
                                  description=decoded_string, colour=discord.Colour.green())
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Base64Cog(bot))
