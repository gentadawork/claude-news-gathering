<#
  毎週土曜12:00にタスクスケジューラから起動される週次ポッドキャスト生成ラッパー。
  AivisSpeechエンジン（手動起動を前提）の起動確認後、ヘッドレスのClaude Codeに
  skills/weekly-podcast.md の内容をプロンプトとして渡して全工程を実行させる。

  権限: グローバルのbypassPermissionsモードはこのマシンでは無効化されているため、
  --dangerously-skip-permissions は使用しない。代わりに、このリポジトリの
  .claude/settings.local.json にこのスクリプトが実際に使うツールだけを許可リスト登録し、
  通常の権限モードで無人実行できるようにしている（2026-06-24、ユーザー同意済み）。
#>

$RepoRoot = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $RepoRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "weekly_podcast_$Timestamp.log"

function Write-Log {
    param([string]$Message)
    $Line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $LogFile -Value $Line
}

Write-Log "weekly podcast run start"

try {
    $EngineCheck = Invoke-WebRequest -Uri "http://localhost:10101/version" -TimeoutSec 5 -UseBasicParsing
    Write-Log "AivisSpeech engine reachable (status $($EngineCheck.StatusCode))"
}
catch {
    Write-Log "ERROR: AivisSpeech engine not reachable at http://localhost:10101 ($($_.Exception.Message))"
    Write-Log "AivisSpeechエンジンを手動で起動してから再実行してください。"
    exit 1
}

$PromptPath = Join-Path $RepoRoot "skills\weekly-podcast.md"
if (-not (Test-Path $PromptPath)) {
    Write-Log "ERROR: prompt file not found: $PromptPath"
    exit 1
}

$TtsVenvScripts = "E:\workspace\TextToSpeech\.venv\Scripts"
if (Test-Path (Join-Path $TtsVenvScripts "aivis-tts.exe")) {
    $env:PATH = "$TtsVenvScripts;$env:PATH"
    Write-Log "added $TtsVenvScripts to PATH for aivis-tts"
}
else {
    Write-Log "ERROR: aivis-tts.exe not found under $TtsVenvScripts"
    exit 1
}

Push-Location $RepoRoot
try {
    $Prompt = Get-Content -Path $PromptPath -Raw
    Write-Log "invoking headless claude code"
    $Prompt | claude -p *>> $LogFile
    $ExitCode = $LASTEXITCODE
    Write-Log "claude exited with code $ExitCode"
}
finally {
    Pop-Location
}

exit $ExitCode
