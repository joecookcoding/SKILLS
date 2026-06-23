<#
.SYNOPSIS
    Deterministic Phase 1 measurements for the optimize-claude-memory skill.

.DESCRIPTION
    Emits a compact report implementing the checks documented in
    references/verification.md:
      (a) true line counts of root CLAUDE.md / AGENTS.md (section 1 — counts match
          editor display; avoids the Get-Content trailing-newline / Measure-Object
          -Line undercount gotchas)
      (b) fast-path verdict: % of AGENTS.md files with the sibling pattern (a
          CLAUDE.md next to them containing only `@AGENTS.md`) + missing-siblings
          list (section 2)
      (c) downward `@import` hits in root CLAUDE.md / AGENTS.md (section 3 of the
          Phase 5 short list — any `@` path containing a slash)
      (d) broken `.md` references in root CLAUDE.md (section 4 — referenced
          relative .md paths that don't exist)

    PowerShell 5.1 compatible. Read-only — never modifies anything.

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
$Root = (Resolve-Path -LiteralPath $Root).Path

# Get-Content drops a trailing newline (and -Raw keeps it), so split the raw text
# on "`n" and drop the single empty element a trailing newline produces. CRLF is
# fine: the "`r" stays attached to the previous line. This matches what an editor
# displays, unlike `Measure-Object -Line` (skips blank lines) or naive splits.
function Get-TrueLineCount {
    param([string]$Path)
    $raw = Get-Content -Raw -LiteralPath $Path
    if ($null -eq $raw -or $raw.Length -eq 0) { return 0 }
    $lines = $raw -split "`n"
    $count = $lines.Count
    if ($lines[$count - 1] -eq '') { $count = $count - 1 }
    return $count
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
# (b) Sibling-pattern coverage / fast-path verdict  (verification.md section 2)
# ---------------------------------------------------------------------------
Write-Output '--- (b) Sibling-pattern coverage (fast-path verdict) ---'
# Standard exclusions per verification.md: node_modules, .claude/skills, vendor,
# .venv, target (and .git for safety).
$excludeRe = '[\\/](node_modules|vendor|\.venv|target|\.git)[\\/]|[\\/]\.claude[\\/]skills[\\/]'
$agentsFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -Filter 'AGENTS.md' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch $excludeRe })

if ($agentsFiles.Count -eq 0) {
    Write-Output '  No AGENTS.md files found (outside exclusions). Sibling pattern not in use.'
    $siblingPct = $null
} else {
    $okCount = 0
    $problems = @()
    foreach ($f in $agentsFiles) {
        $sibling = Join-Path $f.Directory.FullName 'CLAUDE.md'
        if (-not (Test-Path -LiteralPath $sibling)) {
            $problems += "MISSING sibling CLAUDE.md : $($f.FullName)"
        } else {
            $content = Get-Content -Raw -LiteralPath $sibling
            if ($null -eq $content) { $content = '' }
            if ($content.Trim() -eq '@AGENTS.md') {
                $okCount++
            } else {
                $problems += "sibling CLAUDE.md is NOT the `@AGENTS.md` one-liner : $sibling"
            }
        }
    }
    $siblingPct = [math]::Round(100 * $okCount / $agentsFiles.Count, 1)
    Write-Output ("  AGENTS.md files (outside exclusions): {0}" -f $agentsFiles.Count)
    Write-Output ("  With conforming sibling (CLAUDE.md == '@AGENTS.md'): {0}  ({1}%)" -f $okCount, $siblingPct)
    if ($problems.Count -gt 0) {
        Write-Output '  Gaps:'
        foreach ($m in $problems) { Write-Output "    $m" }
    }
}

# Fast-path rule (SKILL.md Phase 1): >=90% sibling coverage AND root file under ~200 lines.
$rootUnderBudget = $false
if ($rootCounts.ContainsKey('CLAUDE.md') -and $rootCounts['CLAUDE.md'] -le 200) { $rootUnderBudget = $true }
elseif ((-not $rootCounts.ContainsKey('CLAUDE.md')) -and $rootCounts.ContainsKey('AGENTS.md') -and $rootCounts['AGENTS.md'] -le 200) { $rootUnderBudget = $true }

if ($null -eq $siblingPct) {
    Write-Output '  VERDICT: no sibling pattern detected -> FULL AUDIT (likely a migration).'
} elseif ($siblingPct -ge 90 -and $rootUnderBudget) {
    Write-Output '  VERDICT: FAST PATH — repo is already on the pattern; produce a touch-up plan only.'
} else {
    Write-Output '  VERDICT: FULL AUDIT — sibling coverage < 90% and/or root file over ~200 lines.'
}
Write-Output ''

# ---------------------------------------------------------------------------
# (c) Downward @import hits in root files  (verification.md Phase-5 check 3)
# ---------------------------------------------------------------------------
Write-Output '--- (c) Downward @import hits in root CLAUDE.md / AGENTS.md ---'
# Any `@` path containing a slash (e.g. @services/x/AGENTS.md) is a downward
# import; only same-directory `@AGENTS.md` / `@README.md` are valid.
$downHits = 0
foreach ($name in @('CLAUDE.md', 'AGENTS.md')) {
    $p = Join-Path $Root $name
    if (-not (Test-Path -LiteralPath $p)) { continue }
    $lineNo = 0
    foreach ($line in (Get-Content -LiteralPath $p)) {
        $lineNo++
        if ($line -match '(^|\s)@[\w.-]+[\\/][\w.\\/-]+') {
            $downHits++
            Write-Output ("  {0}:{1}: {2}" -f $name, $lineNo, $line.Trim())
        }
    }
}
if ($downHits -eq 0) {
    Write-Output '  None found (good — only same-directory @imports, or none at all).'
}
Write-Output ''

# ---------------------------------------------------------------------------
# (d) Broken .md references in root CLAUDE.md  (verification.md section 4)
# ---------------------------------------------------------------------------
Write-Output '--- (d) Broken .md references in root CLAUDE.md ---'
$claudePath = Join-Path $Root 'CLAUDE.md'
if (-not (Test-Path -LiteralPath $claudePath)) {
    Write-Output '  root CLAUDE.md ABSENT — nothing to check.'
} else {
    $broken = 0
    $seen = @{}
    $lineNo = 0
    foreach ($line in (Get-Content -LiteralPath $claudePath)) {
        $lineNo++
        foreach ($m in ([regex]::Matches($line, '[\w@][\w./\\-]*\.md\b'))) {
            $ref = $m.Value
            if ($ref -match '://') { continue }              # URL, not a path
            $candidate = $ref -replace '^@', ''               # @import syntax
            if ([System.IO.Path]::IsPathRooted($candidate)) { continue }  # absolute — out of scope
            $full = Join-Path $Root ($candidate -replace '/', '\')
            if (-not (Test-Path -LiteralPath $full)) {
                $key = $candidate.ToLower()
                if (-not $seen.ContainsKey($key)) { $seen[$key] = @() }
                $seen[$key] += $lineNo
                $broken++
            }
        }
    }
    if ($seen.Keys.Count -eq 0) {
        Write-Output '  None — every relative .md reference in root CLAUDE.md resolves.'
    } else {
        foreach ($key in ($seen.Keys | Sort-Object)) {
            Write-Output ("  BROKEN: {0}  (line(s) {1})" -f $key, (($seen[$key] | Select-Object -Unique) -join ', '))
        }
    }
}
Write-Output ''
Write-Output '=== audit complete (read-only; nothing was modified) ==='
