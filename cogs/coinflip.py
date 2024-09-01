import discord
from discord.ext import commands
import random

class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(name='coinflip', description="heads or tails? 2x ur bet on win! 0x ur bet on lose!")
    async def coinflip(self, ctx, bet: int, choice: str):
        credit_system = self.bot.get_cog('CreditSystem')
        user_id = ctx.author.id
        user_credits = await credit_system.get_user_credits(user_id)
        
        if user_credits < 0:
            await ctx.respond('You don\'t have enough credits to play. use /deposit :3', ephemeral=True)
            return
        if bet > user_credits:
            await ctx.respond('You don\'t have enough credits to bet that much. use /deposit :3', ephemeral=True)
            return
        
        if choice.lower() not in ['heads', 'tails']:
            await ctx.respond('Invalid choice. Please type "heads" or "tails".', ephemeral=True)
            return
        
        roll = random.choice(['heads', 'tails'])
        
        if random.random() < 0.4:
            if choice.lower() == roll:
                await credit_system.update_user_credits(user_id, bet * 2)
                await ctx.respond(f'You chose {choice} and the coin landed on {roll}! You win {bet * 2} credits!')
            else:
                await credit_system.update_user_credits(user_id, -bet)
                await ctx.respond(f'You chose {choice} but the coin landed on {roll}. You lose {bet} credits.')
        else:
            if choice.lower() == 'heads':
                roll = 'tails'
            else:
                roll = 'heads'
            await credit_system.update_user_credits(user_id, -bet)
            await ctx.respond(f'You chose {choice} but the coin landed on {roll}. You lose {bet} credits.')

def setup(bot):
    bot.add_cog(CoinFlip(bot))