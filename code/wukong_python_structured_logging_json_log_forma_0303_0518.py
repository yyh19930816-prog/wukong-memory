#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord Bot Core Implementation
Learning Source: PaulMarisOUMary/Discord-Bot (https://github.com/PaulMarisOUMary/Discord-Bot)
Date: 2023-11-15
Description: A lightweight Discord bot implementation with core features including:
- Slash commands
- Context menus
- Button interactions
- Basic error handling
- Per-guild prefix support
"""

import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            activity=discord.Game(name="with Discord.py")
        )
    
    async def get_prefix(self, message):
        """Dynamic prefix fetcher - can be extended to use per-guild prefixes"""
        return commands.when_mentioned_or('!')(self, message)
    
    async def setup_hook(self):
        """Sync slash commands and load cogs"""
        await self.load_extension('jishaku')  # Debugging tool
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = MyBot()

@bot.event
async def on_command_error(ctx, error):
    """Basic error handling for commands"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Simple ping command showing latency"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓 ({latency}ms)")

@bot.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    """Context menu to show when a member joined"""
    await interaction.response.send_message(
        f'{member} joined at {discord.utils.format_dt(member.joined_at)}',
        ephemeral=True
    )

class ConfirmationView(discord.ui.View):
    """Example view with buttons"""
    def __init__(self):
        super().__init__(timeout=30.0)
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Confirmed!", ephemeral=True)
        self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelled!", ephemeral=True)
        self.stop()

@bot.command(name='ask')
async def ask(ctx):
    """Example command with interactive buttons"""
    view = ConfirmationView()
    await ctx.send("Do you want to continue?", view=view)

if __name__ == '__main__':
    # Replace 'YOUR_TOKEN' with your actual bot token
    bot.run('YOUR_TOKEN')