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

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        # Delete message if original author clicked on trash reaction
        permissions = message.channel.guild.me.permissions_in(message.channel)
        if not permissions.manage_messages or message.reference is None:
            return
        channel = self.bot.get_channel(message.reference.channel_id)
        original = await channel.fetch_message(message.reference.message_id)
        if message.author == self.bot.user and user == original.author and reaction.emoji == '🗑':
            await reaction.message.delete()

def setup(bot):
    bot.add_cog(LinkCleanerCog(bot))
