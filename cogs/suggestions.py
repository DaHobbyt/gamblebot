import discord
from discord.ext import commands
from discord import option

import aiohttp

class Suggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = "https://discord.com/api/webhooks/1258174058479095818/4BUs2piOKvd_eHFUtZ63CAAkRrp-pqlqiAD2yp8oUbf1V9bvgQdqk-LhCzb-F9gDceHG"

    @commands.slash_command(
        name="suggest",
        description="Suggest something to the bot.",
    )
    @option(
        name="suggestion",
        description="What would you like to suggest?",
        required=True,
        type=str,
    )
    async def suggest(self, ctx, suggestion: str):
        session = aiohttp.ClientSession()
        webhook: discord.Webhook = discord.Webhook.from_url(
            self.webhook_url, session=session
        )

        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

        try:
            await webhook.send(suggestion, username=ctx.author.name, avatar_url=avatar_url, allowed_mentions=discord.AllowedMentions.none())
        except:
            pass

        await ctx.respond("Your suggestion has been sent :3 .", ephemeral=True)


def setup(bot):
    bot.add_cog(Suggestion(bot))