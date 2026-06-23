# Measuring Skill Usage

Anthropic instruments skill usage company-wide with a PreToolUse hook that logs every skill invocation — revealing which skills are popular and which are *undertriggering* relative to expectations. (Their example implementation: https://gist.github.com/ThariqS/24defad423d701746e23dc19aace4de5)

Iteration on data beats iteration on vibes: a skill that never triggers either has a description problem or shouldn't exist.

## Local equivalent (Windows / PowerShell)

A `PreToolUse` hook matching the `Skill` tool, appending JSONL to `~/.claude/skill-usage.jsonl`. Install via the `update-config` skill (hooks live in `settings.json` — the harness executes them, not the model). Use the **exec form** (`command` + `args` array — spawned directly, no shell):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          {
            "type": "command",
            "command": "powershell",
            "args": [
              "-NoProfile",
              "-Command",
              "$d = [Console]::In.ReadToEnd() | ConvertFrom-Json; $rec = @{ ts = (Get-Date).ToString('o'); skill = $d.tool_input.skill; cwd = $d.cwd } | ConvertTo-Json -Compress; Add-Content -Path (Join-Path $env:USERPROFILE '.claude\\skill-usage.jsonl') -Value $rec -Encoding utf8"
            ],
            "async": true,
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

Notes:
- **Why exec form, not a single command string:** on Windows without Git Bash, string-form hook commands run through PowerShell, which expands `$d`/`$rec` inside the double-quoted string *before* the inner powershell ever sees them — the hook silently logs nothing. The `args` array bypasses shell parsing entirely. (Verified by pipe-test 2026-06-10; the string form reproduces the failure.)
- Log only metadata (timestamp, skill name, cwd) — not args, which can contain sensitive content.
- `async: true` keeps the ~300ms powershell startup off the critical path of every Skill call.
- Installing this hook may be blocked by the permission classifier as self-modification — if so, hand the JSON to the user to paste into `~/.claude/settings.json` themselves.

## Reading the data (after ~2+ weeks)

```powershell
Get-Content (Join-Path $env:USERPROFILE '.claude\skill-usage.jsonl') -Encoding utf8 |
  ForEach-Object { ($_ | ConvertFrom-Json).skill } |
  Group-Object | Sort-Object Count -Descending | Format-Table Name, Count
```

Interpretation:
- **Zero invocations + broad description** → undertriggering. Candidate for a description rewrite verified with skill-creator trigger evals.
- **Zero invocations + you don't miss it** → candidate for deletion (its description is pure always-on cost).
- **Very high frequency** → optimization target: is it model-pinned appropriately? Could bundled scripts cut its per-run cost?
- Compare against `optimization-log.md` entries: did a description trim change a skill's trigger rate?
