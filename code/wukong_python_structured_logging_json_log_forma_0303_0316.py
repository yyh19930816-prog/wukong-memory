#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot Core Implementation
Learned from: PaulMarisOUMary/Discord-Bot (GitHub)
Date: 2024-04-15
Description: A Discord bot with slash commands, custom error handling, 
             logging and admin features based on README specifications.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import sqlite3
import traceback
import os
from typing import Optional

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_bot')

class DiscordBot(commands.Bot):
    """Main bot class extending discord.py's Bot with additional features"""
    
    def __init__(self, command_prefix='!', intents=None):
        """Initialize bot with default settings"""
        intents = intents or discord.Intents.default()
        intents.members = True  # Required for invite tracking
        
        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix),
            intents=intents,
            help_command=None  # Custom help will be implemented
        )
        
        # Setup SQLite database
        self.db = sqlite3.connect('bot_data.db')
        self._setup_database()
        
        # Load cogs dynamically
        self.load_extensions()
        
    def _setup_database(self):
        """Initialize database tables"""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_prefixes (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invite_tracking (
                guild_id INTEGER,
                inviter_id INTEGER,
                uses INTEGER,
                PRIMARY KEY (guild_id, inviter_id)
            )
        ''')
        self.db.commit()
    
    def load_extensions(self):
        """Dynamically load all Python files in cogs directory as extensions"""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f'Successfully loaded cog: {filename}')
                except Exception as e:
                    logger.error(f'Failed to load cog {filename}: {e}')
    
    async def on_ready(self):
        """Called when bot is connected and ready"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.change_presence(activity=discord.Game(name="/help"))
        
    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f'Error in command {ctx.command}: {error}')
        await ctx.send(f'❌ Error: {str(error)}')

bot = DiscordBot()

@bot.tree.command(name='ping', description="Check bot's latency")
async def ping(interaction: discord.Interaction):
    """Simple slash command to check bot latency"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'🏓 Pong! {latency}ms')

@bot.command(name='prefix')
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, prefix: str):
    """Set custom prefix for guild"""
    cursor = bot.db.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO guild_prefixes VALUES (?, ?)',
        (ctx.guild.id, prefix)
    )
    bot