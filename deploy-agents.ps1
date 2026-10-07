# ==============================================================================
# deploy-agents.ps1
# Platforms: Windows (PowerShell 5.1 / PowerShell 7+)
# Purpose: One-click deploy & online update AI Agents Harness spec, rules & skills
#          (Supports Codex / Claude Code / Antigravity 2.0 / CLI / IDE)
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
    [switch]$CometInit
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

function Backup-ManagedPath([string]$Path) {
    if (Test-Path $Path) {
        $backupPath = "$Path.bak.$(Get-Date -Format yyyyMMddHHmmss)"
        Copy-Item -Path $Path -Destination $backupPath -Recurse -Force
    }
}

function Backup-GlobalRule([string]$Path) {
    $backupBase = "$Path.bak.$(Get-Date -Format yyyyMMddHHmmssfff)"
    $backupPath = $backupBase
    $suffix = 1
    while (Test-Path -LiteralPath $backupPath) {
        $backupPath = "$backupBase.$suffix"
        $suffix++
    }
    Copy-Item -LiteralPath $Path -Destination $backupPath -Force
    return $backupPath
}

function Sync-GlobalRule([string]$TemplatePath, [string]$TargetPath, [string]$ToolName, [bool]$UpdateExisting) {
    $targetDirectory = Split-Path -Parent $TargetPath
    New-Item -ItemType Directory -Path $targetDirectory -Force | Out-Null

    if (Test-Path -LiteralPath $TargetPath) {
        if (-not (Test-Path -LiteralPath $TargetPath -PathType Leaf)) {
            throw "Global rule target exists but is not a file: $TargetPath"
        }
        if (-not $UpdateExisting) {
            Write-Host "  [INFO] Preserved existing $ToolName global rule: $TargetPath (use -Update to back up and replace it)." -ForegroundColor Gray
            return
        }

        $backupPath = Backup-GlobalRule $TargetPath
        Copy-Item -LiteralPath $TemplatePath -Destination $TargetPath -Force
        Write-Host "  [OK] Updated $ToolName global rule: $TargetPath (backup: $backupPath)" -ForegroundColor Green
        return
    }

    Copy-Item -LiteralPath $TemplatePath -Destination $TargetPath
    Write-Host "  [OK] Initialized $ToolName global rule: $TargetPath" -ForegroundColor Green
}

function Confirm-OptionalStep([string]$Prompt) {
    if ([Console]::IsInputRedirected) {
        Write-Host "  [INFO] Non-interactive session; skipped: $Prompt"
        return $false
    }
    $answer = Read-Host "$Prompt [y/N]"
    return $answer -match '^(?i:y|yes)$'
}

function Guide-OptionalCliTools([string]$TargetPath) {
    $codegraphInstall = 'irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex'
    $rtkInstall = 'winget install rtk-ai.rtk'

    Write-Host "`n>>> Optional CLI tools (Ponytail and Caveman Skills are already copied with the project)" -ForegroundColor Cyan

    if (Get-Command codegraph -ErrorAction SilentlyContinue) {
        Write-Host "  [OK] CodeGraph CLI detected." -ForegroundColor Green
    } else {
        Write-Host "  CodeGraph CLI is optional. It connects agents and builds a local project index."
        if (Confirm-OptionalStep "Install CodeGraph CLI now? Agent wiring and project indexing will be asked separately") {
            try {
                Invoke-Expression (Invoke-RestMethod 'https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1')
                Write-Host "  [INFO] Reopen PowerShell if codegraph is not yet on PATH. Then run codegraph install and codegraph init from the project directory." -ForegroundColor Yellow
            } catch {
                Write-Warning "CodeGraph installation failed. Official command: $codegraphInstall"
            }
        } else {
            Write-Host "  Install command: $codegraphInstall"
            Write-Host "  After installation: run codegraph install, then codegraph init from the project directory."
        }
    }

    if (Get-Command codegraph -ErrorAction SilentlyContinue) {
        if (Confirm-OptionalStep "Run codegraph install to configure agents, then codegraph init in this project") {
            try { & codegraph install; if ($LASTEXITCODE -ne 0) { Write-Warning "CodeGraph agent setup exited with $LASTEXITCODE." } } catch { Write-Warning "Agent setup did not complete: $_" }
            Push-Location $TargetPath
            try { & codegraph init; if ($LASTEXITCODE -ne 0) { Write-Warning "CodeGraph project indexing exited with $LASTEXITCODE." } } catch {
                Write-Warning "Project indexing did not complete. Run 'codegraph init' in the project later."
            } finally { Pop-Location }
        } else {
            Write-Host "  Later: codegraph install; then run 'codegraph init' from the project directory."
        }
    }

    $rtkReady = $false
    if (Get-Command rtk -ErrorAction SilentlyContinue) {
        try { & rtk gain *> $null; $rtkReady = ($LASTEXITCODE -eq 0) } catch { $rtkReady = $false }
    }
    if ($rtkReady) {
        Write-Host "  [OK] Rust Token Killer (RTK) CLI detected." -ForegroundColor Green
    } else {
        Write-Host "  RTK CLI is optional. The 'rtk' name is shared by unrelated tools; verify with 'rtk gain'."
        if (Confirm-OptionalStep "Install Rust Token Killer (RTK) CLI now?") {
            if (Get-Command winget -ErrorAction SilentlyContinue) {
                & winget install rtk-ai.rtk
                if ($LASTEXITCODE -ne 0) { Write-Warning "RTK installation failed. Official command: $rtkInstall" }
                Write-Host "  [INFO] Reopen PowerShell, run rtk gain to verify, then run rtk init in the project if you want the hook." -ForegroundColor Yellow
            } else {
                Write-Warning "winget is unavailable. Install from https://github.com/rtk-ai/rtk/releases and place rtk.exe on PATH. Then verify with rtk gain and run rtk init in the project if you want the hook."
            }
        } else {
            Write-Host "  Install command: $rtkInstall; verify with rtk gain, then run rtk init in the project to configure a supported hook."
        }
    }

    $rtkReady = $false
    if (Get-Command rtk -ErrorAction SilentlyContinue) {
        try { & rtk gain *> $null; $rtkReady = ($LASTEXITCODE -eq 0) } catch { $rtkReady = $false }
    }
    if ($rtkReady) {
        if (Confirm-OptionalStep "Run 'rtk init' in this project to configure the RTK hook") {
            Push-Location $TargetPath
            try { & rtk init; if ($LASTEXITCODE -ne 0) { Write-Warning "RTK project setup exited with $LASTEXITCODE." } } catch {
                Write-Warning "RTK project setup did not complete; run 'rtk init' in the project later."
            } finally { Pop-Location }
        } else {
            Write-Host "  Later: run 'rtk init' from the project directory."
        }
    }
}

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
            & git -C "$ScriptDir" pull --ff-only 2>&1 | Write-Host
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] Git repository up to date." -ForegroundColor Green
            } else {
                Write-Warning "git pull --ff-only failed (exit $LASTEXITCODE); continuing with current templates."
            }
        } catch {
            Write-Warning "Failed to git pull: $_"
        }
    } else {
        Write-Host "  [INFO] Template directory is not a Git repo; skipping git pull." -ForegroundColor Gray
    }

    Write-Host "  [INFO] Updating this template repository only; global CLIs and the caller's current directory are not modified." -ForegroundColor Gray
}

# If no ProjectPath is specified and not -Global, show usage
if (-not $ProjectPath -and -not $Global) {
    Write-Host "`n[用法说明] Usage:" -ForegroundColor Cyan
    Write-Host "  .\deploy-agents.ps1 -ProjectPath <目标项目路径> [-Global] [-Update]"
    Write-Host "  .\deploy-agents.ps1 -Global [-Update]   # 初始化全局配置；-Update 先备份再覆盖已有规则"
    Write-Host ""
    Write-Host "[参数说明] Parameters:" -ForegroundColor Cyan
    Write-Host "  -ProjectPath   目标项目根目录路径。"
    Write-Host "  -Global (-g)   初始化 Claude、Antigravity 2.0/CLI/IDE、Codex 用户全局规则。"
    Write-Host "  -Update (-u)   更新模板仓库；与 -Global 一起使用时，先备份再覆盖全局规则。"
    exit 0
}

# ==============================================================================
# 2. Deploy / Update Global Rules (-Global)
# ==============================================================================
if ($Global) {
    Write-Host "`n>>> [1/3] Deploying/Updating global rules..." -ForegroundColor Yellow

    $AntigravityGeminiTemplate = Join-Path $ScriptDir "templates\antigravity-GEMINI.md"
    if (-not (Test-Path $ResolvedGlobalTemplate)) {
        Write-Warning "Global template not found, skipping global setup."
    } else {
        # A. Claude Code (~/.claude/CLAUDE.md)
        $ClaudeGlobalDir = Join-Path $HOME ".claude"
        $ClaudeGlobalFile = Join-Path $ClaudeGlobalDir "CLAUDE.md"
        Sync-GlobalRule $ResolvedGlobalTemplate $ClaudeGlobalFile "Claude Code" $Update

        # B. Current Antigravity releases load AGENTS.md; GEMINI.md is a compatibility entry for older surfaces.
        $AntigravityGlobalDir = Join-Path $HOME ".gemini"
        $AntigravityGlobalFile = Join-Path $AntigravityGlobalDir "AGENTS.md"
        Sync-GlobalRule $ResolvedGlobalTemplate $AntigravityGlobalFile "Antigravity 2.0 / CLI / IDE" $Update
        $AntigravityGeminiFile = Join-Path $AntigravityGlobalDir "GEMINI.md"
        if (Test-Path -LiteralPath $AntigravityGeminiTemplate -PathType Leaf) {
            Sync-GlobalRule $AntigravityGeminiTemplate $AntigravityGeminiFile "Antigravity legacy GEMINI.md compatibility" $Update
        } else {
            Write-Warning "Antigravity GEMINI.md compatibility template not found: $AntigravityGeminiTemplate"
        }

        # C. Codex CLI / app (~/.codex by default, or $CODEX_HOME)
        $CodexGlobalDir = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) { Join-Path $HOME ".codex" } else { [Environment]::ExpandEnvironmentVariables($env:CODEX_HOME) }
        $CodexOverrideFile = Join-Path $CodexGlobalDir "AGENTS.override.md"
        $CodexGlobalFile = Join-Path $CodexGlobalDir "AGENTS.md"
        if ((Test-Path -LiteralPath $CodexOverrideFile -PathType Leaf) -and (Get-Item -LiteralPath $CodexOverrideFile).Length -gt 0) {
            $CodexGlobalFile = $CodexOverrideFile
            Write-Host "  [INFO] Active Codex global override detected; updating that effective instruction file." -ForegroundColor Gray
        }
        Sync-GlobalRule $ResolvedGlobalTemplate $CodexGlobalFile "Codex" $Update
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

# Note: no Zed-specific configuration is created.

# Deploy Claude Code PreToolUse Security Hooks (.claude/settings.json + .claude/hooks/)
if (Test-Path $SourceClaudeSettings) {
    $TargetClaudeDir = Join-Path $ResolvedProjectPath ".claude"
    if (-not (Test-Path $TargetClaudeDir)) {
        New-Item -ItemType Directory -Path $TargetClaudeDir -Force | Out-Null
    }
    $TargetClaudeSettings = Join-Path $TargetClaudeDir "settings.json"
    if ($Update -or (-not (Test-Path $TargetClaudeSettings))) {
        if ($Update) { Backup-ManagedPath $TargetClaudeSettings }
        Copy-Item -Path $SourceClaudeSettings -Destination $TargetClaudeSettings -Force
        Write-Host "  [OK] Deployed Claude Code security hooks: .claude/settings.json" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] .claude/settings.json already exists, keeping existing file." -ForegroundColor Gray
    }
    # Deploy hook scripts (.claude/hooks/)
    $SourceHooksDir = Join-Path $ScriptDir ".claude\hooks"
    if (Test-Path $SourceHooksDir) {
        $TargetHooksDir = Join-Path $TargetClaudeDir "hooks"
        if (-not (Test-Path $TargetHooksDir)) {
            New-Item -ItemType Directory -Path $TargetHooksDir -Force | Out-Null
        }
        Get-ChildItem -Path $SourceHooksDir -File | ForEach-Object {
            $targetHook = Join-Path $TargetHooksDir $_.Name
            if ($Update -or (-not (Test-Path $targetHook))) {
                if ($Update) { Backup-ManagedPath $targetHook }
                Copy-Item -Path $_.FullName -Destination $targetHook -Force
            }
        }
        Write-Host "  [OK] Deployed hook scripts: .claude/hooks/" -ForegroundColor Green
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
            if ($Update) { Backup-ManagedPath $dest }
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
            if ($Update) {
                Backup-ManagedPath $targetSkillPath
                Remove-Item -Path $targetSkillPath -Recurse -Force
            }
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
        if ($Update) { Backup-ManagedPath $targetSkillsLock }
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

Guide-OptionalCliTools $ResolvedProjectPath

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host " Deployment completed successfully!" -ForegroundColor Green
Write-Host " Target Project: $ResolvedProjectPath" -ForegroundColor Cyan
Write-Host " Rules Directory: $TargetRulesDir" -ForegroundColor Cyan
Write-Host " Skills Directory: $TargetSkillsDir" -ForegroundColor Cyan
if ($cometCli) {
    Write-Host "`n[TIP] Comet CLI is installed. Use its current documentation to configure a workflow for this project." -ForegroundColor Yellow
} else {
    Write-Host "`n[INFO] Rule and skill files were deployed. Whether they load automatically depends on the host tool." -ForegroundColor Gray
}
Write-Host "==================================================" -ForegroundColor Green
