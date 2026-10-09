[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [ValidateSet('claude-code', 'codex', 'antigravity', 'antigravity-ide', 'antigravity-cli')]
    [string]$Agent
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$markerPath = Join-Path $repoRoot '.ai-memory.toml'

function Prompt-MultiSelect([string]$Title, [array]$Items) {
    if ([Console]::IsInputRedirected) {
        Write-Host $Title
        for ($i = 0; $i -lt $Items.Count; $i++) {
            Write-Host "$($i + 1)) [$($Items[$i].Checked)] $($Items[$i].Label)"
        }
        $resp = Read-Host "Enter numbers separated by space (or press Enter for defaults)"
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
    Write-Host "`n$Title" -ForegroundColor Cyan
    Write-Host "↑↓ move, space select, enter confirm" -ForegroundColor DarkGray

    $count = $Items.Count
    while ($true) {
        for ($i = 0; $i -lt $count; $i++) {
            $pointer = if ($i -eq $cur) { "> " } else { "  " }
            $box = if ($Items[$i].Checked) { "[x] " } else { "[ ] " }
            $fg = if ($i -eq $cur) { "Cyan" } elseif ($Items[$i].Checked) { "Green" } else { "Gray" }
            Write-Host "$pointer$box$($Items[$i].Label)" -ForegroundColor $fg
        }

        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        if ($key.VirtualKeyCode -eq 38) { # Up
            $cur = ($cur - 1 + $count) % $count
        } elseif ($key.VirtualKeyCode -eq 40) { # Down
            $cur = ($cur + 1) % $count
        } elseif ($key.VirtualKeyCode -eq 32) { # Space
            $Items[$cur].Checked = -not $Items[$cur].Checked
        } elseif ($key.VirtualKeyCode -eq 13) { # Enter
            break
        } elseif ($key.Character -eq 'q') {
            Write-Host "Aborted."
            exit 1
        }

        try {
            $pos = $host.UI.RawUI.CursorPosition
            $pos.Y = [Math]::Max(0, $pos.Y - $count)
            $pos.X = 0
            $host.UI.RawUI.CursorPosition = $pos
        } catch {}
    }
    return ($Items | Where-Object { $_.Checked } | ForEach-Object { $_.Value })
}

$selectedAgents = @()
if ($Agent) {
    $selectedAgents = @($Agent)
} else {
    $options = @(
        @{ Label = "Claude Code (hooks + MCP)"; Value = "claude-code"; Checked = $true },
        @{ Label = "OpenAI Codex (hooks + MCP)"; Value = "codex"; Checked = $true },
        @{ Label = "Google Antigravity IDE (MCP + project instructions)"; Value = "antigravity-ide"; Checked = $true },
        @{ Label = "Google Antigravity CLI (hooks + MCP)"; Value = "antigravity-cli"; Checked = $false }
    )
    $selectedAgents = Prompt-MultiSelect "=== Select Agent Tools for ai-memory Integration ===" $options
    if (-not $selectedAgents -or $selectedAgents.Count -eq 0) {
        Write-Host "No agents selected. Exiting."
        exit 0
    }
}

if (-not (Test-Path -LiteralPath $markerPath -PathType Leaf)) {
    throw "Memory is not enabled for this repository. Review .ai-memory.toml.example, create a local .ai-memory.toml with your chosen workspace/project, then rerun."
}

$marker = Get-Content -LiteralPath $markerPath -Raw
if ($marker -match 'replace-with-') {
    throw 'Replace the example workspace/project values before installing integrations.'
}

$aiMemory = Get-Command ai-memory -ErrorAction SilentlyContinue
if (-not $aiMemory) {
    throw 'ai-memory is not installed in this environment. Install it separately using the upstream guide; this helper never downloads or starts it.'
}

$aiMemoryPinnedVersion = '2.6.0'
$verOutput = ((& ai-memory --version 2>$null) | Out-String)
if ($verOutput -notmatch "(^|[^0-9.])$([regex]::Escape($aiMemoryPinnedVersion))([^0-9.]|$)") {
    Write-Warning "ai-memory version mismatch: this repo pins $aiMemoryPinnedVersion (got: $($verOutput.Trim())). Set `$env:AI_MEMORY_ALLOW_OTHER_VERSION='1' to override."
    if ($env:AI_MEMORY_ALLOW_OTHER_VERSION -ne '1') {
        throw "ai-memory version mismatch: expected $aiMemoryPinnedVersion."
    }
}

foreach ($targetAgent in $selectedAgents) {
    if ($targetAgent -in @('claude-code', 'codex', 'antigravity-cli')) {
        $hookPlatform = $env:AI_MEMORY_HOOK_PLATFORM
        if ($hookPlatform -and $hookPlatform -ne 'windows-native') {
            throw "AI_MEMORY_HOOK_PLATFORM='$hookPlatform' selects a non-native or unverified hook mode. Unset it (or use windows-native) before running setup. No integrations were changed."
        }
        if ($aiMemory.Source -notmatch '\.exe$') {
            throw "The resolved ai-memory command is not a native Windows executable ($($aiMemory.Source)). Use the native ai-memory.exe directly; wrappers cannot enforce allowlist capture. No integrations were changed."
        }
        $stream = [System.IO.File]::OpenRead($aiMemory.Source)
        try {
            $magic = New-Object byte[] 2
            if ($stream.Read($magic, 0, 2) -ne 2 -or $magic[0] -ne 0x4D -or $magic[1] -ne 0x5A) {
                throw "The resolved ai-memory.exe is not a native Windows binary. Wrappers cannot enforce allowlist capture. No integrations were changed."
            }
        }
        finally {
            $stream.Dispose()
        }
    }

    $isAntigravity = $targetAgent -in @('antigravity', 'antigravity-ide', 'antigravity-cli')
    $mcpClient = if ($isAntigravity) { 'antigravity-cli' } else { $targetAgent }
    $instructionTarget = if ($targetAgent -eq 'claude-code') { 'CLAUDE.md' } else { 'AGENTS.md' }

    Write-Host "`nConfiguring ai-memory for $targetAgent. The upstream installer will merge its managed entries into this user's tool configuration." -ForegroundColor Cyan
    & ai-memory install-mcp --client $mcpClient --apply
    if ($LASTEXITCODE -ne 0) { throw "ai-memory install-mcp failed with exit code $LASTEXITCODE." }

    if ($targetAgent -in @('claude-code', 'codex', 'antigravity-cli')) {
        & ai-memory install-hooks --agent $targetAgent --capture-mode allowlist --apply
        if ($LASTEXITCODE -ne 0) { throw "ai-memory install-hooks failed with exit code $LASTEXITCODE." }
    } else {
        Write-Host 'MCP-only setup: this Antigravity surface does not have a first-party ai-memory lifecycle hook target.'
    }

    & ai-memory install-instructions --target (Join-Path $repoRoot $instructionTarget) --no-skills
    if ($LASTEXITCODE -ne 0) { throw "ai-memory install-instructions failed with exit code $LASTEXITCODE." }

    if ($targetAgent -in @('claude-code', 'codex', 'antigravity-cli')) {
        Write-Host 'Native executable and hook mode preflight passed. Confirm installer output reports capture-policy enforcement.'
    }
    Write-Host "Configured $targetAgent. No server, container, API key, or LLM provider was installed or started." -ForegroundColor Green
}
