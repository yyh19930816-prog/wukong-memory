#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 实现代码
学习来源：https://github.com/PaulMarisOUMary/Discord-Bot
创建日期：2023-06-15
功能说明：基于discord.py的Discord机器人，包含核心功能如Slash命令、视图按钮和错误处理
"""

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

# 机器人配置
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # 替换为你的机器人token
GUILD_ID = discord.Object(id=123456789)  # 替换为你的服务器ID

class MyBot(commands.Bot):
    def __init__(self):
        # 设置命令前缀为'!'
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # 添加初始cog(功能模块)
        self.initial_extensions = [
            'cogs.admin',
            'cogs.fun'
        ]
    
    async def setup_hook(self):
        """设置钩子函数，用于初始化机器人"""
        # 同步slash命令到特定服务器(GUILD_ID)
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        
        # 加载初始cog模块
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                print(f"成功加载扩展 {ext}")
            except Exception as e:
                print(f"加载扩展 {ext} 失败: {e}")
    
    async def on_ready(self):
        """当机器人准备就绪时触发"""
        print(f'已登录为 {self.user} (ID: {self.user.id})')
        print('------')

# 创建机器人实例
bot = MyBot()

# 定义slash命令
@bot.tree.command()
async def hello(interaction: discord.Interaction):
    """打招呼的slash命令"""
    await interaction.response.send_message('你好! 我是你的Discord机器人!')

# 定义带按钮的视图
class MyView(View):
    def __init__(self):
        super().__init__(timeout=None)  # 禁用超时
        
    @discord.ui.button(label="点击我!", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("你点击了按钮!")

# 定义带按钮的命令
@bot.tree.command()
async def button(interaction: discord.Interaction):
    """发送带按钮的消息"""
    view = MyView()
    await interaction.response.send_message("这是一个带按钮的消息!", view=view)

# 添加错误处理
@bot.event
async def on_command_error(ctx, error):
    """全局命令错误处理"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("命令不存在!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("缺少必要的参数!")
    else:
        await ctx.send(f"发生错误: {str(error)}")
        print(f"命令错误: {error}")

# 运行机器人
if __name__ == '__main__':
    bot.run(BOT_TOKEN)