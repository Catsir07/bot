import discord
from discord.ext import commands, tasks
import asyncio

# Setup Intents
intents = discord.Intents.default()
intents.members = True  # Required to DM everyone
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

# Global variables to track status
dm_stats = {
    "total": 0,
    "sent": 0,
    "failed": 0,
    "active": False
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def dmall(ctx):
    # Step 1: Ask for the message
    await ctx.send("What message would you like to send to everyone?")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg_content = await bot.wait_for('message', check=check, timeout=60.0)
        
        # Step 2: Confirmation
        await ctx.send(f"Are you sure you want to send this to everyone? Type **YES** to confirm or **NO** to cancel.")
        confirm = await bot.wait_for('message', check=check, timeout=30.0)

        if confirm.content.upper() == "YES":
            members = [m for m in ctx.guild.members if not m.bot]
            dm_stats["total"] = len(members)
            dm_stats["sent"] = 0
            dm_stats["failed"] = 0
            dm_stats["active"] = True
            
            await ctx.send(f"Starting DM process for {len(members)} members. Use `.dmstatus` to track progress.")
            
            for member in members:
                try:
                    await member.send(msg_content.content)
                    dm_stats["sent"] += 1
                except:
                    dm_stats["failed"] += 1
                # Small delay to prevent rate limits
                await asyncio.sleep(0.1)
            
            dm_stats["active"] = False
            await ctx.send("DM All process completed.")
        else:
            await ctx.send("Cancelled.")

    except asyncio.TimeoutError:
        await ctx.send("Timed out. Please try again.")

@bot.command()
async def bothelp(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.add_field(name=".dmall", value="Sends a DM to every member in the server.", inline=False)
    embed.add_field(name=".dmstatus", value="Shows the live status of the DM activity.", inline=False)
    embed.add_field(name=".bothelp", value="Shows this help menu.", inline=False)
    # Adding your specific features
    embed.add_field(name=".stock", value="Check current stock.", inline=False)
    embed.add_field(name=".steamstockadd", value="Add items to steam stock.", inline=False)
    embed.set_footer(text="Admin Only: .sendsteam")
    await ctx.send(embed=embed)

@bot.command()
async def dmstatus(ctx):
    embed = discord.Embed(title="DM Activity Status", color=discord.Color.green())
    embed.description = (
        f"**Total** - {dm_stats['total']}\n"
        f"**Sent** - {dm_stats['sent']}\n"
        f"**Failed** - {dm_stats['failed']}"
    )
    
    status_msg = await ctx.send(embed=embed)

    # Auto-update loop
    while dm_stats["active"]:
        await asyncio.sleep(1)
        new_embed = discord.Embed(title="DM Activity Status", color=discord.Color.green())
        new_embed.description = (
            f"**Total** - {dm_stats['total']}\n"
            f"**Sent** - {dm_stats['sent']}\n"
            f"**Failed** - {dm_stats['failed']}"
        )
        await status_msg.edit(embed=new_embed)
    
    await ctx.send("Final status reached.")

bot.run('MTUwOTUwMjE2NTU5NTU4NjY3MQ.G1EFTI.f0zWxMQ4Oy771OKlIxQktznGuc4OAr5e45aLkA')
