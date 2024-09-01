import discord
from discord.ext import commands
import asyncio

class TicketCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_channels = {}
        self.cooldowns = {}

    @commands.slash_command(name="withdraw")
    async def withdraw(self, ctx, amount: int):
        if ctx.author.id in self.cooldowns:
            await ctx.respond("You have a ticket cooldown. Please wait 10 minutes before creating a new ticket.")
            return
        if ctx.author.id in self.ticket_channels:
            await ctx.respond("You already have an open ticket. Please close it before creating a new one.")
            return

        category_id = 1258091187915722934  
        category = ctx.guild.get_channel(category_id)

        channel = await category.create_text_channel(f"withdraw-{ctx.author.name}")
        self.ticket_channels[ctx.author.id] = channel
        await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
        await ctx.respond(f"Creating channel {channel.mention}")

        role_id = 1258087105926529107  
        role = ctx.guild.get_role(role_id)
        await channel.send(f"{role.mention}")

        embed = discord.Embed(title=f"Withdrawal Request", description=f"{ctx.author.mention} wants to withdraw {amount} credits")
        view = TicketView(ctx.author)

        message = await channel.send(embed=embed, view=view)

        self.cooldowns[ctx.author.id] = True
        await asyncio.sleep(600)
        del self.cooldowns[ctx.author.id]

    @commands.slash_command(name="deposit")
    async def deposit(self, ctx, amount: int):
        if ctx.author.id in self.cooldowns:
            await ctx.respond("You have a ticket cooldown. Please wait 10 minutes before creating a new ticket.")
            return
        if ctx.author.id in self.ticket_channels:
            await ctx.respond("You already have an open ticket. Please close it before creating a new one.")
            return

        category_id = 1258091187915722934  
        category = ctx.guild.get_channel(category_id)

        channel = await category.create_text_channel(f"deposit-{ctx.author.name}")
        self.ticket_channels[ctx.author.id] = channel
        await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
        await ctx.respond(f"Creating channel {channel.mention}")

        role_id = 1258087105926529107  
        role = ctx.guild.get_role(role_id)
        await channel.send(f"{role.mention}")

        embed = discord.Embed(title=f"Deposit Request", description=f"{ctx.author.mention} wants to deposit {amount} credits")
        view = TicketView(ctx.author)

        message = await channel.send(embed=embed, view=view)

        self.cooldowns[ctx.author.id] = True
        await asyncio.sleep(600)
        del self.cooldowns[ctx.author.id]

class TicketView(discord.ui.View):
    def __init__(self, user, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.user = user
        self.allowed_role_id = 1258087105926529107  

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close_button_callback(self, button, interaction):
        if interaction.user.get_role(self.allowed_role_id) is not None:
            channel_id = interaction.channel_id
            await interaction.channel.delete()
            del interaction.guild.cog.ticket_channels[self.user.id] 
            await interaction.response.defer()
        else:
            await interaction.response.send_message("You don't have permission to close this request", ephemeral=True)


    
def setup(bot):
    bot.add_cog(TicketCommand(bot))