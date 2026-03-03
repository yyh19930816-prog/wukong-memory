#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Discord Bot 核心功能实现
学习来源: GitHub仓库 PaulMarisOUMary/Discord-Bot
日期: 2023-10-25
功能描述: 实现一个基础的Discord机器人，包含动态加载、slash命令和按钮交互等核心功能
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# 初始化机器人
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 数据库模拟(实际项目中使用SQL数据库)
fake_db = {
    'guild_prefixes': {},
    'invite_tracker': {}
}

class DynamicCog(commands.Cog):
    """动态加载的Cog示例，展示核心功能"""
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="检查机器人延迟")
    async def ping(self, interaction: discord.Interaction):
        """Slash命令示例: 返回机器人延迟"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! 延迟: {latency}ms")
    
    @commands.command(name='setprefix')
    @commands.has_permissions(manage_guild=True)
    async def set_prefix(self, ctx, prefix: str):
        """设置自定义服务器前缀"""
        fake_db['guild_prefixes'][ctx.guild.id] = prefix
        await ctx.send(f"✅ 服务器前缀已设置为: `{prefix}`")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """邀请追踪器模拟功能"""
        guild = member.guild
        fake_db['invite_tracker'].setdefault(guild.id, {})
        fake_db['invite_tracker'][guild.id][member.id] = "模拟邀请码"
        logger.info(f"{member} 通过邀请加入 {guild.name}")

class ButtonView(discord.ui.View):
    """自定义按钮视图示例"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="点击我", style=discord.ButtonStyle.primary, emoji="✅")
    async def button_callback(self, interaction, button):
        await interaction.response.send_message("你点击了按钮!", ephemeral=True)

@bot.event
async def on_ready():
    """机器人启动时触发"""
    logger.info(f'已登录为 {bot.user.name} (ID: {bot.user.id})')
    logger.info('------')
    
    # 同步slash命令到Discord
    try:
        synced = await bot.tree.sync()
        logger.info(f"已同步 {len(synced)} 个slash命令")
    except Exception as e:
        logger.error(f"同步slash命令时出错: {e}")

@bot.command(name='menu')
async def send_menu(ctx):
    """发送带有按钮的菜单"""
    view = ButtonView()
    await ctx.send("这是一个包含按钮的消息!", view=view)

@bot.command(name='reload')
@commands.is_owner()
async def reload_cogs(ctx):
    """动态重新加载Cogs(模拟动态结构)"""
    try:
        await bot.reload_extension('dynamic_cog')  # 模拟动态加载
        await ctx.send('✅ 成功重新加载Cogs')
    except Exception as e:
        await ctx.send(f'❌