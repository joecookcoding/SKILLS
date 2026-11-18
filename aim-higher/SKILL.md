---
name: aim-higher
description: "Raise the ambition of a task before handing it to Claude: ask for the outcome instead of the task (altitude), the expert's version built from raw material (depth), methods from other fields (range), and an outside judge that shows it worked. Use for \"be more ambitious\", \"aim higher\", \"think bigger\", \"what should I actually be asking for\", \"the goal behind the goal\", \"a deeper version of this task\", \"what would an expert do here\", \"rewrite my prompt to be more ambitious\", \"I keep asking Claude for small fixes\", \"take me out of the loop\", \"turn this into a durable workflow\", or before writing a plan or a long-running agent loop. Not for executing a task the user already scoped, or for picking models (plan-model-picker)."
---

# Aim Higher

People ask for work at the layer it reached them: "fix this crash", "make the QBR slides".
The model does exactly that. This skill rewrites the ask **one level up** (altitude),
**one level deeper** (depth) or **one field wider** (range), and ties each version to a
judge that isn't the model. The result is a brief the user chooses from. It never widens
the work on its own.

Built on Felix Rieseberg's "How to be more ambitious" (2026-10-13) and the posts that put
it into practice; read `references/sources.md` for the list and how they connect.

## The judge comes first

Terence Tao: AI has driven the cost of ideas to almost zero, so the bottleneck is now
checking them. A bigger ask with no outside judge produces more confident output that
nobody can trust. Every version in the brief carries the check that would show it worked.
For code, `test-strategy` picks those checks.

## Workflow

1. **Say the task as verbs.** Nouns hide the job. A QBR "deck" is "getting busy people
   to believe a story about cause and effect, and to decide under uncertainty, in 30
   minutes." The verbs show which outcomes and which fields are in play.
2. **Altitude: climb the ladder.** Ask "what should happen next?" and "what is the goal
   behind the goal?" Write two or three rungs:

   | Rung | Example |
   |---|---|
   | Task | Fix this crash |
   | Outcome | Keep the app crash-free |
   | System | A loop that pulls crash reports, reproduces each on the right OS and version, fixes it, and proves the fix |

   Altitude fits when there will be meetings about the work, when the same kind of task
   keeps coming back, or when a person is only relaying one task after another. It fits
   badly for creative work, where the artifact is the point, and for one-offs. To find the
   right height inside a company, look at the goals of the user's manager's manager.
3. **Depth: the expert's version, not a bigger one.** Answer four questions:
   1. What would a top professional in this field do here that nobody asked for?
   2. What is the **rawest material** they would start from (event logs, not the
      dashboard; the database, not the slide)?
   3. Which **methods and tools** would they use (a database and a statistical model,
      not a markdown table)?
   4. What, **other than the model or the user**, would show the result is right?

   Then use the moves: set a target that seems unreasonable and treat it as reasonable
   (200 ms, not 5 s); test a belief against raw data ("we think churn is an onboarding
   problem: reproduce that"); produce new knowledge and check it on data it hasn't seen
   ("find the earliest churn signal we don't know about, and show it predicts next month").
4. **Range: borrow fields.** From the verbs, list the fields that do that job, and
   assemble a crew: an analyst, a journalist and an editor for the story; a short seller
   and a forensic accountant as the red team. Ask for **what each one does** (their
   methods and checks), never their voice.
5. **Name the judge for each rung,** the strongest one available:
   - the real system running: an end-to-end run, telemetry, replayed production traffic;
   - history, or the old system: a backtest ("show from our own history it would have
     caught this sooner"), a differential run, running beside the current process for a
     quarter;
   - a held-out set the work never saw;
   - a tool with pass/fail: a compiler, a test, a schema, a proof assistant;
   - a separate grader model with a rubric of checkable claims;
   - a domain expert.

   "The model reviews its own work" is not on the list. If no judge fits, lower the rung.
6. **List the instruments.** The higher rungs need access. For each one, name what the
   agent needs in order to act and see without help: crash reports, a map from app version
   to git commit, machines to reproduce on, telemetry that traces back to your own code,
   read access to the raw data, a staging environment. Missing instruments become the
   first tasks, and they are often the whole first week.
7. **Set the limits.** More ambition means the agent touches more, so state:
   - **decisions that need a person:** anything hard to undo (a schema, money, messages
     sent outside, deletes);
   - **invariants** that must hold throughout ("docs open almost instantly", "an
     acknowledged edit is never lost");
   - **a budget** (time, spend per run) and **a stop rule** (three failed rounds, or a
     score that stalls for two or three, means a person looks).
8. **Recommend one rung and its smallest proof.** Say which rung fits and why. Carry one
   idea: a prototype with three good ideas hidden among twenty bad ones convinces nobody.
   Name the first step that would show, within about a day, that the rung works.
9. **Write the brief** from `assets/brief.template.md` and give it to the user. They
   pick the rung. Don't start the larger work in the same turn unless they asked for it.

For an outcome that runs as a loop (a long-running build, a scheduled agent, a
hardening run, climbing an eval score), read `references/durable-loops.md` before
step 7. It has the patterns that keep those loops honest with few interventions.

## Gotchas

- **Role-play is not range.** "Act as a statistician" changes the vocabulary, not the
  method. Ask for the instrument a statistician would use.
- **Bigger is not deeper.** More slides, more features and more agents are scope, not
  ambition.
- **The model can't be its own judge.** Even a careful self-review shares the author's
  blind spots. Name an outside judge, or lower the rung.
- **Altitude without instruments makes the agent guess.** "Keep the app crash-free"
  with no access to crash reports turns into reading code and hoping.
- **One failure doesn't mark the limit.** Capability is jagged and moves with each
  model: what failed may sit right next to what works, and may work next quarter. Write
  down where it failed (the bottleneck) and try the ambitious version again on the next
  model. The reverse also holds: success on one task says little about the task next to it.
- **Pick hard cases because a person can say why they're hard,** not because today's
  model fails them. Otherwise you measure one model's blind spots, not what matters.
- **A score you climb, you overfit.** Hold out cases the work never sees. If the training
  cases improve while the held-out ones stay flat, the gain is fake.
- **The brief is a proposal.** The user asked for a task. Doing the outcome-level
  version without asking spends their time and money on a choice that was theirs.

## When not to use

The user scoped the task and wants it done; a small, well-defined change; creative work
where the user wants their own idea executed. Do the task.

## Composition

- `test-strategy`: the judge for code; which checks prove the outcome.
- `codebase-exploration`: to find instruments the repo already has (crash reporting,
  telemetry, seed scripts) before listing them as missing.
- `adversarial-review`: to attack the brief's assumptions before committing weeks to it.
- `plan-model-picker`: once the chosen rung becomes a phased plan.
