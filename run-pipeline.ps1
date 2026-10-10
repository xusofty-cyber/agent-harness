# ==============================================================================
# run-pipeline.ps1
# Platforms: Windows (PowerShell)
# Purpose: Unified pipeline runner for agent-harness:
#          1. Agent rules & bridge deployment (deploy-agents.ps1)
#          2. AI Memory service & MCP setup (setup-ai-memory.ps1)
#          3. External skill synchronization & verification (tools/sync-skills.py)
#          4. Living documentation impact analysis & quality gate (tools/doc-impact.py)
# ==============================================================================

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [Alias('a')]
    [switch]$All,

    [Parameter(Mandatory = $false)]
    [Alias('s')]
    [string[]]$Stages,

    [Parameter(Mandatory = $false)]
    [switch]$Deploy,

    [Parameter(Mandatory = $false)]
    [switch]$Memory,

    [Parameter(Mandatory = $false)]
    [switch]$Skills,

    [Parameter(Mandatory = $false)]
    [switch]$Docs,

    [Parameter(Mandatory = $false)]
    [Alias('p')]
    [string]$Project = ".",

    [Parameter(Mandatory = $false)]
    [Alias('l')]
    [string]$Lang = "zh",

    [Parameter(Mandatory = $false)]
    [Alias('k')]
    [switch]$CheckOnly,

    [Parameter(Mandatory = $false)]
    [switch]$ApplySkills,

    [Parameter(Mandatory = $false)]
    [Alias('g')]
    [switch]$Global,

    [Parameter(Mandatory = $false)]
    [Alias('u')]
    [switch]$Update,

    [Parameter(Mandatory = $false)]
    [Alias('y', 'NonInteractive')]
    [switch]$Yes,

    [Parameter(Mandatory = $false)]
    [Alias('I')]
    [switch]$Interactive,

    [Parameter(Mandatory = $false)]
    [Alias('h')]
    [switch]$Help
)

$repoRoot = $PSScriptRoot

if ($Help) {
    Write-Host "用法 (Usage):" -ForegroundColor Cyan
    Write-Host "  .\run-pipeline.ps1 [选项 (Options)]`n"
    Write-Host "阶段选项 (Stage Options):" -ForegroundColor Cyan
    Write-Host "  -All, -a               一键执行全量流水线 (全阶段按序执行)"
    Write-Host "  -Stages, -s <列表>     指定阶段列表 (逗号分隔: deploy,memory,skills,docs)"
    Write-Host "  -Deploy                执行阶段 1: 规则与 Agent 桥接部署 (deploy-agents)"
    Write-Host "  -Memory                执行阶段 2: AI-Memory 记忆服务与 MCP 接入 (setup-ai-memory)"
    Write-Host "  -Skills                执行阶段 3: 外部技能库校验与同步 (sync-skills)"
    Write-Host "  -Docs                  执行阶段 4: 活体文档影响分析与质检 (doc-impact)`n"
    Write-Host "配置选项 (Configuration):" -ForegroundColor Cyan
    Write-Host "  -Project, -p <路径>    目标项目根目录 (默认: 当前目录 .)"
    Write-Host "  -Lang, -l <语言>       规则模板语言 (en, zh, zh-tw, fr, de；默认: zh)"
    Write-Host "  -Global, -g            部署/更新本机各工具全局规则 (~/.gemini, ~/.codex, ~/.claude)"
    Write-Host "  -Update, -u            覆盖更新已有全局规则并备份；同时更新外部 skills"
    Write-Host "  -CheckOnly, -k         只读检查模式 (技能仅检查差异、文档仅分析影响)"
    Write-Host "  -ApplySkills           在技能同步阶段主动拉取并应用上游更新"
    Write-Host "  -Yes, -y               非交互/无人值守执行 (直接使用推荐配置，不弹窗确认)"
    Write-Host "  -Interactive, -I       强制启用交互式逐步选择向导"
    Write-Host "  -Help, -h              显示本帮助信息`n"
    exit 0
}

# Resolve Python command
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

function Prompt-Select([string]$Title, [array]$Options) {
    if ([Console]::IsInputRedirected) {
        Write-Host "`n$Title"
        for ($i = 0; $i -lt $Options.Count; $i++) {
            Write-Host "  $($i + 1)) $($Options[$i].Label)"
        }
        $choice = Read-Host "请输入序号 [1-$($Options.Count)] (默认 1)"
        $idx = 0
        if ([int]::TryParse($choice, [ref]$idx)) {
            $idx = $idx - 1
            if ($idx -ge 0 -and $idx -lt $Options.Count) {
                return $Options[$idx].Value
            }
        }
        return $Options[0].Value
    }

    $cur = 0
    $count = $Options.Count
    Write-Host "`n$Title" -ForegroundColor Cyan
    Write-Host "↑↓ 移动光标, 回车确认" -ForegroundColor DarkGray

    while ($true) {
        for ($i = 0; $i -lt $count; $i++) {
            if ($i -eq $cur) {
                Write-Host "> ● $($Options[$i].Label)" -ForegroundColor Cyan
            } else {
                Write-Host "  ○ $($Options[$i].Label)" -ForegroundColor DarkGray
            }
        }

        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        if ($key.VirtualKeyCode -eq 38) { # Up
            $cur = ($cur - 1 + $count) % $count
        } elseif ($key.VirtualKeyCode -eq 40) { # Down
            $cur = ($cur + 1) % $count
        } elseif ($key.VirtualKeyCode -eq 13) { # Enter
            break
        } elseif ($key.Character -eq 'q') {
            Write-Host "操作已取消。"
            exit 0
        }

        # Clear printed lines
        if ($host.UI.RawUI.CursorPosition.Y -ge $count) {
            $pos = $host.UI.RawUI.CursorPosition
            $pos.Y -= $count
            $pos.X = 0
            $host.UI.RawUI.CursorPosition = $pos
        }
    }

    return $Options[$cur].Value
}

function Prompt-MultiSelect([string]$Title, [array]$Items) {
    if ([Console]::IsInputRedirected) {
        Write-Host "`n$Title"
        for ($i = 0; $i -lt $Items.Count; $i++) {
            $chk = if ($Items[$i].Checked) { "x" } else { " " }
            Write-Host ("  {0}) [{1}] {2}" -f ($i + 1), $chk, $Items[$i].Label)
        }
        $resp = Read-Host "输入序号多选（空格分隔，回车保持默认）"
        if ([string]::IsNullOrWhiteSpace($resp)) {
            return ($Items | Where-Object { $_.Checked } | ForEach-Object { $_.Value })
        }
        $selected = @()
        foreach ($num in ($resp -split '\s+')) {
            $idx = 0
            if ([int]::TryParse($num, [ref]$idx)) {
                $idx = $idx - 1
                if ($idx -ge 0 -and $idx -lt $Items.Count) {
                    $selected += $Items[$idx].Value
                }
            }
        }
        return $selected
    }

    $cur = 0
    $count = $Items.Count
    Write-Host "`n$Title" -ForegroundColor Cyan
    Write-Host "↑↓ 移动, 空格切换, a 全选/全反选, 回车确认" -ForegroundColor DarkGray

    while ($true) {
        for ($i = 0; $i -lt $count; $i++) {
            $box = if ($Items[$i].Checked) { "[x]" } else { "[ ]" }
            if ($i -eq $cur) {
                Write-Host "> $box $($Items[$i].Label)" -ForegroundColor Cyan
            } else {
                $color = if ($Items[$i].Checked) { "Green" } else { "DarkGray" }
                Write-Host "  $box $($Items[$i].Label)" -ForegroundColor $color
            }
        }

        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        if ($key.VirtualKeyCode -eq 38) { # Up
            $cur = ($cur - 1 + $count) % $count
        } elseif ($key.VirtualKeyCode -eq 40) { # Down
            $cur = ($cur + 1) % $count
        } elseif ($key.VirtualKeyCode -eq 32) { # Space
            $Items[$cur].Checked = -not $Items[$cur].Checked
        } elseif ($key.Character -eq 'a' -or $key.Character -eq 'A') {
            $allChecked = ($Items | Where-Object { -not $_.Checked }).Count -eq 0
            foreach ($it in $Items) { $it.Checked = -not $allChecked }
        } elseif ($key.VirtualKeyCode -eq 13) { # Enter
            break
        } elseif ($key.Character -eq 'q') {
            Write-Host "操作已取消。"
            exit 0
        }

        if ($host.UI.RawUI.CursorPosition.Y -ge $count) {
            $pos = $host.UI.RawUI.CursorPosition
            $pos.Y -= $count
            $pos.X = 0
            $host.UI.RawUI.CursorPosition = $pos
        }
    }

    return ($Items | Where-Object { $_.Checked } | ForEach-Object { $_.Value })
}

# Determine selected stages
$stageDeploy = $Deploy.IsPresent
$stageMemory = $Memory.IsPresent
$stageSkills = $Skills.IsPresent
$stageDocs   = $Docs.IsPresent

$explicit = $All.IsPresent -or $Deploy.IsPresent -or $Memory.IsPresent -or $Skills.IsPresent -or $Docs.IsPresent -or ($Stages -and $Stages.Count -gt 0) -or $Global.IsPresent -or $Update.IsPresent -or $ApplySkills.IsPresent -or $CheckOnly.IsPresent

if ($All.IsPresent) {
    $stageDeploy = $true
    $stageMemory = $true
    $stageSkills = $true
    $stageDocs   = $true
}

if ($Stages) {
    $stageList = @()
    foreach ($entry in $Stages) {
        $stageList += ($entry -split ',')
    }
    foreach ($s in $stageList) {
        switch ($s.Trim().ToLower()) {
            "deploy" { $stageDeploy = $true }
            "memory" { $stageMemory = $true }
            "skills" { $stageSkills = $true }
            "docs"   { $stageDocs   = $true }
            "doc"    { $stageDocs   = $true }
        }
    }
}

$runDetailMode = "quick"
$runGlobal = $Global.IsPresent
$runUpdate = $Update.IsPresent
$runApplySkills = $ApplySkills.IsPresent -or $runUpdate
$globalDeployedInWizard = $false
$skillsSyncChoice = "check"

function Get-LangSuffix([string]$lang) {
    switch ($lang.ToLower()) {
        { $_ -in "zh", "zh-cn", "cn" } { return "" }
        { $_ -in "zh-tw", "tw" }       { return ".zh-tw" }
        { $_ -in "fr", "fr-fr" }       { return ".fr" }
        { $_ -in "de", "de-de" }       { return ".de" }
        default                         { return ".en" }
    }
}

function Resolve-GlobalTemplate([string]$suffix) {
    $path = Join-Path $repoRoot "Global AGENTS$suffix.md"
    if ($suffix -and (Test-Path $path)) { return $path }
    $basePath = Join-Path $repoRoot "Global AGENTS.md"
    if (Test-Path $basePath) { return $basePath }
    return $basePath
}

function Backup-GlobalFile([string]$path) {
    $ts = Get-Date -Format "yyyyMMddHHmmss"
    $backupPath = "$path.bak.$ts"
    $suffix = 1
    while (Test-Path $backupPath) {
        $backupPath = "$path.bak.$ts.$suffix"
        $suffix++
    }
    Copy-Item -LiteralPath $path -Destination $backupPath -Force
    return $backupPath
}

function Deploy-GlobalAgentFile([string]$toolName, [string]$targetPath, [string]$sourceTemplate) {
    $targetDir = Split-Path $targetPath -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    if (Test-Path $targetPath) {
        if ((Get-Item $targetPath) -is [System.IO.DirectoryInfo]) {
            Write-Warning "$toolName global rule target is a directory: $targetPath"
            return
        }
        $backupPath = Backup-GlobalFile $targetPath
        Copy-Item -LiteralPath $sourceTemplate -Destination $targetPath -Force
        Write-Host "  [√] 已更新 $toolName 全局规则: $targetPath (备份: $backupPath)" -ForegroundColor Green
        return
    }

    Copy-Item -LiteralPath $sourceTemplate -Destination $targetPath -Force
    Write-Host "  [√] 已初始化 $toolName 全局规则: $targetPath" -ForegroundColor Green
}

function Deploy-SelectedGlobalAgents([string]$langOption, [string[]]$selectedTools) {
    $suffix = Get-LangSuffix $langOption
    $globalTmpl = Resolve-GlobalTemplate $suffix
    $antigravityPointer = Join-Path $repoRoot "templates\antigravity-GEMINI.md"

    if (-not (Test-Path $globalTmpl)) {
        Write-Warning "未找到全局模板: $globalTmpl，跳过全局规则部署。"
        return
    }

    Write-Host "`n>>> 正在处理所选 Agent 工具全局规则部署与更新..." -ForegroundColor Yellow
    foreach ($tool in $selectedTools) {
        switch ($tool) {
            "claude" {
                $claudeFile = Join-Path $HOME ".claude\CLAUDE.md"
                Deploy-GlobalAgentFile "Claude Code" $claudeFile $globalTmpl
            }
            "antigravity" {
                $geminiAgents = Join-Path $HOME ".gemini\AGENTS.md"
                Deploy-GlobalAgentFile "Antigravity 2.0 / CLI / IDE" $geminiAgents $globalTmpl
                if (Test-Path $antigravityPointer) {
                    $geminiFile = Join-Path $HOME ".gemini\GEMINI.md"
                    Deploy-GlobalAgentFile "Antigravity legacy GEMINI.md" $geminiFile $antigravityPointer
                }
            }
            "codex" {
                $codexDir = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) { Join-Path $HOME ".codex" } else { [Environment]::ExpandEnvironmentVariables($env:CODEX_HOME) }
                $codexFile = Join-Path $codexDir "AGENTS.md"
                $overrideFile = Join-Path $codexDir "AGENTS.override.md"
                if (Test-Path $overrideFile) {
                    $codexFile = $overrideFile
                    Write-Host "  [i] 检测到 Codex 全局覆盖文件，将更新当前生效的 AGENTS.override.md。" -ForegroundColor Cyan
                }
                Deploy-GlobalAgentFile "Codex" $codexFile $globalTmpl
            }
            "cursor" {
                $cursorFile = Join-Path $HOME ".cursorrules"
                Deploy-GlobalAgentFile "Cursor" $cursorFile $globalTmpl
            }
            "zed" {
                $zedDir = if ($env:APPDATA) { Join-Path $env:APPDATA "Zed" } else { Join-Path $HOME ".config\zed" }
                $zedFile = Join-Path $zedDir "AGENTS.md"
                Deploy-GlobalAgentFile "Zed" $zedFile $globalTmpl
            }
            "pi" {
                $piFile = Join-Path $HOME ".pi\agent\AGENTS.md"
                Deploy-GlobalAgentFile "Pi" $piFile $globalTmpl
            }
            "trae" {
                $traeFile = Join-Path $HOME ".trae\rules\AGENTS.md"
                Deploy-GlobalAgentFile "Trae" $traeFile $globalTmpl
            }
            "codebuddy" {
                $cbFile = Join-Path $HOME ".codebuddy\CODEBUDDY.md"
                Deploy-GlobalAgentFile "CodeBuddy" $cbFile $globalTmpl
            }
            "copilot" {
                $copilotFile = Join-Path $HOME ".config\github-copilot\copilot-instructions.md"
                Deploy-GlobalAgentFile "GitHub Copilot" $copilotFile $globalTmpl
            }
            "gemini" {
                $gemFile = Join-Path $HOME ".gemini\GEMINI.md"
                Deploy-GlobalAgentFile "Gemini CLI" $gemFile $globalTmpl
            }
            "windsurf" {
                $wsFile = Join-Path $HOME ".windsurf\rules\agent-harness.md"
                Deploy-GlobalAgentFile "Windsurf" $wsFile $globalTmpl
            }
            "cline" {
                $clineFile = Join-Path $HOME ".clinerules"
                Deploy-GlobalAgentFile "Cline" $clineFile $globalTmpl
            }
            "roo" {
                $rooFile = Join-Path $HOME ".roo\rules\agent-harness.md"
                Deploy-GlobalAgentFile "Roo Code" $rooFile $globalTmpl
            }
            "qwen" {
                $qwenFile = Join-Path $HOME ".qwen\QWEN.md"
                Deploy-GlobalAgentFile "Qwen Code" $qwenFile $globalTmpl
            }
            "kiro" {
                $kiroFile = Join-Path $HOME ".kiro\steering\agent-harness.md"
                Deploy-GlobalAgentFile "Kiro" $kiroFile $globalTmpl
            }
            "continue" {
                $contFile = Join-Path $HOME ".continue\rules\agent-harness.md"
                Deploy-GlobalAgentFile "Continue.dev" $contFile $globalTmpl
            }
            "opencode" {
                $ocFile = Join-Path $HOME ".config\opencode\AGENTS.md"
                Deploy-GlobalAgentFile "OpenCode" $ocFile $globalTmpl
            }
        }
    }
    Write-Host "[√] 所选 Agent 工具全局规则处理完成！`n" -ForegroundColor Green
}

# Interactive 6-step wizard when executed without explicit stage/config flags
if (-not $explicit -and -not $Yes.IsPresent -and (-not [Console]::IsInputRedirected -or $Interactive.IsPresent)) {
    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "  🚀 Agent Harness 统一工程流水线向导 (Unified Pipeline Runner)  " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan

    $Lang = Prompt-Select "[1/6] 选择规则与文档语言 (Select Language):" @(
        @{ Label = "简体中文 (Simplified Chinese, zh)"; Value = "zh" },
        @{ Label = "English (en)"; Value = "en" },
        @{ Label = "繁體中文 (Traditional Chinese, zh-tw)"; Value = "zh-tw" },
        @{ Label = "Français (French, fr)"; Value = "fr" },
        @{ Label = "Deutsch (German, de)"; Value = "de" }
    )

    $globalChoice = Prompt-Select "[2/6] 是否全局更新各工具的 agents (Global Agents Rules):" @(
        @{ Label = "是，更新各工具全局规则 (Update: 备份并更新本机全局配置)"; Value = "yes" },
        @{ Label = "否，仅在项目工程内生效 (Skip: 跳过全局更新，仅限当前项目)"; Value = "no" }
    )

    if ($globalChoice -eq "yes") {
        $selectedTools = Prompt-MultiSelect "请选择要全局更新规则的 Agent 工具 (Select Agent Tools):" @(
            @{ Label = "Claude Code (~/.claude/CLAUDE.md)"; Value = "claude"; Checked = $true },
            @{ Label = "Antigravity 2.0 / CLI / IDE (~/.gemini/AGENTS.md, GEMINI.md)"; Value = "antigravity"; Checked = $true },
            @{ Label = "Codex CLI / app (~/.codex/AGENTS.md)"; Value = "codex"; Checked = $true },
            @{ Label = "Cursor (~/.cursorrules)"; Value = "cursor"; Checked = $true },
            @{ Label = "Zed (~/.config/zed/AGENTS.md)"; Value = "zed"; Checked = $true },
            @{ Label = "Pi (~/.pi/agent/AGENTS.md)"; Value = "pi"; Checked = $true },
            @{ Label = "Trae (~/.trae/rules/AGENTS.md)"; Value = "trae"; Checked = $false },
            @{ Label = "CodeBuddy (~/.codebuddy/CODEBUDDY.md)"; Value = "codebuddy"; Checked = $false },
            @{ Label = "GitHub Copilot (copilot-instructions.md)"; Value = "copilot"; Checked = $false },
            @{ Label = "Gemini CLI (~/.gemini/GEMINI.md)"; Value = "gemini"; Checked = $false },
            @{ Label = "Windsurf (~/.windsurf/rules/agent-harness.md)"; Value = "windsurf"; Checked = $false },
            @{ Label = "Cline (~/.clinerules)"; Value = "cline"; Checked = $false },
            @{ Label = "Roo Code (~/.roo/rules/agent-harness.md)"; Value = "roo"; Checked = $false },
            @{ Label = "Qwen Code (~/.qwen/QWEN.md)"; Value = "qwen"; Checked = $false },
            @{ Label = "Kiro (~/.kiro/steering/agent-harness.md)"; Value = "kiro"; Checked = $false },
            @{ Label = "Continue.dev (~/.continue/rules/agent-harness.md)"; Value = "continue"; Checked = $false },
            @{ Label = "OpenCode (~/.config/opencode/AGENTS.md)"; Value = "opencode"; Checked = $false }
        )

        if ($selectedTools -and $selectedTools.Count -gt 0) {
            Deploy-SelectedGlobalAgents $Lang $selectedTools
            $globalDeployedInWizard = $true
        } else {
            Write-Host "  [i] 未勾选任何 Agent 工具，跳过全局更新。`n" -ForegroundColor Yellow
        }
        $runGlobal = $false
    } else {
        $runGlobal = $false
    }

    $skillChoice = Prompt-Select "[3/6] 选择是否更新外部扩展的 skills 技能库 (External Skills Sync):" @(
        @{ Label = "在线同步更新 (Apply: 自动拉取上游更新并应用到本地技能库)"; Value = "apply" },
        @{ Label = "安全检查模式 (Check only: 仅对比校验版本差异，不覆写技能文件)"; Value = "check" },
        @{ Label = "跳过更新 (Skip: 不更新也不检查外部技能库)"; Value = "skip" }
    )
    $skillsSyncChoice = $skillChoice
    switch ($skillsSyncChoice) {
        "apply" {
            $runApplySkills = $true
            $CheckOnly = $false
        }
        "check" {
            $runApplySkills = $false
            $CheckOnly = $true
        }
        "skip" {
            $runApplySkills = $false
            $CheckOnly = $false
        }
    }

    Write-Host "`n[4/6] 目标工程根目录 (Target Project Path):" -ForegroundColor Cyan
    $inputProj = Read-Host "请输入工程路径 [默认: 当前目录 .]"
    if (-not [string]::IsNullOrWhiteSpace($inputProj)) { $Project = $inputProj }

    $pipeMode = Prompt-Select "[5/6] 选择流水线执行流程与阶段组合 (Select Pipeline Flow & Stages):" @(
        @{ Label = "一键全量流水线 (Run Full Pipeline: 规则部署 -> AI记忆 -> 技能同步 -> 文档质检)"; Value = "all" },
        @{ Label = "自定义阶段组合 (Custom Stages: 自选执行部分阶段)"; Value = "custom" },
        @{ Label = "仅规则与 Agent 桥接部署 (Deploy Rules & Bridges only)"; Value = "only-deploy" },
        @{ Label = "仅配置 AI-Memory 记忆服务 (Setup AI Memory only)"; Value = "only-memory" },
        @{ Label = "仅校验/同步外部技能库 (Sync Skills only)"; Value = "only-skills" },
        @{ Label = "仅活体文档影响分析与质检 (Living Doc Impact only)"; Value = "only-docs" }
    )

    switch ($pipeMode) {
        "all" {
            $stageDeploy = $true; $stageMemory = $true; $stageSkills = $true; $stageDocs = $true
        }
        "custom" {
            $chosen = Prompt-MultiSelect "选择要纳入本次流水线的阶段 (Select stages to run):" @(
                @{ Label = "阶段 1: 部署规则模板与 Agent 桥接 (deploy-agents)"; Value = "deploy"; Checked = $true },
                @{ Label = "阶段 2: 接入 AI-Memory 跨工具记忆服务 (setup-ai-memory)"; Value = "memory"; Checked = $true },
                @{ Label = "阶段 3: 校验/更新外部技能库 (sync-skills)"; Value = "skills"; Checked = $true },
                @{ Label = "阶段 4: 活体文档影响分析与质检门禁 (doc-impact)"; Value = "docs"; Checked = $true }
            )
            $stageDeploy = $chosen -contains "deploy"
            $stageMemory = $chosen -contains "memory"
            $stageSkills = $chosen -contains "skills"
            $stageDocs   = $chosen -contains "docs"
        }
        "only-deploy" { $stageDeploy = $true }
        "only-memory" { $stageMemory = $true }
        "only-skills" { $stageSkills = $true }
        "only-docs"   { $stageDocs   = $true }
    }

    $runDetailMode = Prompt-Select "[6/6] 选择执行交互细化程度 (Execution Detail):" @(
        @{ Label = "极速推荐配置 (Quick Run: 自动使用最佳实践一键贯通流水线)"; Value = "quick" },
        @{ Label = "逐步向导配置 (Interactive: 依次打开各工具阶段的详细选项向导)"; Value = "detailed" }
    )
}

# Pre-flight review: when user passed explicit CLI parameters but NOT -Yes
if ($explicit -and -not $Yes.IsPresent -and (-not [Console]::IsInputRedirected -or $Interactive.IsPresent)) {
    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "  🚀 Agent Harness 流水线执行前配置确认 (Pre-flight Review)   " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "检测到执行参数。请确认是否需要同步处理全局规则与外部技能库：" -ForegroundColor Yellow

    $globalChoice = Prompt-Select "[1/2] 本机全局各 Agent 工具规则处理 (Global Rules Sync):" @(
        @{ Label = if ($runGlobal) { "● 确认: 部署/覆盖更新全局规则 (~/.gemini, ~/.codex, ~/.claude)" } else { "○ 跳过: 仅更新当前项目工程，不改动本机全局规则" }; Value = if ($runGlobal) { "sync" } else { "skip" } },
        @{ Label = if (-not $runGlobal) { "● 确认: 部署/覆盖更新全局规则 (~/.gemini, ~/.codex, ~/.claude)" } else { "○ 跳过: 仅更新当前项目工程，不改动本机全局规则" }; Value = if (-not $runGlobal) { "sync" } else { "skip" } }
    )
    if ($globalChoice -eq "sync") {
        $runGlobal = $true
        $runUpdate = $true
    } else {
        $runGlobal = $false
    }

    $skillChoice = Prompt-Select "[2/2] 外部开源技能库处理 (External Skills Sync):" @(
        @{ Label = if ($runApplySkills) { "● 确认: 在线拉取 GitHub 上游更新并应用到本地技能库 (--apply)" } else { "○ 仅检查: 仅对比校验版本差异，不覆写技能文件 (--check)" }; Value = if ($runApplySkills) { "apply" } else { "check" } },
        @{ Label = if (-not $runApplySkills) { "● 确认: 在线拉取 GitHub 上游更新并应用到本地技能库 (--apply)" } else { "○ 仅检查: 仅对比校验版本差异，不覆写技能文件 (--check)" }; Value = if (-not $runApplySkills) { "apply" } else { "check" } }
    )
    $runApplySkills = ($skillChoice -eq "apply")
}

# Fallback default
if (-not $stageDeploy -and -not $stageMemory -and -not $stageSkills -and -not $stageDocs) {
    $stageDeploy = $true
    $stageMemory = $true
    $stageSkills = $true
    $stageDocs   = $true
}

$targetAbs = Resolve-Path $Project -ErrorAction SilentlyContinue
if (-not $targetAbs) { $targetAbs = (Get-Item -Path $Project -ErrorAction SilentlyContinue).FullName }
if (-not $targetAbs) { $targetAbs = $Project }
if ($targetAbs -is [System.Management.Automation.PathInfo]) { $targetAbs = $targetAbs.Path }

function Ensure-ProjectMemoryScaffold([string]$targetDir, [string]$langOpt) {
    $langSuffix = switch -Regex ($langOpt) {
        '^(zh|zh-cn|zh-hans)$' { '.zh' }
        '^(zh-tw|zh-hk|zh-hant)$' { '.zh-tw' }
        '^(fr|fr-fr)$' { '.fr' }
        '^(de|de-de)$' { '.de' }
        Default { '' }
    }

    $projBaseName = Split-Path -Leaf $targetDir

    $pTemplate = Join-Path $repoRoot "templates\PROJECT_CONTEXT.template$langSuffix.md"
    if (-not (Test-Path $pTemplate)) { $pTemplate = Join-Path $repoRoot "templates\PROJECT_CONTEXT.template.md" }

    $sTemplate = Join-Path $repoRoot "templates\SESSION_STATE.template$langSuffix.md"
    if (-not (Test-Path $sTemplate)) { $sTemplate = Join-Path $repoRoot "templates\SESSION_STATE.template.md" }

    $pTarget = Join-Path $targetDir "PROJECT_CONTEXT.md"
    if (-not (Test-Path $pTarget) -and (Test-Path $pTemplate)) {
        $content = Get-Content -Path $pTemplate -Raw -Encoding utf8
        $content = $content -replace '<PROJECT_NAME>', $projBaseName
        [System.IO.File]::WriteAllText($pTarget, $content, [System.Text.Encoding]::UTF8)
        Write-Host "  [√] 自动初始化项目长期事实: PROJECT_CONTEXT.md" -ForegroundColor Green
    }

    $sTarget = Join-Path $targetDir "SESSION_STATE.md"
    if (-not (Test-Path $sTarget) -and (Test-Path $sTemplate)) {
        $content = Get-Content -Path $sTemplate -Raw -Encoding utf8
        $content = $content -replace '<PROJECT_NAME>', $projBaseName
        [System.IO.File]::WriteAllText($sTarget, $content, [System.Text.Encoding]::UTF8)
        Write-Host "  [√] 自动初始化当前会话断点: SESSION_STATE.md" -ForegroundColor Green
    }
}

Write-Host "`n▶ 开始执行 Agent Harness 工程流水线" -ForegroundColor Cyan
Write-Host "  目标工程: $targetAbs" -ForegroundColor Green
Write-Host "  模版语言: $Lang" -ForegroundColor Green
Write-Host "  执行模式: $runDetailMode`n" -ForegroundColor Green

Ensure-ProjectMemoryScaffold $targetAbs $Lang

$summaryNames = @()
$summaryStatus = @()
$summaryDetail = @()

$totalStages = 0
if ($stageDeploy) { $totalStages++ }
if ($stageMemory) { $totalStages++ }
if ($stageSkills) { $totalStages++ }
if ($stageDocs)   { $totalStages++ }

$currentStage = 0

# ==============================================================================
# 阶段 1: 规则与 Agent 桥接部署 (deploy-agents)
# ==============================================================================
if ($stageDeploy) {
    $currentStage++
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "[$currentStage/$totalStages] 阶段 1: 规则与 Agent 桥接部署 (deploy-agents)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    $stageName = "规则与 Agent 桥接部署 (deploy-agents)"
    $summaryNames += $stageName

    $deployScript = Join-Path $repoRoot "deploy-agents.ps1"
    $deployParams = @{ ProjectPath = $targetAbs; Language = $Lang }
    if (-not $globalDeployedInWizard -and $runGlobal) { $deployParams["Global"] = $true }
    if ($runUpdate) { $deployParams["Update"] = $true }
    if ($runDetailMode -eq "detailed") {
        $deployParams["Interactive"] = $true
    }

    try {
        & $deployScript @deployParams
        Write-Host "`n✔ 阶段 1 执行完成`n" -ForegroundColor Green
        $summaryStatus += "PASS"
        $summaryDetail += "规则与桥接文件配置就绪"
    } catch {
        Write-Host "`n✖ 阶段 1 出现错误: $_`n" -ForegroundColor Red
        $summaryStatus += "FAIL"
        $summaryDetail += "部署脚本执行失败"
    }
}

# ==============================================================================
# 阶段 2: AI-Memory 跨工具记忆服务接入 (setup-ai-memory)
# ==============================================================================
if ($stageMemory) {
    $currentStage++
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "[$currentStage/$totalStages] 阶段 2: 配置 AI-Memory 记忆服务 (setup-ai-memory)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    $stageName = "AI-Memory 记忆服务 (setup-ai-memory)"
    $summaryNames += $stageName

    $hasAiMemory = Get-Command ai-memory -ErrorAction SilentlyContinue
    if (-not $hasAiMemory) {
        $uPath = [System.Environment]::GetEnvironmentVariable('PATH', [System.EnvironmentVariableTarget]::User)
        $mPath = [System.Environment]::GetEnvironmentVariable('PATH', [System.EnvironmentVariableTarget]::Machine)
        $candidates = @('D:\GreenSoft\ai-memory-windows-x86_64')
        if ($uPath) { $candidates += ($uPath -split ';') }
        if ($mPath) { $candidates += ($mPath -split ';') }
        foreach ($c in ($candidates | Select-Object -Unique)) {
            if ($c -and (Test-Path -LiteralPath (Join-Path $c 'ai-memory.exe'))) {
                $env:PATH = "$c;$env:PATH"
                $hasAiMemory = Get-Command ai-memory -ErrorAction SilentlyContinue
                break
            }
        }
    }

    if (-not $hasAiMemory) {
        Write-Host "⚠ 提示: 系统 PATH 中未检测到 'ai-memory' CLI。" -ForegroundColor Yellow
        Write-Host "  ai-memory 属于可选进阶组件。如需跨工具记忆沉淀，请先安装 upstream ai-memory。"
        Write-Host "↷ 跳过本阶段，继续后续流水线。`n" -ForegroundColor Yellow
        $summaryStatus += "SKIP"
        $summaryDetail += "未检测到 ai-memory CLI"
    } else {
        $tomlPath = Join-Path $targetAbs ".ai-memory.toml"
        $examplePath = Join-Path $repoRoot ".ai-memory.toml.example"
        if (-not (Test-Path $tomlPath) -and (Test-Path $examplePath)) {
            Write-Host "目标工程尚未配置 .ai-memory.toml" -ForegroundColor Yellow
            $doCreate = $false
            if (-not $Yes.IsPresent -and -not [Console]::IsInputRedirected) {
                $ans = Read-Host "是否从 .ai-memory.toml.example 自动初始化配置文件？[y/N]"
                if ($ans -match '^[Yy]$') { $doCreate = $true }
            }
            if ($doCreate) {
                $projName = Split-Path $targetAbs -Leaf
                $raw = Get-Content $examplePath -Raw
                $raw = $raw -replace 'replace-with-workspace-(name|id)', "workspace-$projName"
                $raw = $raw -replace 'replace-with-project-(name|id)', $projName
                Set-Content -Path $tomlPath -Value $raw -Encoding UTF8
                Write-Host "✔ 已生成 $tomlPath" -ForegroundColor Green
            } else {
                Write-Host "↷ 缺少 .ai-memory.toml 配置，跳过记忆集成。`n" -ForegroundColor Yellow
                $summaryStatus += "SKIP"
                $summaryDetail += "未配置 .ai-memory.toml"
            }
        }

        if ((Test-Path $tomlPath) -and ((Get-Content $tomlPath -Raw) -notmatch 'replace-with-')) {
            $setupScript = Join-Path $repoRoot "setup-ai-memory.ps1"
            Push-Location $targetAbs
            try {
                if ($runDetailMode -eq "detailed" -and -not [Console]::IsInputRedirected) {
                    & $setupScript
                } else {
                    & $setupScript -Agent @("claude-code", "codex", "antigravity-ide")
                }
                Write-Host "`n✔ 阶段 2 执行完成`n" -ForegroundColor Green
                $summaryStatus += "PASS"
                $summaryDetail += "AI 记忆集成与 MCP 配置完成"
            } catch {
                Write-Host "`n↷ 阶段 2 跳过或未完全成功: $_`n" -ForegroundColor Yellow
                $summaryStatus += "SKIP"
                $summaryDetail += "环境或依赖未满足"
            } finally {
                Pop-Location
            }
        }
    }
}

# ==============================================================================
# 阶段 3: 外部技能库校验与同步 (sync-skills)
# ==============================================================================
if ($stageSkills) {
    $currentStage++
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "[$currentStage/$totalStages] 阶段 3: 校验/同步外部技能库 (sync-skills)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    $stageName = "外部技能库同步与校验 (sync-skills)"
    $summaryNames += $stageName

    if ($skillsSyncChoice -eq "skip") {
        Write-Host "↷ 外部技能库同步已在步骤 [3/6] 选择跳过。`n" -ForegroundColor Yellow
        $summaryStatus += "SKIP"
        $summaryDetail += "步骤 [3/6] 选择跳过技能同步"
    } elseif (-not $pythonCmd) {
        Write-Host "⚠ 未找到 Python 解释器，跳过技能同步。`n" -ForegroundColor Yellow
        $summaryStatus += "SKIP"
        $summaryDetail += "未找到 Python 环境"
    } else {
        $syncScript = Join-Path $repoRoot "tools\sync-skills.py"
        try {
            $syncArgs = @()
            if ($CheckOnly.IsPresent) { $syncArgs += "--check-only" }
            if ($runDetailMode -eq "detailed" -and -not [Console]::IsInputRedirected) {
                & $pythonCmd $syncScript @syncArgs
            } else {
                if (-not $CheckOnly.IsPresent) {
                    $syncArgs += if ($runApplySkills) { "--apply" } else { "--check" }
                } else {
                    $syncArgs += "--check"
                }
                & $pythonCmd $syncScript @syncArgs
            }
            Write-Host "`n✔ 阶段 3 检查完成`n" -ForegroundColor Green
            $summaryStatus += "PASS"
            $summaryDetail += "技能锁定与版本校验完成"
        } catch {
            Write-Host "`n✖ 阶段 3 出现异常: $_`n" -ForegroundColor Red
            $summaryStatus += "FAIL"
            $summaryDetail += "技能同步工具异常"
        }
    }
}

# ==============================================================================
# 阶段 4: 活体文档影响分析与质检门禁 (doc-impact)
# ==============================================================================
if ($stageDocs) {
    $currentStage++
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "[$currentStage/$totalStages] 阶段 4: 活体文档影响分析与质检 (doc-impact)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    $stageName = "活体文档影响分析与质检 (doc-impact)"
    $summaryNames += $stageName

    if (-not $pythonCmd) {
        Write-Host "⚠ 未找到 Python 解释器，跳过活体文档分析。`n" -ForegroundColor Yellow
        $summaryStatus += "SKIP"
        $summaryDetail += "未找到 Python 环境"
    } else {
        $docScript = Join-Path $repoRoot "tools\doc-impact.py"
        try {
            if ($runDetailMode -eq "detailed" -and -not [Console]::IsInputRedirected) {
                & $pythonCmd $docScript --interactive
            } else {
                & $pythonCmd $docScript --root $targetAbs
            }
            Write-Host "`n✔ 阶段 4 质检完成`n" -ForegroundColor Green
            $summaryStatus += "PASS"
            $summaryDetail += "活体文档溯源关系与影响分析通过"
        } catch {
            Write-Host "`n✖ 阶段 4 出现异常: $_`n" -ForegroundColor Red
            $summaryStatus += "FAIL"
            $summaryDetail += "文档影响分析工具异常"
        }
    }
}

# ==============================================================================
# 流水线执行汇总 (Pipeline Execution Summary)
# ==============================================================================
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " 📊 Agent Harness 流水线执行汇总 (Pipeline Summary)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$hasFail = $false
for ($i = 0; $i -lt $summaryNames.Count; $i++) {
    $st = $summaryStatus[$i]
    $nm = $summaryNames[$i]
    $dt = $summaryDetail[$i]
    $paddedName = $nm.PadRight(38)
    switch ($st) {
        "PASS" {
            Write-Host " [✔ PASS]  $paddedName : $dt" -ForegroundColor Green
        }
        "SKIP" {
            Write-Host " [↷ SKIP]  $paddedName : $dt" -ForegroundColor Yellow
        }
        "FAIL" {
            Write-Host " [✖ FAIL]  $paddedName : $dt" -ForegroundColor Red
            $hasFail = $true
        }
    }
}

Write-Host "================================================================" -ForegroundColor Cyan
if ($hasFail) {
    Write-Host "⚠ 流水线部分阶段未完全通过，请检查上方日志。`n" -ForegroundColor Red
    exit 1
} else {
    Write-Host "🎉 流水线全部阶段执行完毕！`n" -ForegroundColor Green
    exit 0
}
