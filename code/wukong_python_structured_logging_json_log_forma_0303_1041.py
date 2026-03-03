#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord Bot Core Functionality Implementation
Learned from: PaulMarisOUMary/Discord-Bot (https://github.com/PaulMarisOUMary/Discord-Bot)
Date: 2023-11-15
Features:
- Basic Discord bot with commands and event handling
- Slash commands support
- Custom prefix per guild
- Error handling
"""

import os
import discord
from discord.ext import commands
from discord import app_commands

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

class MyBot(commands.Bot):
    def __init__(self):
        # Set up bot with default prefix and all intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None  # Disable default help command
        )
    
    async def get_prefix(self, message):
        """Dynamic prefix getter (would be guild-specific in full implementation)"""
        return '!'  # In full version, this would check a database
    
    async def setup_hook(self):
        """Called when bot is starting up to sync slash commands"""
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")
    
    async def on_ready(self):
        """Called when bot connects to Discord"""
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

# Initialize bot
bot = MyBot()

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        # Log full error traceback
        print(f"Ignoring exception in command {ctx.command}:", flush=True)
        error.__traceback__

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Slash command to check bot latency"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms")

@bot.command()
async def hello(ctx):
    """Regular text command example"""
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    """Admin-only shutdown command"""
    await ctx.send("Shutting down...")
    await bot.close()

def main():
    """Main function to start the bot"""
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("Invalid Discord token provided")
    except KeyboardInterrupt:
        print("Bot shutting down...")
    finally:
        print("Bot has stopped")

if __name__ == "__main__":
    main()