import discord
from discord.ext import commands
import random


class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='play_rps', description="Play Rock Paper Scissors with the bot!")
    async def play_rps(self, ctx, bet: int):
        credit_system = self.bot.get_cog('CreditSystem')
        user_id = ctx.author.id
        user_credits = await credit_system.get_user_credits(user_id)

        if user_credits < 0:
            await ctx.respond('You don\'t have enough credits to play.')
            return
        if bet > user_credits:
            await ctx.respond('You don\'t have enough credits to bet that much. :( use /deposit :3')
            return

        await credit_system.update_user_credits(user_id, -bet)  # Withdraw the bet

        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)

        view = RockPaperScissorsView(self.bot, ctx, bot_choice, bet)
        message = await ctx.respond('Choose your move:', view=view)
        await view.wait()

        await message.delete()


class RockPaperScissorsView(discord.ui.View):
    def __init__(self, bot, ctx, bot_choice, bet):
        super().__init__(timeout=60)  # Set the timeout to 1 minute
        self.bot = bot
        self.ctx = ctx
        self.bot_choice = bot_choice
        self.bet = bet

    @discord.ui.button(label='Rock', style=discord.ButtonStyle.primary)
    async def rock(self, button, interaction):
        if interaction.user.id != self.ctx.author.id:  
            await interaction.response.send_message('You are not the one who started this game!', ephemeral=True)
            return
        await self.process_choice(interaction, 'rock')

    @discord.ui.button(label='Paper', style=discord.ButtonStyle.primary)
    async def paper(self, button, interaction):
        if interaction.user.id != self.ctx.author.id:  
            await interaction.response.send_message('You are not the one who started this game!', ephemeral=True)
            return
        await self.process_choice(interaction, 'paper')

    @discord.ui.button(label='Scissors', style=discord.ButtonStyle.primary)
    async def scissors(self, button, interaction):
        if interaction.user.id != self.ctx.author.id:  
            await interaction.response.send_message('You are not the one who started this game!', ephemeral=True)
            return
        await self.process_choice(interaction, 'scissors')

    async def process_choice(self, interaction, user_choice):
        credit_system = self.bot.get_cog('CreditSystem')
        user_id = self.ctx.author.id

        if user_choice == self.bot_choice:
            await credit_system.update_user_credits(user_id, self.bet * 1)  # Return the bet
            await interaction.response.edit_message(content=f'Tie! You and the bot both chose {user_choice}. Your bet of {self.bet} credits is returned.')
        elif (user_choice == 'rock' and self.bot_choice == 'scissors') or (user_choice == 'paper' and self.bot_choice == 'rock') or (user_choice == 'scissors' and self.bot_choice == 'paper'):
            await credit_system.update_user_credits(user_id, self.bet * 2)  # Add the win money
            await interaction.response.edit_message(content=f'You win! You chose {user_choice} and the bot chose {self.bot_choice}. You win {self.bet * 2} credits!')
        else:
            await interaction.response.edit_message(content=f'You lose! You chose {user_choice} and the bot chose {self.bot_choice}. You lose {self.bet} credits.')

        self.stop()  # Stop the view after a choice is made


def setup(bot):
    bot.add_cog(RockPaperScissors(bot))