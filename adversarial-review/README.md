# Adversarial Review Skill

A reusable AI review workflow for improving code, architecture, product decisions, security posture, and implementation plans through structured adversarial collaboration.

This skill uses scoped sub-agents, claim tracking, adversarial review, impact tracing, deduplication, and human approval gates to improve decisions before action is taken.

## Why Markdown and YAML?

Markdown is used for prompts, templates, and documentation because it is readable by humans, easy for AI coding tools to parse, and simple to version in Git.

YAML is used for structured configuration because it gives the workflow a stable machine-readable contract. This makes it easier to adapt the skill across ChatGPT, Claude, Codex, Cursor, Windsurf, Claude Code, custom scripts, and future AI IDEs.

Plain `.txt` prompts work, but Markdown is better for long-term reuse because it supports headings, examples, tables, fenced blocks, and embedded instructions without becoming hard to scan.

## Folder Structure

```txt
adversarial-review/
├── README.md
├── SKILL.md
├── config/
│   ├── skill.yaml
│   ├── agents.yaml
│   ├── review-modes.yaml
│   └── safety-gates.yaml
├── prompts/
│   ├── 00-orchestrator.md
│   ├── 01-investigator.md
│   ├── 02-devils-advocate.md
│   ├── 03-impact-tracer.md
│   ├── 04-fix-planner.md
│   ├── 05-triage-lead.md
│   └── 06-final-decision.md
├── templates/
│   ├── review-packet.md
│   ├── claim-ledger.md
│   └── review-report.md
└── examples/
    ├── code-review-example.md
    ├── architecture-review-example.md
    └── decision-review-example.md
```

## Core Pattern

1. Narrow the scope.
2. Investigate one specific risk or decision.
3. Challenge the finding with a separate adversarial agent.
4. Trace real-world impact.
5. Plan the smallest safe fix.
6. Deduplicate and prioritize.
7. Make a final decision.

## Good Use Cases

- Pull request review
- Architecture decisions
- Auth and permissions review
- AI agent workflow review
- Vendor or dependency evaluation
- Production readiness review
- Refactor planning
- Risk review before launch
- Product strategy decisions

## Do Not Use For

- Exploit creation
- Malware
- Credential theft
- Unauthorized system testing
- Bypass instructions
- Offensive security operations
- Destructive actions

## Basic Usage

Fill out `templates/review-packet.md`, then run the prompts in order:

1. `prompts/00-orchestrator.md`
2. `prompts/01-investigator.md`
3. `prompts/02-devils-advocate.md`
4. `prompts/03-impact-tracer.md`
5. `prompts/04-fix-planner.md`
6. `prompts/05-triage-lead.md`
7. `prompts/06-final-decision.md`

For a single chat window, use the all-in-one prompt in `SKILL.md`.
