@echo off
chcp 65001 >nul
echo 正在启动悟空 Agent Engine...
cd /d "%USERPROFILE%\.openclaw"
git pull origin main --quiet 2>nul

REM 注册计划任务
schtasks /create /tn "OpenClaw-AgentEngine-Wukong" /tr ""C:\Program Files\Python311\python.exe" -X utf8 "%USERPROFILE%\.openclaw\agent_engine_wukong.py"" /sc minute /mo 15 /ru SYSTEM /rl HIGHEST /f >nul 2>&1
schtasks /run /tn "OpenClaw-AgentEngine-Wukong" >nul 2>&1
echo 悟空 Agent Engine 已启动，每15分钟自主行动
pause
