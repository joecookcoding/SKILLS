---
name: plan-model-picker
description: "Pick the Claude model and effort level for each phase of a plan, whether it needs a lead session, and which phases can launch at once. Use for \"which model should run this plan\", \"what model for each phase\", \"model and effort for this plan\", \"how do I launch this plan\", \"which phases can run in parallel\", \"split this plan into phases\", \"make this plan into action lists\", \"do I need an executor or orchestrator session\", or before handing a plan file to fresh sessions. Not for writing or reviewing the plan, or for picking a model in API code (claude-api)."
---

# Plan Model Picker

Point this at a plan. It returns a **launch sheet**: the model and effort level for
each phase, a lead session if the plan needs one, which phases can be launched at
the same time, and the line that starts each session.

## Why per phase

- **Fit follows what a phase does, not how well it is written.** A clear spec
  doesn't make a phase small: a ten-line task that adds one enum value can touch
  every reader of that type. A whole plan on the top model overpays; a
  wide-reaching phase on a small model fails an hour in.
- **One fresh session per phase.** A session's prompt cache belongs to the model
  that wrote it, and moving down a tier drops the earlier reasoning. Switching
  models mid-session pays for both. So the phase is the unit: each one starts
  clean, on its own model, from the written plan.

## Workflow

1. **Read the plan and the project's standing rules.** The plan is the argument, or
   ask for its path. Then read what binds every session: the repo's `AGENTS.md`
   and the plan's conventions file. Note commit rules, where tests may run,
   whether subagents are allowed, deadlines, and gates that wait on a person.
2. **Check the model lineup.** Read `references/model-guide.md`. It carries an
   as-of date. If it is more than about 60 days old, or it names models the
   session's environment doesn't list, fetch its source again and update the
   file before relying on it. If the fetch fails, use it and say its date.
3. **Find the phases, or cut them.** Keep phases the plan already has. If it has
   none, cut along the lines in "Cutting phases". A plan that is one concern and
   under about a day of work stays whole: one executor session, one row.
4. **Rate each phase** on four things, then map it with the guide:
   - **Reach:** how much working code it changes, and how many places read what
     it changes.
   - **Unknowns:** an outside API nobody has read live, behaviour the plan
     guesses at, decisions left open.
   - **Cost of a wrong result:** an access policy, a data migration, a deploy
     that can't be undone, a deadline with no second try.
   - **Length and attention:** hours unattended, or short with the owner watching.
   Raise effort before raising the model. Give each row a one-line reason the
   owner could repeat to someone else.
5. **Decide whether a lead session is needed.** Usually it is not: the plan is the
   coordinator. Add one when two or more phases run at once, when open decisions
   will be settled mid-run, or when the plan has not been checked against the
   code. See "The lead session".
6. **Group the phases into waves** with the rules in "Launching at once".
7. **Write the launch sheet** from `assets/launch-sheet.template.md`. Put it in
   the plan, as its own section, unless the user asked only for advice: a fresh
   session reads the plan, not this conversation. Give absolute paths in the
   kickoff lines.

## Cutting phases

A phase must leave the tree green and be committable on its own. Cut here:

- **The deadline floor first.** Whatever must ship before the rest becomes phase
  1, even if it is the easy part.
- **One schema concern each.** Phases that add migrations own a fixed block of
  numbers; that fixes their order.
- **By reach.** New files that follow an existing pattern separate from changes
  to code many screens read.
- **Unknowns alone.** Work against an outside system gets its own phase, so a
  surprise there stops one session, not four.
- **Close-out last.** Documentation, trackers and the end-to-end check, after
  the code they describe exists.

Don't cut finer than the commits the owner wants. Five phases is a lot.

## The lead session

A lead (also called executor, orchestrator or advisor) reviews the plan against
the code, hands out phases, owns files more than one phase touches, and answers
the phase sessions' questions. It writes no phase's code.

- Run it on the strongest model at medium effort, and keep its context lean. Long
  logs and file dumps belong in the phase sessions.
- Where subagents are allowed, the lead can start the phases itself. Where they
  are not (check the user's rules), the user launches each phase as a separate
  session and the lead talks to them by message.
- Skip it for a sequential plan with no open decisions. A lead with nothing to
  decide is the most expensive idle session there is.

## Launching at once

Two phases share a wave only when all of these hold:

- **No file in common,** counting generated files, lockfiles, and trackers both
  append to.
- **No ordered resource in common:** migration numbers, version bumps, one deploy
  pipeline, one release channel.
- **Neither needs the other's output:** a table, a type, a route.
- **A working tree each** (a git worktree or a second clone). Sessions in one tree
  share one index and one `git status`, so each sees the other's edits as
  changes nobody explained. The exception is a session that writes only outside
  the repo, or only documents; even then, tell both what the other owns.
- **No shared single-file machine resource:** one test database, one emulator,
  one port.

When unsure, sequence them. Waiting an hour costs less than untangling two
half-finished phases.

## Gotchas

These come from running a five-phase plan with two live sessions in one tree.

- **A second session in the same working tree surprises the first.** Its staged
  deletions and edits show up in the first session's `git status`. Before
  touching the tree, message every live session with exactly which paths are
  yours, and stage with explicit paths.
- **Any session's package-manager command can rewrite a shared lockfile.** Every
  other session then sees a change it didn't make. Put the restore rule in the
  block all phases read.
- **A rule one phase learns belongs to all of them.** "All tests run on the build
  box" arrived mid-run in phase 1; it had to go into the plan's shared block the
  same hour, or phases 2 to 5 would have started without it.
- **A plan that moves while a phase runs needs a pointer at the old path** and a
  message to the session, or its next edit fails with no explanation.
- **Phase numbers often hide an order.** Migration numbers assigned per phase mean
  phase 4 cannot go before phase 2 without renumbering.
- **Same answer on every row is a non-answer.** If every phase comes out on the
  same model and effort, the ratings were not done; redo step 4.
- **A phase that ships alone, with nobody reviewing before deploy, earns one
  notch more effort** than its size suggests. "Unattended for hours" is a reason
  to go up a model; "the owner is watching" is not.
- **Don't recommend what the project forbids.** If subagents are banned, leave
  out small-model subagent patterns and orchestration; waves are sessions the
  user starts by hand.
- **Model names go stale.** Quote the guide's date in the sheet, and prefer the
  names the session's own environment lists over the ones in the guide.

## When not to use

- **The plan has not been checked against the code.** Say so first: a launch
  sheet for a wrong plan runs the wrong work efficiently. Either review it
  now (the `adversarial-review` skill for high stakes, if installed), or give
  a provisional sheet whose first row is the review, marked as provisional.
- **Choosing a model for an API call or an app feature.** The built-in
  `claude-api` skill covers model IDs, pricing and limits.

## Composition

- `adversarial-review`: before, for a plan that carries real risk.
- `commit`: after each phase, for its message, where the project has the agent
  stage and the owner commit.
