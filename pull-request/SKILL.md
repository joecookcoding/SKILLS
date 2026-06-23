---
name: pull-request
description: Generate a pull request message (title + body) from ALL commits on the current branch since the base branch. Use when the user wants to open a PR, finalize a feature branch, or asks for a "PR message", "PR description", "pull request body", or runs /pull-request. Runs on Sonnet for the turn for stronger multi-commit synthesis while keeping session token cost well below Opus.
model: sonnet
allowed-tools:
  - Bash(git status:*)
  - Bash(git log:*)
  - Bash(git diff:*)
  - Bash(git rev-list:*)
  - Bash(git rev-parse:*)
  - Bash(git branch:*)
  - Bash(git remote:*)
  - Bash(git symbolic-ref:*)
  - Bash(git fetch:*)
  - Bash(gh repo view:*)
  - Read
argument-hint: "[base-branch]"
user-invocable: true
---

# Pull Request Message Generator

Produce a high-quality PR title + body synthesized from **every commit** on the current branch since the base branch.

## Why this skill runs on Sonnet

The `model: sonnet` frontmatter above is a per-turn override — for the duration of this skill's turn, Claude Code uses Sonnet, then the session model resumes on your next prompt. Drafting a PR message is synthesis work: reading every commit body, grouping them by theme, and writing a reviewer-facing narrative. Sonnet handles the theme-grouping and prose quality noticeably better than Haiku on long or multi-concern branches, while still costing far less per turn than Opus. If you ever want to force a different model for a single run, start a new turn and invoke `/pull-request` after setting `/model` yourself.

## Usage

```
/pull-request                    # auto-detect base (origin/HEAD → gh → main/master)
/pull-request develop            # explicit base branch
/pull-request --base release/x   # same, long form
```

## Instructions

### Step 1 — Detect the base branch

If the user passed a base branch as an argument, use it. Otherwise walk this ladder and stop at the first step that yields a branch name:

1. `git symbolic-ref --short refs/remotes/origin/HEAD` — strip the `origin/` prefix from the output.
2. `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`
3. Existence check: `git rev-parse --verify main`, then `git rev-parse --verify master` — use whichever verifies.
4. Stop and ask the user which base branch to compare against.

**Remote-only base:** if the local `<base>` doesn't exist (`git rev-parse --verify <base>` fails) but `origin/<base>` does, use `origin/<base>` in **all** ranges below (`origin/<base>..HEAD`, `origin/<base>...HEAD`).

### Step 2 — Sanity check there's work to describe

```bash
git status -sb | head -1
git rev-list --left-right --count <BASE>...HEAD
```

If HEAD is `0` commits ahead of base, stop and tell the user there's nothing to PR. If the working tree has uncommitted changes, note them at the end (they won't be in the PR until committed) but don't let them block the message.

### Step 3 — Read the branch's full history

Collect every commit body and the per-file diff summary. These are the only inputs needed to write the message — **do not read file contents**, the commit messages + stat are sufficient.

```bash
git log <BASE>..HEAD --pretty=format:"%h%n%s%n%b%n---%n"
git diff <BASE>...HEAD --stat
git log <BASE>..HEAD --name-only --pretty=format:"COMMIT %h %s"
```

The third command maps files to commits, which helps when grouping themes across commits.

### Step 4 — Look for theme groupings

Read the commit subjects + bodies together. Ask: *does this branch have one coherent story, or multiple unrelated concerns that happened to land on the same branch?* A clean feature branch usually has one theme; a long-running `fe-refinements`-style branch may have several (polish + a feature + a follow-up parity pass).

Group commits by theme, not chronologically. The reviewer doesn't care which commit came first — they care what changed and why.

### Step 5 — Produce the PR message

Output a **single code block** with exactly this structure:

```markdown
# Title: <Conventional-style title, under 70 chars, no emoji>

## Summary

2–4 bullets covering the major themes across commits. Write for a
reviewer who hasn't seen the branch — lead with *why*, not *what*.

## What's in this PR

Group by **theme**, not per-commit. Two common patterns — pick what fits:

- If the branch has one theme: use a single section of prose + bullets.
- If multiple themes: use `### Theme Name` subheadings (e.g.,
  `### Budget Catalog Integration`, `### Post-Meeting Review Polish`).

Within each theme, short prose + bullets. Reference commit hashes only
when it helps the reviewer navigate — e.g., `(abc1234)`.

## Platform / DX notes

Anything that affects the shared platform: new dependencies, new npm
scripts, config changes, generated types, skill/tooling updates, bundle
size impact. Omit this section entirely if none apply.

## Known backend dependencies

List any backend tickets, open backend bugs, or API gaps mentioned in
the commits or in any issue/ticket files touched by the diff. Omit if none.

## Test plan

Bulleted markdown checklist (`- [ ]`) covering golden paths + edge cases
the reviewer should hit before approving. Be specific: include routes,
button labels, input values, expected network payloads.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Rules for the body:**

- Every bullet must come from something actually in the commits — no speculation.
- Title excludes emoji. Body may use emoji only in the `Generated with Claude Code` footer.
- Even a single-commit branch uses the theme structure (it'll just have one theme).
- The `# Title: ...` line is for parsing — the actual PR title is everything after `# Title: `.

### Step 6 — Present the result to the user

Parse the title out of the first line (`# Title: ...`). Present the message directly in chat for the user to copy — **do not write it to any file**. Emit a push command plus a `gh pr create` that opens the PR form for the user to paste the body into:

````markdown
## Proposed PR Message

(Drafted from <N> commits on `<branch>` vs `<base>`.)

<the full markdown code block from Step 5, verbatim>

### Ready to open the PR

Copy the body above, then:

```
git push -u origin <branch>
gh pr create --base <base> --title "<title parsed from above>" --web
```

`--web` opens the GitHub PR form in the browser with the title prefilled — paste the body into the description box. (Prefer staying in the terminal? Drop `--web` and `gh` opens an editor for the body instead. Either way there's no temp file to clean up.)
````

## Composition with other skills

- **Pre-merge review of the branch** → use `adversarial-review` or the `code-review` plugin before opening/merging the PR. This skill only writes the message; it does not review the code.
- **Boundary:** `superpowers:finishing-a-development-branch` decides merge-vs-PR-vs-cleanup. This skill does not make that call — it only writes the PR message (and emits the ready-to-run commands above).

## What this skill must NOT do

- Do not push the branch.
- Do not run `gh pr create`.
- Do not amend, rebase, or squash existing commits.
- Do not write to `.git/`, the working tree, or any file — the message goes in chat for the user to copy. No temp files (no `pr-body.md`).
- Do not describe uncommitted working-tree changes in the body (they're not in the PR) — only mention them as a one-line warning above the message.

## Edge cases

**No remote tracking.** If `git status -sb` shows no `origin/<branch>` tracking, include `-u origin <branch>` in the push command (already in the template).

**Base branch missing locally.** If the detection ladder (Step 1) yields a base name but no local branch exists, use `origin/<base>` in all ranges. If detection fails entirely, ask which base branch to compare against.

**Branch equals base.** If `git rev-list --left-right --count <base>...HEAD` returns `N 0` (HEAD not ahead of base), stop — nothing to PR.

**Detached HEAD.** If `git status -sb` shows `HEAD (no branch)`, stop — tell the user to create a branch first; a PR needs a branch to push.

**Stale local base.** Run `git fetch origin <base>` and diff against `origin/<base>` — otherwise the message describes commits that were already merged upstream.

**Squash-merged base.** If the base advances via squash-merges, the `git rev-list` ahead-count can be inflated (already-merged work still counts as "ahead"). Sanity-check the count against the actual `git log <base>..HEAD` content before describing N commits of new work.

**Very large branches.** Commit messages + diff stat + per-commit file lists are compact even for 50+ commit branches. If the commit messages are low quality and the body comes out shallow, tell the user — a good PR message cannot be synthesized from bad commit messages. If the commit bodies are weak, run the `commit` skill on future changes; for this branch, reconstruct intent from the diffs themselves.

## Example invocations

**Single-theme branch:**
```
User: /pull-request
Runs: detect main → 3 commits ahead → read history → produce message
```

**Multi-theme branch:**
```
User: /pull-request
Runs: detect main → 2 commits ahead (bundled 3 unrelated concerns) →
      produce message with 3 theme sections
```

**Non-default base:**
```
User: /pull-request release/2026-05
Runs: uses release/2026-05 as base; everything else identical
```
