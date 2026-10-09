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

    [Alias("i")]
    [switch]$Initialize,

    [Alias("k")]
    [switch]$Check,

    [string]$DirectoryPath,

    [Alias("c")]
    [switch]$CometInit,

    [Alias("m")]
    [switch]$AiMemoryInit
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
$SourceAiMemoryExample = Join-Path $ScriptDir ".ai-memory.toml.example"

function Backup-ManagedPath([string]$Path) {
    if (Test-Path $Path) {
        $backupPath = "$Path.bak.$(Get-Date -Format yyyyMMddHHmmss)"
        Copy-Item -Path $Path -Destination $backupPath -Recurse -Force
    }
}
$ResolvedDirectoryTemplate = Join-Path $ScriptDir "Directory AGENTS.md"

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

    if (Get-Command ocr -ErrorAction SilentlyContinue) {
        Write-Host "  [OK] Open Code Review CLI (ocr) detected: Tier A delegation review is available via the open-code-review skill." -ForegroundColor Green
    } else {
        Write-Host "  Open Code Review CLI (ocr) is optional. The open-code-review skill works without it (Tier B methodology mode); installing enables zero-LLM-cost delegation review."
        if (Confirm-OptionalStep "Install Open Code Review CLI now?") {
            & npm install -g @alibaba-group/open-code-review
            if ($LASTEXITCODE -ne 0) { Write-Warning "ocr installation failed. Manual command: npm install -g @alibaba-group/open-code-review" }
            else { Write-Host "  [INFO] ocr installed. Delegation mode needs no LLM key; the host agent performs the review." -ForegroundColor Yellow }
        } else {
            Write-Host "  Install command: npm install -g @alibaba-group/open-code-review"
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
    Write-Host "  -Initialize (-i) 识别项目事实并生成规则，未知项加入待确认清单。"
    Write-Host "  -DirectoryPath   配合 -Initialize 或 -Check，指定项目内已有子目录。"
    Write-Host "  -Check (-k)      检查项目/指定目录 AGENTS.md 中尚未处理的占位项。"
    Write-Host "  -ProjectPath   目标项目根目录路径。"
    Write-Host "  -Global (-g)   初始化 Claude、Antigravity 2.0/CLI/IDE、Codex 用户全局规则。"
    Write-Host "  -Update (-u)   更新模板仓库；与 -Global 一起使用时，先备份再覆盖全局规则。"
    exit 0
}
if ($DirectoryPath -and -not ($Initialize -or $Check)) { throw "-DirectoryPath requires -Initialize or -Check." }
if (($Initialize -or $Check) -and -not $ProjectPath) { throw "-Initialize and -Check require -ProjectPath." }
if ($Check -and $Global) { throw "-Check cannot be combined with -Global." }

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

function Get-InitSuggestions([string]$Root, [string]$Scope) {
    $values = @{}
    if ($Scope -eq "project") {
        $values["PROJECT_NAME"] = Split-Path -Leaf $Root.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        if (Get-Command git -ErrorAction SilentlyContinue) {
            $remote = (& git -C $Root remote get-url origin 2>$null | Select-Object -First 1)
            if ($LASTEXITCODE -eq 0 -and $remote -and $remote -notmatch '://[^/]*@') { $values["REPOSITORY_URL"] = $remote.Trim() }
            $branch = (& git -C $Root symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>$null | Select-Object -First 1)
            if ($LASTEXITCODE -eq 0 -and $branch -match '^origin/(.+)$') { $values["DEFAULT_BRANCH"] = $Matches[1] }
        }
        $manifests = @(
            @{ File = 'package.json'; Name = 'JavaScript/TypeScript (package.json; runtime version to confirm)' },
            @{ File = 'pyproject.toml'; Name = 'Python (pyproject.toml; runtime version to confirm)' },
            @{ File = 'Cargo.toml'; Name = 'Rust (Cargo.toml)' },
            @{ File = 'go.mod'; Name = 'Go (go.mod)' },
            @{ File = 'CMakeLists.txt'; Name = 'C/C++ (CMakeLists.txt)' },
            @{ File = '*.csproj'; Name = '.NET (project file)' }
        ) | Where-Object { (Test-Path -LiteralPath (Join-Path $Root $_.File)) -or (Get-ChildItem -Path $Root -Filter $_.File -File -ErrorAction SilentlyContinue | Select-Object -First 1) }
        if ($manifests) { $values["LANGUAGE_AND_VERSION"] = (($manifests | ForEach-Object Name) -join '; ') }
        $locks = @(
            @{ File = 'pnpm-lock.yaml'; Name = 'pnpm' }, @{ File = 'yarn.lock'; Name = 'Yarn' },
            @{ File = 'package-lock.json'; Name = 'npm' }, @{ File = 'uv.lock'; Name = 'uv' },
            @{ File = 'poetry.lock'; Name = 'Poetry' }, @{ File = 'Cargo.lock'; Name = 'Cargo' },
            @{ File = 'go.sum'; Name = 'Go modules' }, @{ File = 'Pipfile.lock'; Name = 'Pipenv' }
        ) | Where-Object { Test-Path (Join-Path $Root $_.File) }
        if ($locks) { $values["PACKAGE_MANAGER"] = (($locks | ForEach-Object Name) -join ', ') }
        $ci = @()
        $workflowDir = Join-Path $Root '.github\workflows'
        if (Test-Path $workflowDir) { $ci += (Get-ChildItem $workflowDir -File | ForEach-Object { '.github/workflows/' + $_.Name }) }
        foreach ($file in @('.gitlab-ci.yml', 'Jenkinsfile', 'azure-pipelines.yml')) { if (Test-Path (Join-Path $Root $file)) { $ci += $file } }
        if ($ci) { $values["CI_PATH"] = $ci -join ', ' }
        $readme = Join-Path $Root 'README.md'
        if (Test-Path $readme) {
            $summary = Get-Content $readme -TotalCount 40 | Where-Object { $_.Trim() -and $_ -notmatch '^\s*#' } | Select-Object -First 1
            if ($summary) { $values["PROJECT_PURPOSE"] = $summary.Trim() }
        }
    } else {
        $values["MODULE_NAME"] = Split-Path -Leaf $Root.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    }
    $packageJson = Join-Path $Root 'package.json'
    if (Test-Path -LiteralPath $packageJson -PathType Leaf) {
        try { $package = Get-Content -LiteralPath $packageJson -Raw | ConvertFrom-Json -ErrorAction Stop } catch { $package = $null }
        if ($package) {
            $manager = [string]$package.packageManager
            if (-not $manager) {
                if (Test-Path -LiteralPath (Join-Path $Root 'pnpm-lock.yaml')) { $manager = 'pnpm' }
                elseif (Test-Path -LiteralPath (Join-Path $Root 'yarn.lock')) { $manager = 'yarn' }
                elseif (Test-Path -LiteralPath (Join-Path $Root 'package-lock.json')) { $manager = 'npm' }
            } else { $manager = ($manager -split '@')[0] }
            $runPrefix = if ($manager -in @('pnpm','yarn')) { "$manager run" } else { 'npm run' }
            if ($Scope -eq 'project' -and $manager) {
                $values['PACKAGE_MANAGER'] = "建议确认：$manager（由 package.json/锁文件识别）"
                $install = switch ($manager) { 'pnpm' { 'pnpm install --frozen-lockfile' } 'yarn' { 'yarn install --immutable' } default { 'npm ci' } }
                $values['INSTALL_COMMAND'] = "建议确认：$install（根据锁文件推导）"
            }
            $scripts = @{}
            if ($package.scripts) { foreach ($property in $package.scripts.PSObject.Properties) { $scripts[$property.Name] = $property.Value } }
            $scriptValues = @{
                DEV_COMMAND = @('dev'); BUILD_COMMAND = @('build'); UNIT_TEST_COMMAND = @('test','test:unit');
                INTEGRATION_TEST_COMMAND = @('test:e2e','test:integration','e2e'); LINT_COMMAND = @('lint');
                FORMAT_COMMAND = @('format','fmt'); TYPE_CHECK_COMMAND = @('typecheck','type-check');
                MIGRATION_COMMAND = @('db:migrate','migrate')
            }
            foreach ($entry in $scriptValues.GetEnumerator()) {
                foreach ($scriptName in $entry.Value) {
                    if ($scripts.ContainsKey($scriptName)) {
                        $suggested = "建议确认：$runPrefix $scriptName（package.json scripts.$scriptName）"
                        if ($Scope -eq 'project') { $values[$entry.Key] = $suggested }
                        if ($Scope -eq 'project' -and $entry.Key -eq 'UNIT_TEST_COMMAND') { $values['TARGETED_TEST_COMMAND'] = "建议确认：$runPrefix $scriptName -- <test-path>（需核验测试运行器参数）" }
                        if ($Scope -eq 'directory' -and $scriptName -in @('test','test:unit')) { $values['LOCAL_TEST_COMMAND'] = $suggested }
                        if ($Scope -eq 'directory' -and $scriptName -eq 'lint') { $values['LOCAL_LINT_COMMAND'] = $suggested }
                        break
                    }
                }
            }
            if ($Scope -eq 'project') {
                $deps = @()
                foreach ($source in @($package.dependencies, $package.devDependencies)) {
                    if ($source) { $deps += $source.PSObject.Properties.Name }
                }
                $frameworks = @()
                foreach ($framework in @(@{ Package='next'; Name='Next.js' }, @{ Package='react'; Name='React' }, @{ Package='vue'; Name='Vue' }, @{ Package='@angular/core'; Name='Angular' }, @{ Package='express'; Name='Express' }, @{ Package='fastify'; Name='Fastify' })) {
                    if ($deps -contains $framework.Package) { $frameworks += $framework.Name }
                }
                if ($frameworks) { $values['FRAMEWORK'] = "建议确认：$($frameworks -join ', ')（package.json dependencies）" }
                $stores = $deps | Where-Object { $_ -match '^(pg|mysql2?|sqlite3?|mongoose|prisma|@prisma/client|redis|ioredis)$' } | Sort-Object -Unique
                if ($stores) { $values['DATABASE_AND_CACHE'] = "建议确认：$($stores -join ', ')（依赖清单；实际运行配置需复核）" }
            }
        }
    }
    return $values
}

function Initialize-AgentInstructions([string]$TemplatePath, [string]$OutputPath, [string]$Scope, [string]$DisplayPath) {
    $values = Get-InitSuggestions $DisplayPath $Scope
    if ($Scope -eq 'directory') {
        $baseUri = [Uri]($ResolvedProjectPath.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar)
        $relative = [Uri]::UnescapeDataString($baseUri.MakeRelativeUri([Uri]$DisplayPath).ToString())
        $values['DIRECTORY_PATH'] = $relative
        if ([Console]::IsInputRedirected) {
            $values['RESPONSIBILITY'] = '待 Agent 检查并向用户确认'
        } else {
            $answer = Read-Host '请用一句话说明该目录的职责（留空则交给 Agent 根据代码检查）'
            $values['RESPONSIBILITY'] = if ($answer.Trim()) { $answer.Trim() } else { '待 Agent 检查并向用户确认' }
        }
    } else {
        if ([Console]::IsInputRedirected) {
            $values['PROJECT_PURPOSE'] = '待确认（README 摘要需核实）'
            $values['OWNERS'] = '待用户确认（不从 Git 提交记录推断）'
        } else {
            $purposeDefault = $values['PROJECT_PURPOSE']
            $purposePrompt = if ($purposeDefault) { "项目用途（回车接受 README 摘要：$purposeDefault）" } else { '项目用途（一句话）' }
            $purpose = Read-Host $purposePrompt
            if ($purpose.Trim()) { $values['PROJECT_PURPOSE'] = $purpose.Trim() }
            elseif (-not $purposeDefault) { $values['PROJECT_PURPOSE'] = '待用户确认' }
            $owners = Read-Host '核心维护者（可填团队/账号；留空标记待确认）'
            $values['OWNERS'] = if ($owners.Trim()) { $owners.Trim() } else { '待用户确认' }
        }
    }
    $text = [IO.File]::ReadAllText($TemplatePath)
    $pending = [Collections.Generic.List[string]]::new()
    $text = [regex]::Replace($text, '<([A-Z][A-Z0-9_]*)>', [System.Text.RegularExpressions.MatchEvaluator]{
        param($match)
        $key = $match.Groups[1].Value
        if ($values.ContainsKey($key) -and -not [string]::IsNullOrWhiteSpace([string]$values[$key])) {
            if ([string]$values[$key] -match '^(待|建议确认：)') { $pending.Add($key) }
            return [string]$values[$key]
        }
        $pending.Add($key)
        return "待确认（$key）"
    }.GetNewClosure())
    $status = if ($pending.Count) { "## 初始化待确认项`r`n`r`n" + (($pending | Select-Object -Unique | ForEach-Object { "- $($_)" }) -join "`r`n") + "`r`n`r`n" } else { "## 初始化状态`r`n`r`n自动识别字段已填充；请复核后使用。`r`n`r`n" }
    $text = $text -replace '(?s)\A', ($status + "<!-- Generated by deploy-agents.ps1 -Initialize; review before use. -->`r`n`r`n")
    Set-Content -LiteralPath $OutputPath -Value $text -Encoding UTF8
    Write-Host "  [OK] Initialized guidance file: $OutputPath" -ForegroundColor Green
    if ($pending.Count) {
        Write-Host "  [INFO] Fields needing agent inspection or human confirmation: $(($pending | Select-Object -Unique) -join ', ')" -ForegroundColor Yellow
        Write-Host '  [NEXT] Ask your coding agent: Inspect the initialization checklist in this file, fill only facts supported by repository evidence, ask me about business purpose/ownership/module boundaries when needed, and do not guess.' -ForegroundColor Cyan
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
if (($Initialize -or $Check) -and $DirectoryPath) {
    if ([IO.Path]::IsPathRooted($DirectoryPath)) { throw "-DirectoryPath must be relative to -ProjectPath." }
    $directoryRoot = [IO.Path]::GetFullPath((Join-Path $ResolvedProjectPath $DirectoryPath))
    $projectPrefix = $ResolvedProjectPath.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $directoryRoot.StartsWith($projectPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw "-DirectoryPath must remain inside the project." }
    if (-not (Test-Path -LiteralPath $directoryRoot -PathType Container)) { throw "Directory does not exist: $DirectoryPath" }
    $pathCursor = $directoryRoot
    while ($pathCursor.StartsWith($projectPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        if ((Get-Item -LiteralPath $pathCursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "-DirectoryPath cannot traverse a reparse point: $pathCursor" }
        $pathCursor = Split-Path -Parent $pathCursor
    }
    if (-not (Test-Path -LiteralPath $ResolvedDirectoryTemplate -PathType Leaf)) { throw "Directory template not found: $ResolvedDirectoryTemplate" }
}
if ($Initialize -and (Test-Path -LiteralPath (Join-Path $ResolvedProjectPath 'AGENTS.md') -PathType Leaf) -and (Test-Path -LiteralPath (Join-Path $ResolvedProjectPath 'AGENTS.generated.md'))) {
    throw "Refusing to overwrite existing generated project guidance: $(Join-Path $ResolvedProjectPath 'AGENTS.generated.md')"
}
if ($Initialize -and $DirectoryPath -and (Test-Path -LiteralPath (Join-Path $directoryRoot 'AGENTS.md') -PathType Leaf) -and (Test-Path -LiteralPath (Join-Path $directoryRoot 'AGENTS.generated.md'))) {
    throw "Refusing to overwrite existing generated directory guidance: $(Join-Path $directoryRoot 'AGENTS.generated.md')"
}
if ($Check) {
    $checkFiles = @((Join-Path $ResolvedProjectPath 'AGENTS.md'), (Join-Path $ResolvedProjectPath 'AGENTS.generated.md'))
    if ($DirectoryPath) { $checkFiles += (Join-Path $directoryRoot 'AGENTS.md'), (Join-Path $directoryRoot 'AGENTS.generated.md') }
    $incomplete = $false
    $checkedCount = 0
    foreach ($file in $checkFiles) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { continue }
        $checkedCount++
        $matches = Select-String -LiteralPath $file -Pattern '<[A-Z][A-Z0-9_]*>|待确认（[A-Z][A-Z0-9_]*）|待用户确认|待 Agent 检查|建议确认：' -AllMatches
        if ($matches) { Write-Host "[!] Unresolved fields in $file" -ForegroundColor Yellow; $matches | ForEach-Object { Write-Host "    line $($_.LineNumber): $($_.Line.Trim())" }; $incomplete = $true }
        else { Write-Host "[OK] No initialization placeholders: $file" -ForegroundColor Green }
    }
    if (-not $checkedCount) { Write-Host '[!] No AGENTS.md or AGENTS.generated.md found to check.' -ForegroundColor Yellow; $incomplete = $true }
    if ($incomplete) { exit 1 }
    exit 0
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Target Project: $ResolvedProjectPath" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# ==============================================================================
# 3. Deploy / Update Project-level AGENTS.md & Bridges
# ==============================================================================
Write-Host "`n>>> [2/3] Deploying project rules and tool bridges..." -ForegroundColor Yellow

$TargetAgentsFile = Join-Path $ResolvedProjectPath "AGENTS.md"
$HadProjectAgents = Test-Path -LiteralPath $TargetAgentsFile -PathType Leaf
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

if ($Initialize) {
    $projectOutput = if ($HadProjectAgents) { Join-Path $ResolvedProjectPath "AGENTS.generated.md" } else { $TargetAgentsFile }
    if ($HadProjectAgents -and (Test-Path -LiteralPath $projectOutput)) { throw "Refusing to overwrite existing generated guidance: $projectOutput" }
    Initialize-AgentInstructions $ResolvedProjectTemplate $projectOutput 'project' $ResolvedProjectPath

    if ($DirectoryPath) {
        if ([IO.Path]::IsPathRooted($DirectoryPath)) { throw "-DirectoryPath must be relative to -ProjectPath." }
        $directoryRoot = [IO.Path]::GetFullPath((Join-Path $ResolvedProjectPath $DirectoryPath))
        $projectPrefix = $ResolvedProjectPath.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
        if (-not $directoryRoot.StartsWith($projectPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw "-DirectoryPath must remain inside the project." }
        if (-not (Test-Path -LiteralPath $directoryRoot -PathType Container)) { throw "Directory does not exist: $DirectoryPath" }
        if (-not (Test-Path -LiteralPath $ResolvedDirectoryTemplate -PathType Leaf)) { throw "Directory template not found: $ResolvedDirectoryTemplate" }
        $directoryAgents = Join-Path $directoryRoot 'AGENTS.md'
        $hadDirectoryAgents = Test-Path -LiteralPath $directoryAgents -PathType Leaf
        $directoryOutput = if ($hadDirectoryAgents) { Join-Path $directoryRoot 'AGENTS.generated.md' } else { $directoryAgents }
        if ($hadDirectoryAgents -and (Test-Path -LiteralPath $directoryOutput)) { throw "Refusing to overwrite existing generated guidance: $directoryOutput" }
        Initialize-AgentInstructions $ResolvedDirectoryTemplate $directoryOutput 'directory' $directoryRoot
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

# Sync .ai-memory.toml.example
if (Test-Path $SourceAiMemoryExample) {
    $targetAiMemoryExample = Join-Path $ResolvedProjectPath ".ai-memory.toml.example"
    $targetAiMemory = Join-Path $ResolvedProjectPath ".ai-memory.toml"
    if ((-not (Test-Path $targetAiMemory)) -and (-not (Test-Path $targetAiMemoryExample))) {
        Copy-Item -Path $SourceAiMemoryExample -Destination $targetAiMemoryExample -Force
        Write-Host "  [OK] Synced .ai-memory.toml.example for reference" -ForegroundColor Green
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
# 8. Initialize Living Documentation Scaffold (docs/{specs,architecture,reference,guides,adr})
# ==============================================================================
# LivingDocScaffold
$TargetDocsBase = Join-Path $ResolvedProjectPath "docs"
$docSubdirs = @("specs", "architecture", "reference", "guides", "adr")
foreach ($sub in $docSubdirs) {
    $dirPath = Join-Path $TargetDocsBase $sub
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}
Write-Host "  [OK] Initialized living documentation scaffold: docs/{specs,architecture,reference,guides,adr}" -ForegroundColor Green

# ==============================================================================
# 9. Optional Comet CLI Init (-CometInit)
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

# ==============================================================================
# 10. Optional ai-memory Init (-AiMemoryInit)
# ==============================================================================
$aiMemoryCli = Get-Command "ai-memory" -ErrorAction SilentlyContinue
if ($AiMemoryInit) {
    $TargetAiMemory = Join-Path $ResolvedProjectPath ".ai-memory.toml"
    if (Test-Path $TargetAiMemory) {
        Write-Host "  [i] Target project already has .ai-memory.toml, keeping existing configuration." -ForegroundColor Gray
    } else {
        Write-Host "`n>>> Initializing .ai-memory.toml in target project..." -ForegroundColor Yellow
        $projName = Split-Path -Leaf $ResolvedProjectPath
        $parentPath = Split-Path -Parent $ResolvedProjectPath
        $wsName = if ($parentPath) { Split-Path -Leaf $parentPath } else { $projName }
        if ([string]::IsNullOrWhiteSpace($wsName)) { $wsName = $projName }

        $aiMemoryContent = @"
# Auto-generated by deploy-agents -AiMemoryInit
workspace = "$wsName"
project = "$projName"

[capture]
ignore_paths = [
  "**/.env*",
  "**/*.pem",
  "**/*.key",
  "**/secrets/**",
  "**/credentials/**",
  "**/private/**",
]
"@
        Set-Content -Path $TargetAiMemory -Value $aiMemoryContent -Encoding utf8
        Write-Host "  [OK] Created .ai-memory.toml (workspace: $wsName, project: $projName)" -ForegroundColor Green
    }

    if ($aiMemoryCli) {
        Write-Host "  [OK] Detected ai-memory CLI in PATH." -ForegroundColor Green
    } else {
        Write-Warning "'-AiMemoryInit' was specified, but 'ai-memory' CLI is not found in PATH."
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
} elseif ($aiMemoryCli) {
    Write-Host "`n[TIP] ai-memory CLI is installed. Use -AiMemoryInit or configure .ai-memory.toml to enable cross-tool memory." -ForegroundColor Yellow
} else {
    Write-Host "`n[INFO] Rule and skill files were deployed. Whether they load automatically depends on the host tool." -ForegroundColor Gray
}
Write-Host "==================================================" -ForegroundColor Green
