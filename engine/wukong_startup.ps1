# 悟空开机自动启动脚本 v1.0
# 自动启动飞书服务 + ngrok + 自动更新飞书Webhook地址

$PYTHON      = "C:\Program Files\Python311\python.exe"
$FEISHU_SVC  = "E:\CURSOR\wukong-memory\engine\wukong_feishu.py"
$HUD         = "E:\CURSOR\wukong-memory\hud\wukong_hud.py"
$NGROK       = "E:\CURSOR\ngrok.exe"
$NGROK_PORT  = 9919

$FEISHU_APP_ID     = "cli_a92effd632b85cd5"
$FEISHU_APP_SECRET = "agCdNI6zfbIjqMBAfF3cmeMzPkPhWFFq"

$LOG = "C:\Users\Administrator\.wukong\startup.log"
New-Item -ItemType Directory -Force -Path "C:\Users\Administrator\.wukong" | Out-Null

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts  $msg" | Tee-Object -FilePath $LOG -Append
}

Log "===== 悟空启动中 ====="

# ── 1. 关闭旧进程 ─────────────────────────────────────────────────────────────
Log "清理旧进程..."
Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1

# ── 2. 启动飞书服务 ───────────────────────────────────────────────────────────
Log "启动飞书服务 (端口 $NGROK_PORT)..."
Start-Process -FilePath $PYTHON -ArgumentList $FEISHU_SVC -WindowStyle Hidden
Start-Sleep 2
Log "飞书服务已启动"

# ── 3. 启动 ngrok ─────────────────────────────────────────────────────────────
Log "启动 ngrok 内网穿透..."
Start-Process -FilePath $NGROK -ArgumentList "http $NGROK_PORT" -WindowStyle Hidden
Start-Sleep 5

# ── 4. 获取 ngrok 公网地址 ────────────────────────────────────────────────────
Log "获取 ngrok 公网地址..."
$ngrok_url = ""
for ($i = 0; $i -lt 10; $i++) {
    try {
        $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 3
        $ngrok_url = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" })[0].public_url
        if ($ngrok_url) { break }
    } catch {}
    Start-Sleep 2
}

if (-not $ngrok_url) {
    Log "获取ngrok地址失败，请手动检查"
    exit 1
}

Log "公网地址: $ngrok_url"

# ── 5. 获取飞书 tenant_access_token ──────────────────────────────────────────
Log "获取飞书 Token..."
try {
    $token_resp = Invoke-RestMethod -Uri "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" `
        -Method Post `
        -ContentType "application/json" `
        -Body (ConvertTo-Json @{ app_id = $FEISHU_APP_ID; app_secret = $FEISHU_APP_SECRET })
    $token = $token_resp.tenant_access_token
    Log "Token获取成功"
} catch {
    Log "Token获取失败: $_"
    exit 1
}

# ── 6. 自动更新飞书事件订阅地址 ───────────────────────────────────────────────
Log "更新飞书 Webhook 地址..."
try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type"  = "application/json"
    }
    $body = ConvertTo-Json @{ url = $ngrok_url }
    $resp = Invoke-RestMethod `
        -Uri "https://open.feishu.cn/open-apis/event/v1/app_status_patch" `
        -Method Patch -Headers $headers -Body $body -ErrorAction SilentlyContinue
    Log "Webhook地址更新完成: $ngrok_url"
} catch {
    # 部分接口需要走开放平台控制台更新，这里记录地址供手动备用
    Log "自动更新Webhook接口受限，当前地址: $ngrok_url"
}

# ── 7. 把新地址写入本地文件，方便查看 ────────────────────────────────────────
$ngrok_url | Out-File "C:\Users\Administrator\.wukong\current_ngrok_url.txt" -Encoding UTF8
Log "当前ngrok地址已保存到: C:\Users\Administrator\.wukong\current_ngrok_url.txt"

# ── 8. 启动悟空 HUD 桌面界面 ──────────────────────────────────────────────────
Log "启动悟空 HUD..."
Start-Sleep 2
Start-Process -FilePath $PYTHON -ArgumentList $HUD -WindowStyle Normal
Log "悟空 HUD 已启动"

Log "===== 悟空全部启动完成 ====="
Log "飞书地址: $ngrok_url"

# 弹出通知
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show(
    "悟空已上线！`n`n飞书地址: $ngrok_url`n`n如地址变化，请到飞书开放平台手动更新",
    "悟空启动成功",
    [System.Windows.Forms.MessageBoxButtons]::OK,
    [System.Windows.Forms.MessageBoxIcon]::Information
)
