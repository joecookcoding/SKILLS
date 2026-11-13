# Platform Facts for Skills

How Claude Code loads, lists and keeps skills. Checked 2026-11-12 against
https://code.claude.com/docs/en/skills on Claude Code v2.1.323. These facts change; when a
number here decides a finding, re-read the docs page first and update this file with the new
date.

## The listing (always-on cost)

- Every session gets a listing of skill names and descriptions. The listing always holds
  every name.
- **Budget: 1% of the model's context window.** At 4 characters per token that is roughly
  8,000 characters on a 200K window and 40,000 on a 1M window (an estimate; the docs give
  only the 1%).
- **Over budget, Claude Code drops descriptions, least-invoked skills first.** The dropped
  skills keep their names and lose every trigger keyword. This is why a fleet's total matters
  more than any one description.
- **Per-skill cap: `description` + `when_to_use` together are truncated at 1,536 characters**
  in the listing. Put the key use case first.
- Personal, project, plugin and synced skills all share the one budget.
- Levers, cheapest first:
  - trim narration out of descriptions (see `description-patterns.md`);
  - `skillOverrides` in settings: `"name-only"` lists a skill without its description,
    `"user-invocable-only"` hides it from Claude but keeps `/name`, `"off"` hides it entirely.
    It does not apply to plugin skills (use `/plugin`);
  - `disable-model-invocation: true` in frontmatter: the description leaves the listing and
    only `/name` reaches the skill. Right for side-effecting tasks the user always starts;
  - raise the budget with `skillListingBudgetFraction` (for example `0.02`) or
    `SLASH_COMMAND_TOOL_CHAR_BUDGET` (a fixed character count). This buys room; it does not
    reduce cost.

## Built-in commands worth running before a manual audit

| Command | What it gives | Needs |
|---|---|---|
| `/doctor` | Estimated listing cost and its biggest contributors | — |
| `/context` | The Skills row: listing size after the budget is applied | v2.1.196+ for an accurate figure |
| `/skill-doctor` | Per-skill cost and how often each is used; flags never-invoked skills | v2.1.252+; run in the terminal on the machine with the session |
| `/doctor prompt-audit <path>` | Stale, conflicting or model-outdated instructions, with proposed edits | v2.1.283+; runs through the bundled `claude-api` skill |
| `claude plugin validate <dir>/.claude/skills` | Frontmatter that fails to parse | v2.1.233+ |
| `claude --debug` | A warning when the listing is over budget; frontmatter parse errors | — |

The user runs slash commands; ask for the output rather than guessing it.

## Lifecycle of a loaded skill

- An invoked SKILL.md enters the conversation as one message and **stays for the rest of the
  session**. Claude Code does not re-read the file. Every body line is a recurring cost, and
  guidance that must hold all task should read as a standing instruction ("run the tests
  after every edit"), not a one-time step.
- The docs' size guidance: **keep SKILL.md under 500 lines** and move detail to other files.
- **After compaction** the most recent invocation of each skill is re-attached, but only its
  **first 5,000 tokens**, within a shared 25,000-token budget filled from the most recently
  used skill. Anything past token 5,000 is gone until the skill is invoked again. So the
  principle, the routing table and the gotchas index go near the top.
- A rule that must hold every time belongs in a hook (the `hooks` frontmatter key keeps it
  with the skill), not in prose the model may skip.

## Frontmatter

Claude Code accepts: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`,
`disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`,
`effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, plus the informational
`metadata`, `license`, `compatibility`. Unknown keys are ignored without an error.

- **Portable keys only** for a claude.ai upload, the Skills API or `package_skill.py`:
  `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Any other
  key is a hard error there. A skill that is both installed locally and shipped as a zip
  needs the six-key frontmatter; the script lists the keys that would break.
- **Malformed YAML does not stop the skill loading.** The body loads with empty metadata, so
  `/name` works and auto-triggering silently doesn't.
- `model` takes an alias (`sonnet`, `opus`, `haiku`, `fable`) or a full ID. An alias follows
  the provider's current model; a full ID pins a version and goes stale. Prefer the alias
  unless the pin is the point, and say why in the body.
- `allowed-tools` grants last one turn; the instructions persist, the permissions don't.
- `${CLAUDE_SKILL_DIR}` is the folder holding SKILL.md. Use it in commands that run a bundled
  script so the path works at personal, project and plugin level.
- `` !`command` `` blocks run before the model sees the skill. A failing command aborts the
  whole invocation.
- `<` and `>` in a description display as `&lt;` and `&gt;`. Use `[placeholder]`.

## Where skills live, and which copy wins

Enterprise over personal (`~/.claude/skills`) over project (`.claude/skills`). Plugin skills
are namespaced (`plugin:skill`), so they never collide. `~/.claude/skills/synced/` holds
skills downloaded from claude.ai: edits there are overwritten by the next sync, so change
those on claude.ai.
