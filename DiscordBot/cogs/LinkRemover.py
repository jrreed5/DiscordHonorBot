import re

from discord.ext import commands
from unalix import clear_url


class LinkCleanerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Extract links and clean
        urls = re.findall('(?P<url>https?://[^\\s]+)', message.content)
        cleaned = []
        for url in urls:
            if clear_url(url) != url:
                cleaned.append(clear_url(url))

        # Send message and add reactions
        if cleaned:
            text = 'This link has trackers! removing... \n' + '\n'.join(cleaned)
            await message.reply(text, mention_author=False)
def setup(bot):
    bot.add_cog(LinkCleanerCog(bot))
