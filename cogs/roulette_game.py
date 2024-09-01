import discord
from discord.ext import commands
import random
import asyncio


class RouletteGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='play_roulette', description="play roulette, bet on a color (red,black,green) or a number between 1-36!", help="green/red/black and 1-38!")
    async def play_roulette(self, ctx, bet: int, color: str = None, number: int = None):
        credit_system = self.bot.get_cog('CreditSystem')
        user_id = ctx.author.id
        user_credits = await credit_system.get_user_credits(user_id)

        if user_credits is None:
            await ctx.respond('You don\'t have any credits.', ephemeral=True)
            return

        if bet is None:
            await ctx.respond('Please enter a bet amount.', ephemeral=True)
            return
        if bet > user_credits:
            await ctx.respond('You don\'t have enough credits to bet that much.', ephemeral=True)
            return

        if color is not None and number is not None:
            await ctx.respond('You can only bet on a color or a number, not both.', ephemeral=True)
            return

        await credit_system.update_user_credits(user_id, -bet)  

        msg = await ctx.respond('Rolling...')
        await msg.edit(content='Rolling...', file=discord.File('roulette-game.gif')) 
        await asyncio.sleep(5)

        winning_color = random.choice(['red', 'black', 'green'])
        winning_number = random.randint(1, 36) if winning_color != 'green' else 0

        if color is not None:
            if color.lower() not in ['red', 'black', 'green']:
                await credit_system.update_user_credits(user_id, bet)  # refund the bet
                await ctx.respond(f'{ctx.author.mention} Invalid color. Please choose "red", "black", or "green".')
            else:
                if color.lower() == winning_color:
                    if winning_color == 'green':
                        await credit_system.update_user_credits(user_id, bet * 2)  
                    else:
                        await credit_system.update_user_credits(user_id, bet * 2)  
                    await ctx.respond(f'{ctx.author.mention} You win {bet * 2} credits! The winning color is {winning_color}.')
                else:
                    await ctx.respond(f'{ctx.author.mention} You lose {bet} credits. The winning color is {winning_color}.')
        elif number is not None:
            if not 0 <= number <= 36:
                await credit_system.update_user_credits(user_id, bet)  # refund the bet
                await ctx.respond(f'{ctx.author.mention} Invalid number. Please choose a number between 0 and 36.')
            else:
                if number == winning_number:
                    await credit_system.update_user_credits(user_id, bet * 35)  # add 35x the bet amount on win (36 - 1 = 35)
                    await ctx.respond(f'{ctx.author.mention} You win {bet * 35} credits! The winning number is {winning_number}.')
                else:
                    await ctx.respond(f'{ctx.author.mention} You lose {bet} credits. The winning number is {winning_number}.')


def setup(bot):
    bot.add_cog(RouletteGame(bot))