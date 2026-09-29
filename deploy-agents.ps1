# ==============================================================================
# deploy-agents.ps1
# Platforms: Windows (PowerShell 5.1 / PowerShell 7+)
# Purpose: One-click deploy & online update AI Agents Harness spec, rules & skills
#          (Supports Codex / Claude Code / Antigravity IDE)
# ==============================================================================

[CmdletBinding()]
param (
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$ProjectPath,

    [Alias("g")]
    [switch]$Global,

    [Alias("u")]
    [switch]$Update,

    [Alias("c")]
    [switch]$CometInit,

    [string]$UpdateSource = ""
)

$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Template file paths
$ResolvedGlobalTemplate = Join-Path $ScriptDir "Global AGENTS.md"
if (-not (Test-Path $ResolvedGlobalTemplate)) {
    $found = Get-ChildItem -Path $ScriptDir -Filter "*Global*AGENTS*.md" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $found) {
        $found = Get-ChildItem -Path $ScriptDir -Filter "*全局*AGENTS*.md" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if ($found) { $ResolvedGlobalTemplate = $found.FullName }
}

$ResolvedProjectTemplate = Join-Path $ScriptDir "Project AGENTS.md"
if (-not (Test-Path $ResolvedProjectTemplate)) {
    $found = Get-ChildItem -Path $ScriptDir -Filter "*Project*AGENTS*.md" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $found) {
        $found = Get-ChildItem -Path $ScriptDir -Filter "*项目级*AGENTS*.md" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if ($found) { $ResolvedProjectTemplate = $found.FullName }
}

$SourceRulesDir = Join-Path $ScriptDir ".agents\rules"
$SourceSkillsDir = Join-Path $ScriptDir ".agents\skills"
$SourceSkillsLock = Join-Path $ScriptDir "skills-lock.json"
$SourceClaudeSettings = Join-Path $ScriptDir ".claude\settings.json"

# ==============================================================================
# 1. Online Update Phase (-Update)
# ==============================================================================
if ($Update) {
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host " Checking & Performing Online Updates..." -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan

    # A. Check Git repository update
    $IsGitRepo = $false
    try {
        $gitCheck = & git -C "$ScriptDir" rev-parse --is-inside-work-tree 2>$null
        if ($gitCheck -eq "true") { $IsGitRepo = $true }
    } catch {
        $IsGitRepo = $false
    }

    if ($IsGitRepo) {
        Write-Host ">>> Pulling latest templates, rules, and skills from Git upstream..." -ForegroundColor Yellow
        try {
            & git -C "$ScriptDir" pull --rebase 2>&1 | Write-Host
            Write-Host "  [OK] Git repository up to date." -ForegroundColor Green
        } catch {
            Write-Warning "Failed to git pull: $_"
        }
    } else {
        Write-Host "  [INFO] Template directory is not a Git repo; skipping git pull." -ForegroundColor Gray
    }

    # B. Check Harness ecosystem CLI tools
    Write-Host "`n>>> Checking Harness ecosystem tools updates..." -ForegroundColor Yellow
    $cometInstalled = Get-Command "comet" -ErrorAction SilentlyContinue
    if ($cometInstalled) {
        Write-Host "  [INFO] Found Comet CLI. Executing 'comet update'..." -ForegroundColor Gray
        try {
            & comet update
        } catch {
            Write-Warning "comet update execution: $_"
        }
    } else {
        $npmInstalled = Get-Command "npm" -ErrorAction SilentlyContinue
        if ($npmInstalled) {
            Write-Host "  [INFO] Comet CLI not installed. To install: npm install -g @rpamis/comet" -ForegroundColor Gray
        }
    }

    # C. Update Skills via npx skills from online upstream
    $npxInstalled = Get-Command "npx" -ErrorAction SilentlyContinue
    if ($npxInstalled) {
        Write-Host "`n>>> Updating Skills via 'npx skills@latest update' from online upstream..." -ForegroundColor Yellow
        try {
            & npx -y skills@latest update -y 2>&1 | Write-Host
            Write-Host "  [OK] Online skills refreshed via npx skills." -ForegroundColor Green
        } catch {
            Write-Warning "npx skills update encountered warning: $_"
        }
    } else {
        Write-Host "  [INFO] Node/npx not found; skipping npx skills update." -ForegroundColor Gray
    }
}

# If no ProjectPath is specified and not -Global, show usage
if (-not $ProjectPath -and -not $Global) {
    Write-Host "`n[用法说明] Usage:" -ForegroundColor Cyan
    Write-Host "  .\deploy-agents.ps1 -ProjectPath <目标项目路径> [-Global] [-Update]"
    Write-Host "  .\deploy-agents.ps1 -Global [-Update]   # 仅更新全局配置"
    Write-Host ""
    Write-Host "[参数说明] Parameters:" -ForegroundColor Cyan
    Write-Host "  -ProjectPath   目标项目根目录路径。"
    Write-Host "  -Global (-g)   同时部署/更新当前用户的全局规则 (~/.claude/ 与 ~/.gemini/)。"
    Write-Host "  -Update (-u)   执行在线检测与更新（拉取最新规则、更新技能库与配套脚手架）。"
    exit 0
}

# ==============================================================================
# 2. Deploy / Update Global Rules (-Global)
# ==============================================================================
if ($Global) {
    Write-Host "`n>>> [1/3] Deploying/Updating global rules..." -ForegroundColor Yellow

    if (-not (Test-Path $ResolvedGlobalTemplate)) {
        Write-Warning "Global template not found, skipping global setup."
    } else {
        # A. Claude Code (~/.claude/CLAUDE.md)
        $ClaudeGlobalDir = Join-Path $HOME ".claude"
        $ClaudeGlobalFile = Join-Path $ClaudeGlobalDir "CLAUDE.md"
        if (-not (Test-Path $ClaudeGlobalDir)) {
            New-Item -ItemType Directory -Path $ClaudeGlobalDir -Force | Out-Null
        }
        Copy-Item -Path $ResolvedGlobalTemplate -Destination $ClaudeGlobalFile -Force
        Write-Host "  [OK] Claude Code global rule: $ClaudeGlobalFile" -ForegroundColor Green

        # B. Antigravity IDE (~/.gemini/config/rules/global_agents.md)
        $AntigravityGlobalDir = Join-Path $HOME ".gemini\config\rules"
        $AntigravityGlobalFile = Join-Path $AntigravityGlobalDir "global_agents.md"
        if (-not (Test-Path $AntigravityGlobalDir)) {
            New-Item -ItemType Directory -Path $AntigravityGlobalDir -Force | Out-Null
        }
        Copy-Item -Path $ResolvedGlobalTemplate -Destination $AntigravityGlobalFile -Force
        Write-Host "  [OK] Antigravity IDE global rule: $AntigravityGlobalFile" -ForegroundColor Green
    }
}

# If no target project path specified, finish here
if (-not $ProjectPath) {
    Write-Host "`n[OK] Global operations completed successfully!" -ForegroundColor Green
    exit 0
}

# Validate target project directory
if (-not (Test-Path $ProjectPath)) {
    Write-Host "`n[ERROR] Target project path does not exist: $ProjectPath" -ForegroundColor Red
    exit 1
}
$ResolvedProjectPath = (Resolve-Path $ProjectPath).Path

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Target Project: $ResolvedProjectPath" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# ==============================================================================
# 3. Deploy / Update Project-level AGENTS.md & Bridges
# ==============================================================================
Write-Host "`n>>> [2/3] Deploying project rules and tool bridges..." -ForegroundColor Yellow

$TargetAgentsFile = Join-Path $ResolvedProjectPath "AGENTS.md"
if (-not (Test-Path $TargetAgentsFile)) {
    Copy-Item -Path $ResolvedProjectTemplate -Destination $TargetAgentsFile
    Write-Host "  [OK] Created AGENTS.md from template" -ForegroundColor Green
} else {
    Write-Host "  [INFO] AGENTS.md already exists, preserving custom project configuration." -ForegroundColor Gray
    if ($Update) {
        # Generate an updated reference template for user inspection
        $TargetRefTemplate = Join-Path $ResolvedProjectPath "AGENTS.template.md"
        Copy-Item -Path $ResolvedProjectTemplate -Destination $TargetRefTemplate -Force
        Write-Host "  [INFO] Created AGENTS.template.md for reference with latest specs." -ForegroundColor Gray
    }
}

# Bridge for Claude Code (CLAUDE.md)
$TargetClaudeFile = Join-Path $ResolvedProjectPath "CLAUDE.md"
if (-not (Test-Path $TargetClaudeFile)) {
    try {
        New-Item -ItemType SymbolicLink -Path $TargetClaudeFile -Target "AGENTS.md" -ErrorAction Stop | Out-Null
        Write-Host "  [OK] Created symlink: CLAUDE.md -> AGENTS.md" -ForegroundColor Green
    } catch {
        Set-Content -Path $TargetClaudeFile -Value "@AGENTS.md`n" -Encoding UTF8
        Write-Host "  [OK] Created reference file: CLAUDE.md (@AGENTS.md)" -ForegroundColor Green
    }
} else {
    Write-Host "  [INFO] CLAUDE.md already exists, keeping existing file." -ForegroundColor Gray
}

# Bridge for GitHub Copilot (.github/copilot-instructions.md)
$TargetGithubDir = Join-Path $ResolvedProjectPath ".github"
$TargetCopilotFile = Join-Path $TargetGithubDir "copilot-instructions.md"
if (-not (Test-Path $TargetGithubDir)) {
    New-Item -ItemType Directory -Path $TargetGithubDir -Force | Out-Null
}
if (-not (Test-Path $TargetCopilotFile)) {
    try {
        New-Item -ItemType SymbolicLink -Path $TargetCopilotFile -Target "..\AGENTS.md" -ErrorAction Stop | Out-Null
        Write-Host "  [OK] Created symlink: .github/copilot-instructions.md -> AGENTS.md" -ForegroundColor Green
    } catch {
        Copy-Item -Path $TargetAgentsFile -Destination $TargetCopilotFile -Force
        Write-Host "  [OK] Created file: .github/copilot-instructions.md" -ForegroundColor Green
    }
} else {
    Write-Host "  [INFO] copilot-instructions.md already exists, keeping existing file." -ForegroundColor Gray
}

# Bridge for Zed IDE (ZED.md)
$TargetZedFile = Join-Path $ResolvedProjectPath "ZED.md"
if (-not (Test-Path $TargetZedFile)) {
    try {
        New-Item -ItemType SymbolicLink -Path $TargetZedFile -Target "AGENTS.md" -ErrorAction Stop | Out-Null
        Write-Host "  [OK] Created symlink: ZED.md -> AGENTS.md" -ForegroundColor Green
    } catch {
        $zedBridge = @"
# ZED.md
See @AGENTS.md for project commands, architecture boundaries, conventions, and rules.
"@
        Set-Content -Path $TargetZedFile -Value $zedBridge -Encoding UTF8
        Write-Host "  [OK] Created bridge file: ZED.md" -ForegroundColor Green
    }
} else {
    Write-Host "  [INFO] ZED.md already exists, keeping existing file." -ForegroundColor Gray
}

# Deploy Claude Code PreToolUse Security Hooks (.claude/settings.json)
if (Test-Path $SourceClaudeSettings) {
    $TargetClaudeDir = Join-Path $ResolvedProjectPath ".claude"
    if (-not (Test-Path $TargetClaudeDir)) {
        New-Item -ItemType Directory -Path $TargetClaudeDir -Force | Out-Null
    }
    $TargetClaudeSettings = Join-Path $TargetClaudeDir "settings.json"
    if ($Update -or (-not (Test-Path $TargetClaudeSettings))) {
        Copy-Item -Path $SourceClaudeSettings -Destination $TargetClaudeSettings -Force
        Write-Host "  [OK] Deployed Claude Code security hooks: .claude/settings.json" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] .claude/settings.json already exists, keeping existing file." -ForegroundColor Gray
    }
}

# ==============================================================================
# 4. Deploy / Update Sub-rules (.agents/rules/)
# ==============================================================================
$TargetRulesDir = Join-Path $ResolvedProjectPath ".agents\rules"
if (Test-Path $SourceRulesDir) {
    if (-not (Test-Path $TargetRulesDir)) {
        New-Item -ItemType Directory -Path $TargetRulesDir -Force | Out-Null
    }
    Get-ChildItem -Path $SourceRulesDir -Filter "*.md" | ForEach-Object {
        $dest = Join-Path $TargetRulesDir $_.Name
        if ($Update -or (-not (Test-Path $dest))) {
            Copy-Item -Path $_.FullName -Destination $dest -Force
            Write-Host "  [OK] Synced rule: .agents/rules/$($_.Name)" -ForegroundColor Green
        }
    }
}

# ==============================================================================
# 5. Deploy / Update Skills (.agents/skills/ & .claude/skills/)
# ==============================================================================
Write-Host "`n>>> [3/3] Deploying integrated skills library..." -ForegroundColor Yellow

$TargetSkillsDir = Join-Path $ResolvedProjectPath ".agents\skills"
$TargetClaudeSkillsDir = Join-Path $ResolvedProjectPath ".claude\skills"

if (-not (Test-Path $TargetSkillsDir)) {
    New-Item -ItemType Directory -Path $TargetSkillsDir -Force | Out-Null
}
if (-not (Test-Path $TargetClaudeSkillsDir)) {
    New-Item -ItemType Directory -Path $TargetClaudeSkillsDir -Force | Out-Null
}

if (Test-Path $SourceSkillsDir) {
    Get-ChildItem -Path $SourceSkillsDir -Directory | ForEach-Object {
        $skillName = $_.Name
        $targetSkillPath = Join-Path $TargetSkillsDir $skillName
        
        # Copy / Update skill files
        if ($Update -or (-not (Test-Path $targetSkillPath))) {
            Copy-Item -Path $_.FullName -Destination $targetSkillPath -Recurse -Force
            Write-Host "  [OK] Deployed skill: .agents/skills/$skillName" -ForegroundColor Green
        } else {
            Write-Host "  [INFO] Skill .agents/skills/$skillName already exists." -ForegroundColor Gray
        }

        # Create Claude Code junction / symlink
        $claudeSkillLink = Join-Path $TargetClaudeSkillsDir $skillName
        if (-not (Test-Path $claudeSkillLink)) {
            try {
                New-Item -ItemType Junction -Path $claudeSkillLink -Target $targetSkillPath -ErrorAction Stop | Out-Null
                Write-Host "  [OK] Created Claude junction: .claude/skills/$skillName" -ForegroundColor Green
            } catch {
                # Fallback to copy if junction fails
                Copy-Item -Path $targetSkillPath -Destination $claudeSkillLink -Recurse -Force
                Write-Host "  [OK] Copied Claude skill: .claude/skills/$skillName" -ForegroundColor Green
            }
        }
    }
}

# Deploy skills-lock.json
if (Test-Path $SourceSkillsLock) {
    $targetSkillsLock = Join-Path $ResolvedProjectPath "skills-lock.json"
    if ($Update -or (-not (Test-Path $targetSkillsLock))) {
        Copy-Item -Path $SourceSkillsLock -Destination $targetSkillsLock -Force
        Write-Host "  [OK] Synced skills-lock.json" -ForegroundColor Green
    }
}

# ==============================================================================
# 6. Initialize Tasks Tracking (lessons.md & todo.md)
# ==============================================================================
$TargetTasksDir = Join-Path $ResolvedProjectPath "tasks"
if (-not (Test-Path $TargetTasksDir)) {
    New-Item -ItemType Directory -Path $TargetTasksDir -Force | Out-Null
}

$LessonsFile = Join-Path $TargetTasksDir "lessons.md"
if (-not (Test-Path $LessonsFile)) {
    $starterLessons = @"
# Lessons Learned (项目错题本)

> 本文件记录人类纠偏与架构踩坑经验。Agent 在开始新会话或类似改动前优先阅读，**同一错误绝不犯第二次**。

## 历史经验记录
- [INIT] 项目初始化完成，已接入 Harness 渐进式披露规约与技能库。
"@
    Set-Content -Path $LessonsFile -Value $starterLessons -Encoding UTF8
    Write-Host "  [OK] Initialized tasks/lessons.md" -ForegroundColor Green
}

$TodoFile = Join-Path $TargetTasksDir "todo.md"
if (-not (Test-Path $TodoFile)) {
    $starterTodo = @"
# Task Checklist

> 复杂任务（>= 3 步）在此维护打勾清单，实时更新进度。

- [x] 项目基础规则与 Harness 技能库部署就绪
"@
    Set-Content -Path $TodoFile -Value $starterTodo -Encoding UTF8
    Write-Host "  [OK] Initialized tasks/todo.md" -ForegroundColor Green
}

# ==============================================================================
# 7. Initialize OpenSpec Scaffold (docs/openspec/changes)
# ==============================================================================
$TargetOpenSpecChanges = Join-Path $ResolvedProjectPath "docs\openspec\changes"
if (-not (Test-Path $TargetOpenSpecChanges)) {
    New-Item -ItemType Directory -Path $TargetOpenSpecChanges -Force | Out-Null
    Write-Host "  [OK] Initialized OpenSpec scaffold: docs/openspec/changes" -ForegroundColor Green
}

# ==============================================================================
# 8. Optional Comet CLI Init (-CometInit)
# ==============================================================================
$cometCli = Get-Command "comet" -ErrorAction SilentlyContinue
if ($CometInit) {
    if ($cometCli) {
        Write-Host "`n>>> Running 'comet init' in target project..." -ForegroundColor Yellow
        try {
            Push-Location $ResolvedProjectPath
            & comet init
            Pop-Location
            Write-Host "  [OK] Comet initialization completed." -ForegroundColor Green
        } catch {
            Pop-Location
            Write-Warning "comet init encountered an issue: $_"
        }
    } else {
        Write-Warning "'-CometInit' was specified, but 'comet' CLI is not found in PATH. Install via: npm install -g @rpamis/comet"
    }
}

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host " Deployment completed successfully!" -ForegroundColor Green
Write-Host " Target Project: $ResolvedProjectPath" -ForegroundColor Cyan
Write-Host " Rules Directory: $TargetRulesDir" -ForegroundColor Cyan
Write-Host " Skills Directory: $TargetSkillsDir" -ForegroundColor Cyan
if ($cometCli) {
    Write-Host "`n[TIP] Detected Comet CLI in system. To enable native terminal state machine & hooks, you can run:`n      cd `"$ResolvedProjectPath`"; comet init" -ForegroundColor Yellow
} else {
    Write-Host "`n[INFO] Skills & rules are fully ready in conversation." -ForegroundColor Gray
    Write-Host "       For terminal CLI (comet doctor/status), install: npm install -g @rpamis/comet" -ForegroundColor Gray
}
Write-Host "==================================================" -ForegroundColor Green

