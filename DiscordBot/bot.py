import os
import platform
import logging
import base64
from json import load
from pathlib import Path

import discord
from discord.ext import commands, tasks

# Fetch bot token.
with Path("../config.json").open() as f:
    config = load(f)

TOKEN = config["DISCORD_TOKEN"]


# DO NOT TOUCH - for running on hosting platform.
if TOKEN == "":
    TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = False

bot = commands.Bot(
    intents=intents,
    owner_id=1236297405079486514
)
# Logging (DEBUG clogs my stdout).
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter(
    "%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
            logging.info(f'Loaded {filename[:-3]}')
        except discord.errors.ExtensionFailed as e:
            logging.error(f'Failed to load {filename[:-3]}')
            logging.error(e.with_traceback(e.__traceback__))


@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} connected!")
    logger.info(f"Using Discord.py version {discord.__version__}")
    logger.info(f"Using Python version {platform.python_version()}")
    logger.info(
        f"Running on {platform.system()} {platform.release()} ({os.name})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"over your messages"))
    # status_loop.start()


@bot.slash_command(name="base64", description="Encode and decode in base64")
async def b64(ctx, task, string=None):
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


@bot.slash_command(name="ping", description="Pong back latency")
async def ping(ctx: discord.ApplicationContext):
    """Pong back latency"""
    await bot.wait_until_ready()
    await ctx.respond(
        f"_Pong!_ ({round(bot.latency * 1000, 1)} ms)",
        ephemeral=True,
        delete_after=15)

if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)
