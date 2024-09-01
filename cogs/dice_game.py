import discord
from discord.ext import commands
import random
import math

class DiceGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='roll_dice', description="Rolls a dice on six you win 5x ur bet!")
    async def roll_dice(self, ctx, bet: int):
        credit_system = self.bot.get_cog('CreditSystem')
        user_id = ctx.author.id
        user_credits = await credit_system.get_user_credits(user_id)
        
        if user_credits < 0:
            await ctx.respond('You don\'t have enough credits to play.')
            return
        if bet > user_credits:
            await ctx.respond('You don\'t have enough credits to bet that much. :( use /deposit :3')
            return
        roll = random.randint(1, 8) 
        if roll == 8: 
            await credit_system.update_user_credits(user_id, bet * 6)
            await ctx.respond(f'You rolled a 6! GG you win {bet * 6} credits!')
        elif roll == 6: 
            await credit_system.update_user_credits(user_id, -bet)
            await ctx.respond(f'You rolled a 5. You lose {bet} credit.')
        elif 7 <= roll <= 8: 
            roll_display = roll - 6 
            penalty = math.floor(roll / 3)
            await credit_system.update_user_credits(user_id, -bet)
            await ctx.respond(f'You rolled a {roll_display}. You lose {bet} credits.')
        else:
            await credit_system.update_user_credits(user_id, -bet)
            await ctx.respond(f'You rolled a {roll}. You lose {bet} credits.')


def setup(bot):
    bot.add_cog(DiceGame(bot))