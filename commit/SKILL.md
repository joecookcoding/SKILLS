---
name: commit
description: Generate a commit message based on staged and unstaged changes since the last commit. Reviews changes and creates a conventional commit message for user approval. Runs on Sonnet for the turn for sharper diff synthesis and scope detection while keeping cost well below Opus.
model: sonnet
allowed-tools:
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Read
  - Glob
  - Grep
user-invocable: true
---
# Commit Message Generator

Generate a conventional commit message based on recent changes for user review.

> **Model:** this skill uses `model: sonnet` as a per-turn override — Claude Code switches to Sonnet for the duration of this skill's turn, then the session model resumes on your next prompt. Reading a diff and synthesizing an accurate Conventional Commits message — correct type, right scope, a body that captures the *why* across multiple files — is synthesis work Sonnet handles noticeably better than Haiku, while still costing far less per turn than Opus. Override with `/model` before invoking if you need Opus for a specific commit.

## Usage

```
/commit
```

## Commit Message Format

Messages follow the Conventional Commits specification:

```
<type>(<scope>): <short description>

<body - explains what and why>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types
- `feat` - New feature or capability
- `fix` - Bug fix
- `refactor` - Code change that neither fixes a bug nor adds a feature
- `docs` - Documentation only changes
- `style` - Formatting, missing semi-colons, etc (no code change)
- `test` - Adding or updating tests
- `chore` - Maintenance tasks, dependency updates
- `perf` - Performance improvements

### Scope
- Component or feature area (e.g., `ConfigurationPage`, `MeetingLocations`, `auth`)
- Can be omitted for broad changes

## Instructions

### Current state (auto-collected)

The output below is injected automatically before this skill runs — read it; do not re-run these commands.

!`git status`

!`git diff --stat HEAD`

!`git log -3 --oneline`

### Steps

When this skill is invoked:

1. Read the injected output above: `git status` for changed files, `git diff --stat HEAD` for the change summary, `git log -3 --oneline` for recent commit style. (If you ever re-run `git status`, never use the `-uall` flag — it floods the context with untracked noise that drowns the actual change.)
2. Read the full diff via `git diff HEAD` (or `git diff --staged` if files are staged) **only when the stat summary is insufficient** to write an accurate message
3. Read the key modified files to understand the changes — only when the diff alone is ambiguous (e.g., pure deletions, renames, generated files)
4. Analyze:
   - What type of change is this? (feat, fix, refactor, etc.)
   - What is the scope? (which component/feature area)
   - What is the main purpose of the changes?
   - Why were these changes made?
5. Generate a commit message following the format above
6. Display the message in a code block for the user to review and copy

## Gotchas

- **Empty diff and status** — stop and say "nothing to commit". Do not invent a message.
- **Lockfile/generated noise** — when the stat is dominated by `package-lock.json`, `pnpm-lock.yaml`, or `dist`, describe the source change, not the churn. Read the diff excluding them:
  `git diff HEAD -- . ':(exclude)package-lock.json' ':(exclude)pnpm-lock.yaml'`
- **Pre-commit hooks** — if husky or `.pre-commit-config.yaml` is present, hooks may rewrite files during commit, so the committed content can differ from what was summarized here.
- **Secrets in untracked files** — before suggesting `git add .`, scan the injected status for untracked `.env` / credential / key-looking files and warn instead of blindly staging them.
- **Merge in progress or detached HEAD** — if the injected status shows either, say so instead of proposing a normal commit.

## Output Format

Present the commit message like this:

```
## Proposed Commit Message

Based on your changes to [list key files], here's the suggested commit message:

\`\`\`
<type>(<scope>): <description>

<body explaining what changed and why>

Co-Authored-By: Claude <noreply@anthropic.com>
\`\`\`

### Summary of Changes
- [bullet points of what changed]

### Ready to commit?
Copy the message above and run (PowerShell — the closing '@ must start at column 0):
\`\`\`powershell
git add .
git commit -m @'
<paste message here>
'@
\`\`\`

(In a bash shell, the equivalent is a heredoc: `git add . && git commit -m "$(cat <<'EOF' … EOF)"` — note that `&&` and heredocs are parser errors in Windows PowerShell 5.1, so the PowerShell form above is the default here.)
```

## Important Notes

- This skill does NOT create commits - it only generates the message
- User reviews and commits manually
- Always include `Co-Authored-By: Claude <noreply@anthropic.com>` — org convention for identifying agent-written commits
- Keep the short description under 72 characters
- Focus on the "why" in the body, not just the "what"
- For a branch-level message spanning multiple commits, use the `pull-request` skill instead.
