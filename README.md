# SKILLS

A collection of [Claude Code](https://claude.com/claude-code) **skills** — reusable, model-invoked workflows that give coding agents domain expertise on demand.

Built and maintained by **[Joe Cook](https://www.cookcoding.com/)** ([Cook Coding](https://www.cookcoding.com/)) — full-stack developer and digital solutions architect. *Turning ideas into production-ready digital products.*

> 📍 Florida, USA · [cookcoding.com](https://www.cookcoding.com/) · [@joecookcoding](https://github.com/joecookcoding) · [LinkedIn](https://www.linkedin.com/in/cookcoding/)

---

## What is a skill?

A skill is a self-contained folder with a `SKILL.md` file. Its frontmatter `description` tells the agent **when** to use it; the body tells the agent **how**. Skills load lazily — they cost nothing until something in the conversation matches their trigger, then the full instructions (plus any bundled references, templates, scripts, and evals) are pulled into context.

The result: instead of one model improvising builder, reviewer, and skeptic all at once, you get focused, repeatable, battle-tested procedures that fire exactly when they're relevant.

Each skill here follows a consistent layout:

```
<skill-name>/
├── SKILL.md           # frontmatter (name + trigger description) and the core workflow
├── references/        # deep-dive material loaded on demand
├── templates/ assets/ # reusable scaffolds the skill fills in
├── scripts/           # bundled executables (when the skill runs code)
└── evals/             # test cases that verify the skill triggers and performs correctly
```

---

## The skills

### 🛠️ Engineering & code quality

| Skill | What it does |
|-------|--------------|
| **[adversarial-review](adversarial-review/)** | A structured, multi-agent review workflow. Splits the work across narrow roles — Orchestrator, Investigator, Devil's Advocate, Impact Tracer, Fix Planner, Triage Lead, Final Decision — to catch what a single pass misses. Use for thorough reviews, red-teaming, ship/no-ship calls, and high-stakes engineering *or* business decisions, with explicit human-approval gates on risky actions. |
| **[codebase-exploration](codebase-exploration/)** | An *investigate-before-mutate* discipline (adapted from NVIDIA's TensorRT-LLM exploration playbook) for any bug fix, feature, or refactor. Search the concept not the symbol, read callers before callees, find existing helpers before writing new ones, and use a three-pass file budget to avoid the "read 30 files, still lost" spiral. |
| **[optimize-claude-memory](optimize-claude-memory/)** | Audits and restructures a repo's agent memory (`CLAUDE.md`, `AGENTS.md`, skills, `MEMORY.md`) to cut per-turn token usage, make docs portable across Claude Code / Copilot / Cursor / Cody, and improve trigger accuracy. Always produces a plan for approval before editing. |

### 🚀 Founder, brand & growth

| Skill | What it does |
|-------|--------------|
| **[founder-validation-skills](founder-validation-skills/)** | A 5-step workflow taking a founder from "I have an idea" to a validated landing page and growth plan — without building the wrong thing. Customer-pain research → lead-magnet selection → copy → site build → funnel + 30/60/90 plan. Don't build until pain is validated. |
| **[profile-hero-redesign](profile-hero-redesign/)** | A 5-step workflow that turns a clean-but-generic profile, personal-brand, or service-provider hero into a focused, premium, conversion-driven layout. Diagnosis → message hierarchy → visual composition → CTA conversion → responsive polish. |

### 🖼️ Utilities

| Skill | What it does |
|-------|--------------|
| **[heic-to-jpeg](heic-to-jpeg/)** | Converts iPhone HEIC/HEIF images to widely-compatible JPEG, preserving EXIF metadata and orientation. Handles single files or whole directories, skips already-converted files, and auto-installs `pillow` + `pillow-heif` if missing. |

---

## Using these skills

These are skills for [Claude Code](https://claude.com/claude-code). Once a skill is on your skills path, Claude invokes it automatically whenever the conversation matches its trigger description — you don't have to call it by name.

### Install

Clone the repo and drop the skills where Claude Code looks for them:

```powershell
git clone https://github.com/joecookcoding/SKILLS.git

# User-level skills (available in every project)
Copy-Item -Recurse SKILLS\* "$env:USERPROFILE\.claude\skills\"
```

```bash
# macOS / Linux equivalent
git clone https://github.com/joecookcoding/SKILLS.git
cp -r SKILLS/* ~/.claude/skills/
```

Or copy individual skill folders into a project's `.claude/skills/` directory to scope them to that repo.

### Invoke

- **Automatically** — just describe your task. "Give this PR a thorough review" loads `adversarial-review`; "convert these HEIC photos" loads `heic-to-jpeg`.
- **Explicitly** — reference the skill by name, e.g. *"use codebase-exploration before you touch this."*

---

## Author

**Joe Cook** — Cook Coding. Full-stack development across Python, Next.js, React, Node.js, and Azure, with a focus on AI-powered tools, scalable SaaS, and technology for churches and nonprofits.

- 🌐 [cookcoding.com](https://www.cookcoding.com/)
- 💼 [linkedin.com/in/cookcoding](https://www.linkedin.com/in/cookcoding/)
- 🐙 [github.com/joecookcoding](https://github.com/joecookcoding)

---

## Contributing

Each skill is independent — open an issue or PR against the relevant folder. New skills should follow the layout above and include a clear, trigger-rich `SKILL.md` description plus `evals/` cases that prove the skill fires when it should.
