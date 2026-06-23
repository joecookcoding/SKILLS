<#
.SYNOPSIS
  Inventory + red-flag scan for Claude Code skills. Part of the skill-optimizer skill.
.DESCRIPTION
  Walks a skills root (default: ~/.claude/skills) and, for each folder containing a
  SKILL.md, emits: description length (chars + ~tokens at chars/4), body line count,
  bundled file count, gotchas-section heuristic, progressive-disclosure pointer count,
  and threshold flags. Deterministic measurement belongs in a script, not in model
  output (rubric criterion H).
.PARAMETER Root
  Skills directory to scan. Run once per scope (user + repo) and compare skill names
  across runs to catch cross-scope duplicates.
.PARAMETER Json
  Emit JSON instead of a markdown table.
.EXAMPLE
  .\audit-skills.ps1
  .\audit-skills.ps1 -Root "C:\repo\.claude\skills" -Json
#>
param(
  [string]$Root = (Join-Path $env:USERPROFILE '.claude\skills'),
  [switch]$Json
)

if (-not (Test-Path $Root)) {
  Write-Output "Skills root not found: $Root"
  exit 1
}

$results = @()
$dirs = Get-ChildItem -Path $Root -Directory | Where-Object { $_.Name -notlike '*-workspace' }

foreach ($dir in $dirs) {
  $skillFile = Join-Path $dir.FullName 'SKILL.md'
  if (-not (Test-Path $skillFile)) { continue }

  $raw = Get-Content $skillFile -Raw -Encoding UTF8
  $totalLines = ($raw -split "`n").Count

  # --- frontmatter description ---
  $desc = ''
  $fmLines = 0
  $fm = [regex]::Match($raw, '(?s)\A---\s*\n(.*?)\n---')
  if ($fm.Success) {
    $fmLines = ($fm.Value -split "`n").Count
    $dm = [regex]::Match($fm.Groups[1].Value, '(?s)(?:^|\n)description:\s*(.*?)(?=\n[A-Za-z_-]+\s*:|\z)')
    if ($dm.Success) { $desc = ($dm.Groups[1].Value -replace '\s+', ' ').Trim() }
  }
  $descChars = $desc.Length
  $descTokens = [math]::Round($descChars / 4)
  $bodyLines = $totalLines - $fmLines

  # --- bundled files (everything except SKILL.md; evals/ are skill-creator artifacts, not content) ---
  $bundled = @(Get-ChildItem -Path $dir.FullName -Recurse -File |
    Where-Object { ($_.Name -ne 'SKILL.md') -and ($_.FullName -notmatch '\\evals\\') })
  $bundledCount = $bundled.Count

  # --- heuristics ---
  $hasGotchas = [bool]([regex]::IsMatch($raw, '(?im)gotcha|pitfall|edge case|anti-pattern|mistakes?|known issue|failure mode|never do|^#+\s*(never|don''t)\b'))
  # lookbehind: don't match dir names mid-path (e.g. services/x/config/settings.py is not a skill-local pointer)
  $pointerCount = ([regex]::Matches($raw, '(?i)(?<![\w/\\.-])(references|scripts|assets|prompts|templates|config|examples)/[\w][\w.\-/]*')).Count

  # --- per-file orphan detection: bundled file whose relative path AND bare filename
  #     both never appear in SKILL.md. Files referenced only via a glob/pattern
  #     (e.g. "prompts/NN-*.md") show up as false orphans — judge in the per-skill read.
  $orphans = @()
  foreach ($f in $bundled) {
    $rel = $f.FullName.Substring($dir.FullName.Length + 1) -replace '\\', '/'
    if (($raw.IndexOf($rel, [StringComparison]::OrdinalIgnoreCase) -lt 0) -and
        ($raw.IndexOf($f.Name, [StringComparison]::OrdinalIgnoreCase) -lt 0)) {
      $orphans += $rel
    }
  }

  # --- dangling pointers: SKILL.md points at a bundled path that doesn't exist ---
  $dangling = @()
  $ptrValues = [regex]::Matches($raw, '(?i)(?<![\w/\\.-])(?:references|scripts|assets|prompts|templates|config|examples)/[\w][\w.\-/]*') |
    ForEach-Object { $_.Value } | Sort-Object -Unique
  foreach ($p in $ptrValues) {
    if ($p -match '[\*\?]') { continue }  # glob pattern, not a literal path
    if (-not (Test-Path (Join-Path $dir.FullName ($p -replace '/', '\')))) { $dangling += $p }
  }

  # --- threshold flags ---
  $flags = @()
  if ($descChars -gt 400) { $flags += 'DESC>400c' }
  if ($bodyLines -gt 400) { $flags += 'BODY>400L' }
  if (-not $hasGotchas) { $flags += 'NO-GOTCHAS' }
  if ($orphans.Count -gt 0) { $flags += "ORPHANS:$($orphans.Count)" }
  if ($dangling.Count -gt 0) { $flags += "DANGLING:$($dangling.Count)" }

  $results += [pscustomobject]@{
    Skill        = $dir.Name
    DescChars    = $descChars
    DescTokens   = $descTokens
    BodyLines    = $bodyLines
    BundledFiles = $bundledCount
    HasGotchas   = $hasGotchas
    Pointers     = $pointerCount
    Flags        = ($flags -join ', ')
    OrphanList   = ($orphans -join '; ')
    DanglingList = ($dangling -join '; ')
  }
}

if ($Json) {
  $results | ConvertTo-Json
} else {
  Write-Output ("Skills root: {0}  ({1} skills)" -f $Root, $results.Count)
  Write-Output ''
  Write-Output '| Skill | Desc chars | ~Tokens | Body lines | Bundled | Gotchas | Pointers | Flags |'
  Write-Output '|---|---|---|---|---|---|---|---|'
  foreach ($r in ($results | Sort-Object DescChars -Descending)) {
    Write-Output ('| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} |' -f $r.Skill, $r.DescChars, $r.DescTokens, $r.BodyLines, $r.BundledFiles, $r.HasGotchas, $r.Pointers, $r.Flags)
  }
  $totalTokens = ($results | Measure-Object -Property DescTokens -Sum).Sum
  Write-Output ''
  Write-Output ("Always-on description cost: ~{0} tokens loaded EVERY session (this root only)." -f $totalTokens)

  $problems = $results | Where-Object { $_.OrphanList -or $_.DanglingList }
  if ($problems) {
    Write-Output ''
    Write-Output 'File-level findings:'
    foreach ($r in $problems) {
      if ($r.OrphanList)   { Write-Output ("  {0} - orphans (no mention in SKILL.md): {1}" -f $r.Skill, $r.OrphanList) }
      if ($r.DanglingList) { Write-Output ("  {0} - dangling pointers (path missing): {1}" -f $r.Skill, $r.DanglingList) }
    }
  }
}
