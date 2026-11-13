<#
.SYNOPSIS
    Deterministic Phase 1 measurements for the optimize-claude-memory skill.

.DESCRIPTION
    Emits a compact report implementing the checks documented in
    references/verification.md:
      (a) true line counts of root CLAUDE.md / AGENTS.md (section 1 - counts match
          editor display; avoids the Get-Content trailing-newline / Measure-Object
          -Line undercount gotchas)
      (b) every CLAUDE.md / CLAUDE.local.md / .claude/CLAUDE.md in the repo and in
          its parent directories, each labelled ONE-LINER (`@AGENTS.md`, delete) or
          CONTENT (migrate, then delete), plus the triage verdict (section 2).
          Claude Code reads AGENTS.md itself only while none of these exist on the
          path, so the target is zero.
      (c) the Claude Code version (AGENTS.md support needs v2.1.277+) and the
          Project instructions setting from ~/.claude/settings.json
      (d) downward `@import` hits in root CLAUDE.md / AGENTS.md (any `@` path
          containing a slash)
      (e) broken `.md` references in the root instruction file (CLAUDE.md while it
          exists, else AGENTS.md)

    PowerShell 5.1 compatible. Pure ASCII on purpose (5.1 misreads UTF-8 without a
    BOM). Read-only - never modifies anything.

.PARAMETER Root
    Repository root to audit. Defaults to the current directory.

.EXAMPLE
    powershell -File audit-memory-tree.ps1 -Root C:\repos\my-app
#>
[CmdletBinding()]
param(
    [string]$Root = (Get-Location).Path
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\', '/')

# Get-Content drops a trailing newline (and -Raw keeps it), so split the raw text
# on "`n" and drop the single empty element a trailing newline produces. CRLF is
# fine: the "`r" stays attached to the previous line. This matches what an editor
# displays, unlike `Measure-Object -Line` (skips blank lines) or naive splits.
function Get-TrueLineCount {
    param([string]$Path)
    $raw = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
    if ($null -eq $raw -or $raw.Length -eq 0) { return 0 }
    $lines = $raw -split "`n"
    $count = $lines.Count
    if ($lines[$count - 1] -eq '') { $count = $count - 1 }
    return $count
}

# Walks the tree once with .NET enumeration (a cmdlet per directory takes minutes
# on a large monorepo), pruning dependency directories instead of descending into
# them. Also skips .claude/skills (skills have their own discovery),
# .claude/worktrees (full repo copies) and reparse points (junction cycles).
# Collects the instruction files, and the lower-cased name of every .md file so
# section (e) can resolve a bare reference like `some-plan.md`.
$pruneNames = @('node_modules', 'vendor', '.venv', 'target', '.git')
$instructionNames = @('agents.md', 'claude.md', 'claude.local.md')
$script:mdNames = New-Object 'System.Collections.Generic.HashSet[string]'
function Find-InstructionFiles {
    param([string]$Start)
    $found = New-Object System.Collections.ArrayList
    $stack = New-Object System.Collections.Stack
    $stack.Push((New-Object System.IO.DirectoryInfo $Start))
    while ($stack.Count -gt 0) {
        $d = $stack.Pop()
        try {
            foreach ($file in $d.EnumerateFiles('*.md')) {
                $lower = $file.Name.ToLowerInvariant()
                [void]$script:mdNames.Add($lower)
                if ($instructionNames -contains $lower) { [void]$found.Add($file.FullName) }
            }
            foreach ($sub in $d.EnumerateDirectories()) {
                if ($pruneNames -contains $sub.Name) { continue }
                if ($d.Name -eq '.claude' -and ($sub.Name -eq 'skills' -or $sub.Name -eq 'worktrees')) { continue }
                if ($sub.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                $stack.Push($sub)
            }
        } catch {
            Write-Verbose "skipped unreadable directory: $($d.FullName)"
        }
    }
    return ,$found
}

function Get-Relative {
    param([string]$Path)
    if ($Path.StartsWith($Root, [StringComparison]::OrdinalIgnoreCase)) {
        $rel = $Path.Substring($Root.Length).TrimStart('\', '/')
        if ($rel -eq '') { return '.' }
        return $rel
    }
    return $Path
}

Write-Output '=== optimize-claude-memory : memory-tree audit ==='
Write-Output "Root: $Root"
Write-Output ''

# ---------------------------------------------------------------------------
# (a) Root file line counts  (verification.md section 1)
# ---------------------------------------------------------------------------
Write-Output '--- (a) Root file line counts ---'
$rootCounts = @{}
foreach ($name in @('CLAUDE.md', 'AGENTS.md')) {
    $p = Join-Path $Root $name
    if (Test-Path -LiteralPath $p) {
        $n = Get-TrueLineCount -Path $p
        $rootCounts[$name] = $n
        $flag = ''
        if ($n -gt 200) { $flag = '   [OVER the 200-line budget]' }
        Write-Output ("  root {0}: {1} lines{2}" -f $name, $n, $flag)
    } else {
        Write-Output ("  root {0}: ABSENT" -f $name)
    }
}
Write-Output ''

# ---------------------------------------------------------------------------
# (b) CLAUDE.md-family files in the repo and above it  (verification.md section 2)
# ---------------------------------------------------------------------------
Write-Output '--- (b) CLAUDE.md-family files (target: none) ---'
$all = Find-InstructionFiles -Start $Root
$agentsFiles = @($all | Where-Object { (Split-Path -Leaf $_) -eq 'AGENTS.md' })
$claudeFiles = @($all | Where-Object { (Split-Path -Leaf $_) -ne 'AGENTS.md' })

$oneLiners = @()
$withContent = @()
foreach ($f in $claudeFiles) {
    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $f
    if ($null -eq $content) { $content = '' }
    if ($content.Trim() -eq '@AGENTS.md') {
        $oneLiners += $f
    } else {
        $withContent += $f
    }
}

# Parent directories: any CLAUDE.md / CLAUDE.local.md / .claude/CLAUDE.md above the
# repo also switches native AGENTS.md reading off. ~/.claude/CLAUDE.md doesn't count.
$userClaude = Join-Path $HOME '.claude\CLAUDE.md'
$parentHits = @()
$dir = Split-Path -Parent $Root
while (-not [string]::IsNullOrEmpty($dir)) {
    foreach ($rel in @('CLAUDE.md', 'CLAUDE.local.md', '.claude\CLAUDE.md')) {
        $p = Join-Path $dir $rel
        if ((Test-Path -LiteralPath $p -PathType Leaf) -and ($p -ne $userClaude)) { $parentHits += $p }
    }
    $up = Split-Path -Parent $dir
    if ($up -eq $dir) { break }
    $dir = $up
}

Write-Output ("  AGENTS.md files (outside exclusions): {0}" -f $agentsFiles.Count)
Write-Output ("  CLAUDE.md-family files in the repo: {0}  ({1} one-line @AGENTS.md, {2} with content)" -f $claudeFiles.Count, $oneLiners.Count, $withContent.Count)
foreach ($f in $oneLiners) { Write-Output ("    ONE-LINER (delete)               : {0}" -f (Get-Relative $f)) }
foreach ($f in $withContent) {
    Write-Output ("    CONTENT, {0} lines (migrate, then delete) : {1}" -f (Get-TrueLineCount -Path $f), (Get-Relative $f))
}
if ($parentHits.Count -gt 0) {
    Write-Output '  In parent directories (outside this repo; Claude reads CLAUDE.md only while these exist):'
    foreach ($p in $parentHits) { Write-Output "    PARENT : $p" }
} else {
    Write-Output '  In parent directories: none'
}

# Mixed state: AGENTS.md files with no @AGENTS.md sibling while other CLAUDE.md files remain.
$noSibling = @()
foreach ($a in $agentsFiles) {
    $sib = Join-Path (Split-Path -Parent $a) 'CLAUDE.md'
    if (-not (Test-Path -LiteralPath $sib -PathType Leaf)) { $noSibling += $a }
}

$rootAgentsOver = $rootCounts.ContainsKey('AGENTS.md') -and $rootCounts['AGENTS.md'] -gt 200
if ($agentsFiles.Count -eq 0 -and $withContent.Count -eq 0 -and $oneLiners.Count -eq 0) {
    Write-Output '  VERDICT: GREENFIELD - no instruction files in the repo; write a root AGENTS.md directly (not /init, which writes a CLAUDE.md).'
} elseif ($agentsFiles.Count -eq 0) {
    Write-Output '  VERDICT: MIGRATION - no AGENTS.md tree yet; build it and retire the CLAUDE.md files.'
} elseif ($withContent.Count -gt 0) {
    Write-Output ("  VERDICT: MIGRATION - {0} CLAUDE.md file(s) hold content to move into AGENTS.md (or .claude/rules/) before deleting." -f $withContent.Count)
} elseif ($oneLiners.Count -gt 0) {
    Write-Output ("  VERDICT: TOUCH-UP (legacy sibling pattern) - delete all {0} one-liners in one step, root included." -f $oneLiners.Count)
    if ($noSibling.Count -gt 0) {
        Write-Output ("    Mixed state: {0} AGENTS.md file(s) have no sibling, so Claude never reads them while any CLAUDE.md stays:" -f $noSibling.Count)
        foreach ($a in $noSibling) { Write-Output ("      {0}" -f (Get-Relative $a)) }
    }
} elseif ($rootAgentsOver) {
    Write-Output '  VERDICT: ON THE PATTERN, but root AGENTS.md is over budget - full audit of its content.'
} else {
    Write-Output '  VERDICT: ON THE PATTERN - touch-up plan only.'
}
if ($parentHits.Count -gt 0) {
    Write-Output '  BLOCKER: a parent-directory file above keeps Claude off AGENTS.md for this whole repo; the plan must name it.'
}
Write-Output ''

# ---------------------------------------------------------------------------
# (c) Claude Code version and the Project instructions setting
# ---------------------------------------------------------------------------
Write-Output '--- (c) Claude Code AGENTS.md support ---'
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if ($null -eq $claudeCmd) {
    Write-Output '  claude: not on PATH - check the version by hand (needs v2.1.277+).'
} else {
    $verText = ''
    try { $verText = (& claude --version 2>$null | Select-Object -First 1) } catch { $verText = '' }
    $m = [regex]::Match([string]$verText, '(\d+)\.(\d+)\.(\d+)')
    if ($m.Success) {
        $ver = New-Object System.Version ([int]$m.Groups[1].Value), ([int]$m.Groups[2].Value), ([int]$m.Groups[3].Value)
        $ok = ''
        if ($ver -lt (New-Object System.Version 2, 1, 277)) { $ok = '   [TOO OLD: reads CLAUDE.md only - update Claude Code]' }
        Write-Output ("  claude --version: {0}{1}" -f $ver, $ok)
    } else {
        Write-Output "  claude --version: could not parse '$verText'"
    }
}
$settingsPath = Join-Path $HOME '.claude\settings.json'
$instr = $null
if (Test-Path -LiteralPath $settingsPath) {
    try {
        $settings = Get-Content -Raw -Encoding UTF8 -LiteralPath $settingsPath | ConvertFrom-Json
        if ($settings.pluginConfigs) {
            foreach ($id in @('cc-plugin-agents-md@builtin', 'agents-md@builtin')) {
                $entry = $settings.pluginConfigs.$id
                if ($entry -and $entry.options -and $entry.options.instructionFiles) { $instr = $entry.options.instructionFiles; break }
            }
        }
    } catch {
        Write-Output '  ~/.claude/settings.json: could not parse (JSON with comments?) - check /config by hand.'
    }
}
if ($null -eq $instr) {
    Write-Output '  Project instructions: not set in ~/.claude/settings.json (default claude-md-or-agents-md)'
} else {
    $warn = ''
    if ($instr -eq 'claude-md' -or $instr -eq 'managed-only') { $warn = '   [AGENTS.md is NOT read with this value]' }
    Write-Output ("  Project instructions: {0}{1}" -f $instr, $warn)
}
Write-Output '  (Only this machine. Ask whether anyone on the team runs an older Claude Code.)'
Write-Output ''

# ---------------------------------------------------------------------------
# (d) Downward @import hits in root files  (verification.md Phase-5 check 3)
# ---------------------------------------------------------------------------
Write-Output '--- (d) Downward @import hits in root CLAUDE.md / AGENTS.md ---'
# Any `@` path containing a slash (e.g. @services/x/AGENTS.md) is a downward
# import; only same-directory imports are valid. Claude Code doesn't evaluate
# imports inside code spans or fenced blocks, so those are stripped first (an npm
# scope such as `pnpm --filter @repo/ui` is not an import).
$downHits = 0
foreach ($name in @('CLAUDE.md', 'AGENTS.md')) {
    $p = Join-Path $Root $name
    if (-not (Test-Path -LiteralPath $p)) { continue }
    $lineNo = 0
    $inFence = $false
    foreach ($line in (Get-Content -Encoding UTF8 -LiteralPath $p)) {
        $lineNo++
        if ($line -match '^\s*(```|~~~)') { $inFence = -not $inFence; continue }
        if ($inFence) { continue }
        $plain = [regex]::Replace($line, '`[^`]*`', '')
        if ($plain -match '(^|\s)@[\w.-]+[\\/][\w.\\/-]+') {
            $downHits++
            Write-Output ("  {0}:{1}: {2}" -f $name, $lineNo, $line.Trim())
        }
    }
}
if ($downHits -eq 0) {
    Write-Output '  None found (good - only same-directory @imports, or none at all).'
}
Write-Output ''

# ---------------------------------------------------------------------------
# (e) Broken .md references in the root instruction file  (verification.md section 4)
# ---------------------------------------------------------------------------
$refName = 'AGENTS.md'
if (Test-Path -LiteralPath (Join-Path $Root 'CLAUDE.md')) { $refName = 'CLAUDE.md' }
Write-Output ("--- (e) Broken .md references in root {0} ---" -f $refName)
$refPath = Join-Path $Root $refName
if (-not (Test-Path -LiteralPath $refPath)) {
    Write-Output ("  root {0} ABSENT - nothing to check." -f $refName)
} else {
    $seen = @{}
    $display = @{}
    $lineNo = 0
    foreach ($line in (Get-Content -Encoding UTF8 -LiteralPath $refPath)) {
        $lineNo++
        foreach ($m in ([regex]::Matches($line, '[\w@][\w./\\-]*\.md\b'))) {
            $ref = $m.Value
            if ($ref -match '://') { continue }              # URL, not a path
            $candidate = $ref -replace '^@', ''               # @import syntax
            if ([System.IO.Path]::IsPathRooted($candidate)) { continue }  # absolute - out of scope
            $leafName = (Split-Path -Leaf $candidate).ToLowerInvariant()
            # Mentions of CLAUDE.md / CLAUDE.local.md are prose about the rule; on the
            # target pattern those files are absent on purpose.
            if ($leafName -eq 'claude.md' -or $leafName -eq 'claude.local.md') { continue }
            if ($candidate -notmatch '[\\/]') {
                # A bare name (`some-plan.md`) resolves if a file of that name exists anywhere.
                if ($script:mdNames.Contains($leafName)) { continue }
            } elseif (Test-Path -LiteralPath (Join-Path $Root ($candidate -replace '/', '\'))) {
                continue
            }
            $key = $candidate.ToLowerInvariant()
            if (-not $seen.ContainsKey($key)) { $seen[$key] = @(); $display[$key] = $candidate }
            $seen[$key] += $lineNo
        }
    }
    if ($seen.Keys.Count -eq 0) {
        Write-Output ("  None - every relative .md reference in root {0} resolves." -f $refName)
    } else {
        Write-Output '  (Paths resolve from the repo root, bare names anywhere in it; a path into another repo shows here too - judge each.)'
        foreach ($key in ($seen.Keys | Sort-Object)) {
            Write-Output ("  BROKEN: {0}  (line(s) {1})" -f $display[$key], (($seen[$key] | Select-Object -Unique) -join ', '))
        }
    }
}
Write-Output ''
Write-Output '=== audit complete (read-only; nothing was modified) ==='
