[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [ValidateSet('claude-code', 'codex', 'antigravity', 'antigravity-ide', 'antigravity-cli')]
    [string]$Agent
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$markerPath = Join-Path $repoRoot '.ai-memory.toml'

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

# Version this repository was validated against. Bump deliberately after
# re-verifying the install flags against the new release's docs.
$aiMemoryPinnedVersion = '2.6.0'
$verOutput = ((& ai-memory --version 2>$null) | Out-String)
if ($verOutput -notmatch "(^|[^0-9.])$([regex]::Escape($aiMemoryPinnedVersion))([^0-9.]|$)") {
    Write-Warning "ai-memory version mismatch: this repo pins $aiMemoryPinnedVersion (got: $($verOutput.Trim())). Set `$env:AI_MEMORY_ALLOW_OTHER_VERSION='1' to override."
    if ($env:AI_MEMORY_ALLOW_OTHER_VERSION -ne '1') {
        throw "ai-memory version mismatch: expected $aiMemoryPinnedVersion."
    }
}

if ($Agent -in @('claude-code', 'codex', 'antigravity-cli')) {
    # Allowlist is enforced inside the native hook binary. Reject wrappers and
    # compatibility script modes before any user-level tool configuration changes.
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

$isAntigravity = $Agent -in @('antigravity', 'antigravity-ide', 'antigravity-cli')
$mcpClient = if ($isAntigravity) { 'antigravity-cli' } else { $Agent }
$instructionTarget = if ($Agent -eq 'claude-code') { 'CLAUDE.md' } else { 'AGENTS.md' }

Write-Host "Configuring ai-memory for $Agent. The upstream installer will merge its managed entries into this user's tool configuration."
& ai-memory install-mcp --client $mcpClient --apply
if ($LASTEXITCODE -ne 0) { throw "ai-memory install-mcp failed with exit code $LASTEXITCODE." }

if ($Agent -in @('claude-code', 'codex', 'antigravity-cli')) {
    & ai-memory install-hooks --agent $Agent --capture-mode allowlist --apply
    if ($LASTEXITCODE -ne 0) { throw "ai-memory install-hooks failed with exit code $LASTEXITCODE." }
} else {
    Write-Host 'MCP-only setup: this Antigravity surface does not have a first-party ai-memory lifecycle hook target.'
}

& ai-memory install-instructions --target (Join-Path $repoRoot $instructionTarget)
if ($LASTEXITCODE -ne 0) { throw "ai-memory install-instructions failed with exit code $LASTEXITCODE." }

if ($Agent -in @('claude-code', 'codex', 'antigravity-cli')) {
    Write-Host 'Native executable and hook mode preflight passed. Confirm installer output reports capture-policy enforcement.'
}
Write-Host "Configured $Agent. No server, container, API key, or LLM provider was installed or started."
