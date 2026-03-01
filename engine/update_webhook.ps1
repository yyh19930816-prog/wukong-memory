# 悟空 Webhook 一键更新脚本
# 双击运行，自动读取新地址并打开飞书配置页面

$URL_FILE = "C:\Users\Administrator\.wukong\current_ngrok_url.txt"
$FEISHU_CONFIG_URL = "https://open.feishu.cn/app/cli_a92effd632b85cd5/event"

Add-Type -AssemblyName System.Windows.Forms

# ── 读取当前 ngrok 地址 ───────────────────────────────────────────────────────
$ngrok_url = ""

# 优先从 ngrok API 实时获取（最准确）
try {
    $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 3
    $ngrok_url = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" })[0].public_url
} catch {}

# 如果 ngrok 没运行，从文件读取上次的地址
if (-not $ngrok_url) {
    if (Test-Path $URL_FILE) {
        $ngrok_url = (Get-Content $URL_FILE -Encoding UTF8).Trim()
    }
}

if (-not $ngrok_url) {
    [System.Windows.Forms.MessageBox]::Show(
        "获取不到 ngrok 地址！`n`n请先确认悟空服务已启动。",
        "悟空提示",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Warning
    )
    exit
}

# ── 复制地址到剪贴板 ──────────────────────────────────────────────────────────
Set-Clipboard -Value $ngrok_url

# ── 弹出提示 ──────────────────────────────────────────────────────────────────
$msg = "当前 ngrok 地址已复制到剪贴板：`n`n$ngrok_url`n`n点确定后自动打开飞书配置页面。`n`n操作步骤：`n1. 点订阅方式旁边的 ✏️`n2. 把地址粘贴进去（Ctrl+V）`n3. 点保存"

$result = [System.Windows.Forms.MessageBox]::Show(
    $msg,
    "悟空 Webhook 更新",
    [System.Windows.Forms.MessageBoxButtons]::OKCancel,
    [System.Windows.Forms.MessageBoxIcon]::Information
)

if ($result -eq "OK") {
    Start-Process $FEISHU_CONFIG_URL
}
