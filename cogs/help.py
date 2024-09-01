import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='help', description="Displays information about all the games!")
    async def help(self, ctx):
        embed = discord.Embed(title="Games Help", description="Here are all the games you can play!", color=0x0000FF)

        embed.add_field(name="/roll_dice", value="Roll a dice, if you roll a 6 you win 5x your bet!", inline=False)
        embed.add_field(name="/coinflip", value="Flip a coin, heads or tails. Bet on the outcome and win double your bet!", inline=False)
        embed.add_field(name="/play_roulette", value="Play a game of roulette, bet on the color (red/black/green) its a 33/33/33 chance! , and/or on the number (1-38) 36x on win")
        embed.add_field(name="/deposit, withdraw", value="manually deposit stuff")
        embed.add_field(name="/play_rps", value="Plays rps against bot! win 2x credits on win, return on tie!")
        embed.set_footer(text="Made by dahobber! DM for custom bots! :3")
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))