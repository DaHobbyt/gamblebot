import discord
from discord.ext import commands
import random
from discord.ui import Button, View
import asyncio

class CrashGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crash_games = {}

    @commands.slash_command(name='crash', description="Play a game of crash!")
    async def crash(self, ctx, bet: int):
        credit_system = self.bot.get_cog('CreditSystem')
        user_id = ctx.author.id
        user_credits = await credit_system.get_user_credits(user_id)

        if user_credits < 0:
            await ctx.respond('You don\'t have enough credits to play. Please deposit some credits and try again!')
            return
        if bet > user_credits:
            await ctx.respond(f'You don\'t have enough credits to bet that much. You have {user_credits} credits. Please try again!')
            return

        await credit_system.update_user_credits(user_id, -bet)  

        self.crash_games[ctx.author.id] = {'bet': bet, 'multiplier': 1.0, 'channel_id': ctx.channel.id, 'message_id': None}
        message = await ctx.respond(embed=self.create_embed('Game started!', f'Your current multiplier is {self.crash_games[ctx.author.id]["multiplier"]:.2f}x.'))
        self.crash_games[ctx.author.id]['message_id'] = message.id
        button = Button(label='Cash Out', style=discord.ButtonStyle.green)
        button.callback = self.cash_out_callback
        view = View()
        view.add_item(button)
        await message.edit(view=view)

        if random.random() < 0.25:
            game = self.crash_games[ctx.author.id]
            if 'multiplier' in game and 'bet' in game:
                del self.crash_games[ctx.author.id]
                await message.edit(embed=self.create_embed('Game Over!', f'{ctx.author.mention} lost {game["bet"]} credits. Better luck next time!'), view=None)
            else:
                await message.edit(embed=self.create_embed('Error', 'Game data is incomplete. Please try again!'), view=None)
        else:
            while ctx.author.id in self.crash_games:
                crash_chance = 1 - (1 / self.crash_games[ctx.author.id].get('multiplier', 1.0))
                if random.random() < crash_chance:
                    game = self.crash_games[ctx.author.id]
                    if 'multiplier' in game and 'bet' in game:
                        del self.crash_games[ctx.author.id]
                        await message.edit(embed=self.create_embed('Game Over!', f'{ctx.author.mention} lost {game["bet"]} credits. Better luck next time!'), view=None)
                    else:
                        await message.edit(embed=self.create_embed('Error', 'Game data is incomplete. Please try again!'), view=None)
                    break
                else:
                    if 'multiplier' in self.crash_games[ctx.author.id]:
                        self.crash_games[ctx.author.id]['multiplier'] = round(self.crash_games[ctx.author.id]['multiplier'] * 1.1, 2)
                    await message.edit(embed=self.create_embed('Game Continues!', f'Your current multiplier is {self.crash_games[ctx.author.id].get("multiplier", 1.0):.2f}x.'))
                    await asyncio.sleep(1)


    async def cash_out_callback(self, interaction):
        user_id = interaction.user.id
        if user_id in self.crash_games:
            game = self.crash_games[user_id]
            if 'multiplier' in game and 'bet' in game:
                winnings = round(game['bet'] * game['multiplier'])
                await self.bot.get_cog('CreditSystem').update_user_credits(user_id, winnings)  
                del self.crash_games[user_id]
                await interaction.response.edit_message(embed=self.create_embed('You Cashed Out!', f'{interaction.user.mention} won {winnings} credits! Congratulations!'), view=None)
            else:
                await interaction.response.edit_message(embed=self.create_embed('Error', 'Game data is incomplete. Please try again!'), view=None)
        else:
            await interaction.response.edit_message(embed=self.create_embed('Error', 'You are not in a game. Please start a new game!'), view=None)

    def create_embed(self, title, description):
        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())
        return embed

def setup(bot):
    bot.add_cog(CrashGame(bot))