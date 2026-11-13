<#
.SYNOPSIS
  Inventory + red-flag scan for Claude Code skills. Part of the skill-optimizer skill.
.DESCRIPTION
  Walks a skills root (default: ~/.claude/skills) and, for each folder containing a
  SKILL.md, emits: listing length (description + when_to_use, chars and ~tokens at
  chars/4), body lines and ~tokens, bundled file count, a gotchas heuristic, the
  progressive-disclosure pointer count, and threshold flags. Then file-level findings:
  orphans, dangling pointers, paths that point outside the skill, frontmatter that
  only Claude Code accepts. Deterministic measurement belongs in a script, not in
  model output (rubric criterion H).

  Read-only. Windows PowerShell 5.1-compatible.
.PARAMETER Root
  Skills directory to scan. Run once per scope (user + repo) and compare.
.PARAMETER CompareRoot
  A second skills directory holding copies of the same skills (a source repo against
  ~/.claude/skills, or the reverse). Adds a drift report: which skills exist on one
  side only, and which files differ. Line endings are ignored. "Modified later" is the
  file timestamp, which a git checkout resets: read the diff before trusting it.
.PARAMETER Json
  Emit JSON instead of the markdown report.
.EXAMPLE
  .\audit-skills.ps1
  .\audit-skills.ps1 -Root "C:\repo\.claude\skills" -Json
  .\audit-skills.ps1 -Root "C:\src\SKILLS" -CompareRoot "$env:USERPROFILE\.claude\skills"
#>
param(
  [string]$Root = (Join-Path $env:USERPROFILE '.claude\skills'),
  [string]$CompareRoot = '',
  [switch]$Json
)

if (-not (Test-Path $Root)) {
  Write-Output "Skills root not found: $Root"
  exit 1
}
if ($CompareRoot -and -not (Test-Path $CompareRoot)) {
  Write-Output "Compare root not found: $CompareRoot"
  exit 1
}

# Frontmatter keys every distribution path accepts (Agent Skills spec). Anything else
# loads in Claude Code but is a hard error on a claude.ai upload or the Skills API.
$portableKeys = @('name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools')
# Files written for people or tooling, not for the model. Not orphans.
$humanFacing = '^(README|LICENSE|LICENCE|CHANGELOG|NOTICE)(\.[A-Za-z0-9]+)?$'
$skipPath    = '\\(evals|__pycache__|node_modules|\.git)\\'
$pointerRx   = '(?i)(?<![\w/\\.-])(references|scripts|assets|prompts|templates|config|examples)/[\w][\w.\-/]*'
$gotchaRx    = '(?im)gotcha|pitfall|edge case|anti-pattern|mistakes?|known issue|failure mode|troubleshoot|red flag|never do|^#+\s*(never|don''t|rules|working rules)\b'

function Get-SkillDirs([string]$Path) {
  Get-ChildItem -Path $Path -Directory |
    Where-Object { ($_.Name -notlike '*-workspace') -and (Test-Path (Join-Path $_.FullName 'SKILL.md')) }
}

function Get-FrontmatterValue([string]$Frontmatter, [string]$Key) {
  $m = [regex]::Match($Frontmatter, "(?s)(?:^|\n)$([regex]::Escape($Key)):[ \t]*(.*?)(?=\n[A-Za-z_-]+\s*:|\z)")
  if (-not $m.Success) { return $null }
  $rawValue = $m.Groups[1].Value.Trim()
  $style = 'plain'
  if ($rawValue -match '^[>|][+-]?\s*(\n|$)') {
    $style = 'block'
    $rawValue = $rawValue -replace '^[>|][+-]?\s*', ''
  } elseif ($rawValue.Length -ge 2 -and $rawValue[0] -eq '"' -and $rawValue[$rawValue.Length - 1] -eq '"') {
    $style = 'quoted'
    $rawValue = $rawValue.Substring(1, $rawValue.Length - 2) -replace '\\"', '"'
  } elseif ($rawValue.Length -ge 2 -and $rawValue[0] -eq "'" -and $rawValue[$rawValue.Length - 1] -eq "'") {
    $style = 'quoted'
    $rawValue = $rawValue.Substring(1, $rawValue.Length - 2) -replace "''", "'"
  }
  return [pscustomobject]@{ Text = ($rawValue -replace '\s+', ' ').Trim(); Style = $style }
}

$results = @()
foreach ($dir in (Get-SkillDirs $Root)) {
  $skillFile = Join-Path $dir.FullName 'SKILL.md'
  $raw = Get-Content $skillFile -Raw -Encoding UTF8
  $totalLines = ($raw -split "`n").Count

  # --- frontmatter ---
  $desc = ''; $descStyle = ''; $whenToUse = ''; $nameField = ''; $fmLines = 0; $fmKeys = @()
  $fm = [regex]::Match($raw, '(?s)\A---\s*\n(.*?)\n---')
  if ($fm.Success) {
    $fmText = $fm.Groups[1].Value
    $fmLines = ($fm.Value -split "`n").Count
    $fmKeys = @([regex]::Matches($fmText, '(?m)^([A-Za-z_-]+)\s*:') | ForEach-Object { $_.Groups[1].Value })
    $d = Get-FrontmatterValue $fmText 'description'
    if ($d) { $desc = $d.Text; $descStyle = $d.Style }
    $w = Get-FrontmatterValue $fmText 'when_to_use'
    if ($w) { $whenToUse = $w.Text }
    $n = Get-FrontmatterValue $fmText 'name'
    if ($n) { $nameField = $n.Text }
  }
  $body = if ($fm.Success) { $raw.Substring($fm.Length) } else { $raw }
  $listingChars = $desc.Length + $whenToUse.Length
  $listingTokens = [math]::Round($listingChars / 4)
  $bodyLines = $totalLines - $fmLines
  $bodyTokens = [math]::Round($body.Length / 4)

  # --- bundled files (everything except SKILL.md; evals/ are skill-creator artifacts) ---
  $bundled = @(Get-ChildItem -Path $dir.FullName -Recurse -File |
    Where-Object { ($_.Name -ne 'SKILL.md') -and ($_.FullName -notmatch $skipPath) -and ($_.Extension -ne '.pyc') })
  $contentFiles = @($bundled | Where-Object { $_.Name -notmatch $humanFacing })
  $mdText = @{}
  foreach ($f in ($bundled | Where-Object { $_.Extension -eq '.md' })) {
    $mdText[$f.FullName] = Get-Content $f.FullName -Raw -Encoding UTF8
  }

  # --- gotchas: SKILL.md or any bundled markdown (step files often hold them) ---
  $hasGotchas = [regex]::IsMatch($raw, $gotchaRx)
  $gotchasIn = if ($hasGotchas) { 'SKILL.md' } else { '' }
  if (-not $hasGotchas) {
    foreach ($k in $mdText.Keys) {
      if ($mdText[$k] -and [regex]::IsMatch($mdText[$k], $gotchaRx)) { $hasGotchas = $true; $gotchasIn = 'bundled'; break }
    }
  }
  $pointerCount = ([regex]::Matches($raw, $pointerRx)).Count

  # --- orphans: a content file SKILL.md never names, and no file SKILL.md names does either ---
  function Test-Mentioned([string]$Text, $File, [string]$Rel) {
    if (-not $Text) { return $false }
    return (($Text.IndexOf($Rel, [StringComparison]::OrdinalIgnoreCase) -ge 0) -or
            ($Text.IndexOf($File.Name, [StringComparison]::OrdinalIgnoreCase) -ge 0))
  }
  $direct = @{}
  foreach ($f in $contentFiles) {
    $rel = $f.FullName.Substring($dir.FullName.Length + 1) -replace '\\', '/'
    $direct[$f.FullName] = (Test-Mentioned $raw $f $rel)
  }
  $orphans = @()
  foreach ($f in $contentFiles) {
    if ($direct[$f.FullName]) { continue }
    $rel = $f.FullName.Substring($dir.FullName.Length + 1) -replace '\\', '/'
    $viaReferenced = $false
    foreach ($k in $mdText.Keys) {
      if ($k -eq $f.FullName) { continue }
      if ($direct.ContainsKey($k) -and $direct[$k] -and (Test-Mentioned $mdText[$k] $f $rel)) { $viaReferenced = $true; break }
    }
    if (-not $viaReferenced) { $orphans += $rel }
  }

  # --- dangling: SKILL.md points at a path that does not exist ---
  $dangling = @(); $external = @()
  $ptrValues = @([regex]::Matches($raw, $pointerRx) | ForEach-Object { $_.Value.TrimEnd('.', ',', ')') } | Sort-Object -Unique)
  foreach ($p in $ptrValues) {
    if ($p -match '[\*\?]') { continue }  # glob pattern, not a literal path
    if (Test-Path (Join-Path $dir.FullName ($p -replace '/', '\'))) { continue }
    $top = ($p -split '/')[0]
    # No such top folder in the skill at all: the path most likely names a file in a
    # project the skill works on. Report it apart so the read can decide.
    if (Test-Path (Join-Path $dir.FullName $top)) { $dangling += $p } else { $external += $p }
  }
  # markdown links to relative files, including ../sibling-skill/FILE.md
  $linkValues = @([regex]::Matches($raw, '\]\(([^)\s#]+)(#[^)\s]*)?\)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
  foreach ($l in $linkValues) {
    if ($l -match '^(https?:|mailto:|/|<|\{|\$)' -or $l -match '[\*\?<>{}]') { continue }
    if (-not (Test-Path (Join-Path $dir.FullName ($l -replace '/', '\')))) {
      if ($dangling -notcontains $l) { $dangling += $l }
    }
  }

  # --- threshold flags ---
  $flags = @()
  if (-not $fm.Success) { $flags += 'NO-FRONTMATTER' }
  elseif (-not $desc) { $flags += 'NO-DESC' }
  if ($nameField -and ($nameField -ne $dir.Name)) { $flags += 'NAME!=DIR' }
  # A plain one-line scalar holding ": " or " #" is not valid YAML. Claude Code reads it
  # anyway; PyYAML (package_skill.py, uploads, other agents) rejects the whole file.
  if ($descStyle -eq 'plain' -and ($desc -match ':\s' -or $desc -match '\s#')) { $flags += 'YAML-RISK' }
  if ($listingChars -gt 1536) { $flags += 'DESC>1536c' }
  elseif ($listingChars -gt 400) { $flags += 'DESC>400c' }
  if ($bodyLines -gt 400) { $flags += 'BODY>400L' }
  if ($bodyTokens -gt 5000) { $flags += 'BODY>5kTOK' }
  if (-not $hasGotchas) { $flags += 'NO-GOTCHAS' }
  if ($orphans.Count -gt 0) { $flags += "ORPHANS:$($orphans.Count)" }
  if ($dangling.Count -gt 0) { $flags += "DANGLING:$($dangling.Count)" }
  if ($external.Count -gt 0) { $flags += "EXTERNAL?:$($external.Count)" }

  $results += [pscustomobject]@{
    Skill         = $dir.Name
    DescChars     = $listingChars
    DescTokens    = $listingTokens
    BodyLines     = $bodyLines
    BodyTokens    = $bodyTokens
    BundledFiles  = $bundled.Count
    HasGotchas    = $hasGotchas
    GotchasIn     = $gotchasIn
    Pointers      = $pointerCount
    Flags         = ($flags -join ', ')
    OrphanList    = ($orphans -join '; ')
    DanglingList  = ($dangling -join '; ')
    ExternalList  = ($external -join '; ')
    ClaudeOnlyKeys = (@($fmKeys | Where-Object { $portableKeys -notcontains $_ }) -join ', ')
  }
}

# --- drift between two copies of the same skills ---
function Get-NormalizedHash([string]$Path) {
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  # drop CR so a CRLF checkout equals an LF one; harmless for the rare binary file
  $clean = New-Object System.Collections.Generic.List[byte]
  foreach ($b in $bytes) { if ($b -ne 13) { $clean.Add($b) } }
  $sha = [System.Security.Cryptography.SHA1]::Create()
  try { return [BitConverter]::ToString($sha.ComputeHash($clean.ToArray())) } finally { $sha.Dispose() }
}
function Get-SkillFileMap([string]$SkillDir) {
  $map = @{}
  Get-ChildItem -Path $SkillDir -Recurse -File |
    Where-Object { ($_.FullName -notmatch '\\(__pycache__|node_modules|\.git)\\') -and ($_.Extension -ne '.pyc') } |
    ForEach-Object { $map[($_.FullName.Substring($SkillDir.Length + 1) -replace '\\', '/')] = $_.FullName }
  return $map
}
$drift = @()
if ($CompareRoot) {
  $left = @{};  foreach ($d in (Get-SkillDirs $Root))        { $left[$d.Name]  = $d.FullName }
  $right = @{}; foreach ($d in (Get-SkillDirs $CompareRoot)) { $right[$d.Name] = $d.FullName }
  foreach ($name in (@($left.Keys) + @($right.Keys) | Sort-Object -Unique)) {
    if (-not $right.ContainsKey($name)) { $drift += [pscustomobject]@{ Skill = $name; State = 'only in Root'; Files = '' }; continue }
    if (-not $left.ContainsKey($name))  { $drift += [pscustomobject]@{ Skill = $name; State = 'only in CompareRoot'; Files = '' }; continue }
    $a = Get-SkillFileMap $left[$name]; $b = Get-SkillFileMap $right[$name]
    $diffs = @()
    foreach ($rel in (@($a.Keys) + @($b.Keys) | Sort-Object -Unique)) {
      if (-not $b.ContainsKey($rel)) { $diffs += "$rel (Root only)" }
      elseif (-not $a.ContainsKey($rel)) { $diffs += "$rel (CompareRoot only)" }
      elseif ((Get-NormalizedHash $a[$rel]) -ne (Get-NormalizedHash $b[$rel])) {
        $newer = if ((Get-Item $a[$rel]).LastWriteTime -gt (Get-Item $b[$rel]).LastWriteTime) { 'Root modified later' } else { 'CompareRoot modified later' }
        $diffs += "$rel ($newer)"
      }
    }
    $state = if ($diffs.Count -eq 0) { 'same' } else { 'differs' }
    $drift += [pscustomobject]@{ Skill = $name; State = $state; Files = ($diffs -join '; ') }
  }
}

if ($Json) {
  if ($CompareRoot) { [pscustomobject]@{ Skills = $results; Drift = $drift } | ConvertTo-Json -Depth 4 }
  else { $results | ConvertTo-Json }
  exit 0
}

Write-Output ("Skills root: {0}  ({1} skills)" -f $Root, $results.Count)
Write-Output ''
Write-Output '| Skill | Desc chars | ~Tokens | Body lines | ~Body tok | Bundled | Gotchas | Pointers | Flags |'
Write-Output '|---|---|---|---|---|---|---|---|---|'
foreach ($r in ($results | Sort-Object DescChars -Descending)) {
  $g = if ($r.HasGotchas) { $r.GotchasIn } else { 'none' }
  Write-Output ('| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |' -f $r.Skill, $r.DescChars, $r.DescTokens, $r.BodyLines, $r.BodyTokens, $r.BundledFiles, $g, $r.Pointers, $r.Flags)
}
$totalChars = ($results | Measure-Object -Property DescChars -Sum).Sum
$totalTokens = ($results | Measure-Object -Property DescTokens -Sum).Sum
Write-Output ''
Write-Output ("Listing cost: {0} chars (~{1} tokens) in every session, this root only." -f $totalChars, $totalTokens)
Write-Output 'Budget: the listing gets 1% of the context window, roughly 8,000 chars on a 200K window and'
Write-Output '40,000 on a 1M window (4 chars/token estimate). Over budget, Claude Code drops whole'
Write-Output 'descriptions, least-invoked skills first. Other roots, plugins and synced skills share it;'
Write-Output '/doctor reports the real figure.'
if (Test-Path (Join-Path $Root 'synced')) {
  Write-Output 'Note: synced/ holds skills downloaded from claude.ai. Not scanned; edit those on claude.ai.'
}

$problems = $results | Where-Object { $_.OrphanList -or $_.DanglingList -or $_.ExternalList }
if ($problems) {
  Write-Output ''
  Write-Output 'File-level findings:'
  foreach ($r in $problems) {
    if ($r.OrphanList)   { Write-Output ("  {0} - orphans (nothing points to them): {1}" -f $r.Skill, $r.OrphanList) }
    if ($r.DanglingList) { Write-Output ("  {0} - dangling pointers (path missing): {1}" -f $r.Skill, $r.DanglingList) }
    if ($r.ExternalList) { Write-Output ("  {0} - paths outside the skill (a project file, or a missing folder): {1}" -f $r.Skill, $r.ExternalList) }
  }
}

$claudeOnly = $results | Where-Object { $_.ClaudeOnlyKeys }
if ($claudeOnly) {
  Write-Output ''
  Write-Output 'Claude Code-only frontmatter (a claude.ai upload or the Skills API rejects these keys):'
  foreach ($r in $claudeOnly) { Write-Output ("  {0}: {1}" -f $r.Skill, $r.ClaudeOnlyKeys) }
}

if ($CompareRoot) {
  Write-Output ''
  Write-Output ("Drift against {0}:" -f $CompareRoot)
  $changed = @($drift | Where-Object { $_.State -ne 'same' })
  if ($changed.Count -eq 0) { Write-Output '  none - every shared skill is identical' }
  foreach ($d in $changed) {
    if ($d.Files) { Write-Output ("  {0} - {1}: {2}" -f $d.Skill, $d.State, $d.Files) }
    else { Write-Output ("  {0} - {1}" -f $d.Skill, $d.State) }
  }
  Write-Output ("  ({0} identical)" -f (@($drift | Where-Object { $_.State -eq 'same' }).Count))
}
