#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot Template with Core Features
Learn from: PaulMarisOUMary/Discord-Bot (https://github.com/PaulMarisOUMary/Discord-Bot)
Created: 2023-11-20

A basic Discord bot with core features including:
- Slash commands
- Message commands
- Custom error handling
- Dynamic cog loading
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MyBot(commands.Bot):
    def __init__(self):
        # Enable all intents (for testing purposes)
        intents = discord.Intents.all()
        
        # Initialize bot with prefix commands and slash commands
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=os.getenv('DISCORD_APP_ID')
        )
        
        # Store startup timestamp
        self.start_time = discord.utils.utcnow()
        
    async def setup_hook(self):
        """Load extensions and sync commands"""
        # Load all cogs from cogs directory
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f'Loaded cog: {filename}')
        
        # Sync slash commands globally
        await self.tree.sync()
        logger.info('Synced slash commands globally')
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Bot is ready! Latency: {round(self.latency * 1000)}ms')

# Instantiate the bot
bot = MyBot()

@bot.tree.command(name='ping', description='Check bot latency')
async def ping(interaction: discord.Interaction):
    """Simple slash command to check bot latency"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'Pong! Latency: {latency}ms')

@bot.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    """Right-click context menu command"""
    await interaction.response.send_message(
        f'{member} joined at {discord.utils.format_dt(member.joined_at)}', 
        ephemeral=True
    )

@bot.event
async def on_command_error(ctx: commands.Context, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        logger.error(f'Error in command {ctx.command}: {error}')
        await ctx.send(f'An error occurred: {error}')

def main():
    """Main entry point"""
    # Load token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError('Missing DISCORD_TOKEN environment variable')
    
    bot.run(token)

if __name__ == '__main__':
    main()