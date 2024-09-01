import discord
from discord.ext import commands
import aiosqlite
import asyncio


class CreditSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelist_ids = [449194683575435264, 724539085632438273]  

    async def create_database(self):
        async with aiosqlite.connect("credits.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    credits INTEGER DEFAULT 0
                )
            """)

    async def log_user_credits(self, user_id):
        async with aiosqlite.connect("credits.db") as db:
            await db.execute("""
                INSERT INTO users (user_id, credits)
                SELECT?, 0
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM users
                    WHERE user_id =?
                )
            """, (user_id, user_id))
            await db.commit()
    
    async def get_user_credits(self, user_id):
        async with aiosqlite.connect("credits.db") as db:
            async with db.execute("SELECT credits FROM users WHERE user_id =?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                else:
                    return 0
                
    async def update_user_credits(self, user_id, amount):
        async with aiosqlite.connect("credits.db") as db:
            await db.execute("""
                UPDATE users
                SET credits = credits + ?
                WHERE user_id = ?
            """, (amount, user_id))
            if db.total_changes == 0: 
                await db.execute("""
                    INSERT INTO users (user_id, credits)
                    VALUES (?, ?)
                """, (user_id, amount))
            await db.commit()

    async def get_leaderboard(self):
        async with aiosqlite.connect("credits.db") as db:
            async with db.execute("SELECT user_id, credits FROM users ORDER BY credits DESC") as cursor:
                rows = await cursor.fetchall()
                return rows

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log_user_credits(member.id)

    @commands.slash_command(name="addbal", decription="adds credits to user (owner only)")
    async def add_credits(self, ctx, user: discord.User, amount: int):
        if ctx.author.id not in self.whitelist_ids:
            await ctx.respond("You are not authorized to use this command.")
            return

        user_id = user.id
        async with aiosqlite.connect("credits.db") as db:
            async with db.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await db.execute("INSERT INTO users(user_id, credits) VALUES(?, ?)", (user_id, amount))
                else:
                    current_credits = row[0]
                    balls = current_credits + amount
                    await db.execute("UPDATE users SET credits = ? WHERE user_id = ?", (balls, user_id))
                await db.commit()

        await ctx.respond(f"Added {amount} credits to {user.mention}.")

    @commands.slash_command(name="bal", description="checks user credits!")
    async def check_credits(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        user_id = user.id
        await self.log_user_credits(user_id) 
        credits = await self.get_user_credits(user_id)
        await ctx.respond(f"{user.mention} has {credits} credits.", ephemeral=True)

    @commands.slash_command(name="leaderboard", description="Gets the credits leaderboard!")
    async def leaderboard(self, ctx):
        try:
            leaderboard = await self.get_leaderboard()
            embed = discord.Embed(title="Credits Leaderboard")
            for i, (user_id, credits) in enumerate(leaderboard[:5], start=1):
                try:
                    user = await self.bot.fetch_user(user_id)
                    username = user.name
                except discord.NotFound:
                    username = "Unknown User"
                except discord.HTTPException as e:
                    if e.status == 404:
                        username = "Unknown User"
                    else:
                        raise
                embed.add_field(name=f"{i}. {username}", value=f"Credits: {credits}", inline=False)
            await ctx.respond(embed=embed)
        except discord.errors.ApplicationCommandInvokeError as e:
            if e.original.status == 10062:
                await ctx.respond("Error: Unknown interaction. Please try again.")
            else:
                raise
            
    @commands.slash_command(name="removebal", description="removes credits from user (owner only)")
    async def remove_credits(self, ctx, user: discord.User, amount: int):
        if ctx.author.id not in self.whitelist_ids:
            await ctx.respond("You are not authorized to use this command.", ephemeral=True)
            return

        user_id = user.id
        await self.log_user_credits(user_id) 
        current_credits = await self.get_user_credits(user_id)
        if current_credits < amount:
            await ctx.respond(f"{user.mention} does not have enough credits to remove {amount} credits.")
            return

        async with aiosqlite.connect("credits.db") as db:
            await db.execute("UPDATE users SET credits = credits - ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

        await ctx.respond(f"Removed {amount} credits from {user.mention}.")



    @commands.slash_command(name="deletebal", description="removes a user's entire balance (owner only)")
    async def delete_credits(self, ctx, user: discord.User):
        if ctx.author.id not in self.whitelist_ids:
            await ctx.respond("You are not authorized to use this command.", ephemeral=True)
            return

        user_id = user.id
        await self.log_user_credits(user_id) 
        async with aiosqlite.connect("credits.db") as db:
            await db.execute("UPDATE users SET credits = 0 WHERE user_id =?", (user_id,))
            await db.commit()

        await ctx.respond(f"Removed entire balance of {user.mention}.")


    @commands.slash_command(name="pay", description="pay another user some credits!")
    async def pay(self, ctx, user: discord.User, amount: int):
        user_id = user.id
        author_id = ctx.author.id
        await self.log_user_credits(author_id)
        await self.log_user_credits(user_id)
        author_credits = await self.get_user_credits(author_id)
        if author_credits < amount:
            await ctx.respond("You don't have enough credits to pay that amount.")
            return

        async with aiosqlite.connect("credits.db") as db:
            await db.execute("UPDATE users SET credits = credits - ? WHERE user_id = ?", (amount, author_id))
            await db.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

        await ctx.respond(f"Paid {amount} credits to {user.mention}.")


    @commands.slash_command(name="deleteall", description="deletes every user's entire balance (owner only)")
    async def delete_all_credits(self, ctx):
        if ctx.author.id not in self.whitelist_ids:
            await ctx.respond("You are not authorized to use this command.", ephemeral=True)
            return

        async with aiosqlite.connect("credits.db") as db:
            await db.execute("UPDATE users SET credits = 0")
            await db.commit()

        await ctx.respond("Deleted entire balance of all users.")


def setup(bot):
    cog = CreditSystem(bot)
    bot.add_cog(cog)
    bot.loop.create_task(cog.create_database())