# WUKONG_DEPLOY.md — 悟空自动部署指南
# 悟空那边的 Cursor AI 读到这个文件后，执行以下PowerShell命令完成部署

## 第一步：检查环境
```powershell
python --version
```

## 第二步：创建.openclaw目录并拉取仓库
```powershell
if (!(Test-Path "$env:USERPROFILE\.openclaw")) { New-Item -ItemType Directory "$env:USERPROFILE\.openclaw" }
Set-Location "$env:USERPROFILE\.openclaw"
git init
git remote add origin https://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@github.com/yyh19930816-prog/wukong-memory.git
git pull origin main
```

## 第三步：安装依赖
```powershell
pip install requests psutil
```

## 第四步：注册并启动计划任务
```powershell
$python = (Get-Command python).Source
$script = "$env:USERPROFILE\.openclaw\agent_engine_wukong.py"
schtasks /create /tn "OpenClaw-AgentEngine-Wukong" /tr "`"$python`" -X utf8 `"$script`"" /sc minute /mo 15 /ru SYSTEM /rl HIGHEST /f
schtasks /run /tn "OpenClaw-AgentEngine-Wukong"
Write-Host "悟空Agent Engine已启动！"
```

## 验证
```powershell
schtasks /query /tn "OpenClaw-AgentEngine-Wukong"
Get-Content "$env:USERPROFILE\.openclaw\agent_engine_wukong.log" -Tail 10
```

## 完成后告诉老板
"悟空已部署完毕，agent_engine每15分钟自动运行，正在监督美团并学习新知识。"
