# SKILLS

A collection of [Claude Code](https://claude.com/claude-code) **skills** — reusable, model-invoked workflows that give coding agents domain expertise on demand.

Built and maintained by **[Joe Cook](https://www.cookcoding.com/)** ([Cook Coding](https://www.cookcoding.com/)) — full-stack developer and digital solutions architect. *Turning ideas into production-ready digital products.*

> 📍 Florida, USA · [cookcoding.com](https://www.cookcoding.com/) · [@joecookcoding](https://github.com/joecookcoding) · [LinkedIn](https://www.linkedin.com/in/cookcoding/) · [X @thejoecook](https://x.com/thejoecook)

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
| **[no-glaze](no-glaze/)** | Senior-engineer feedback mode where accuracy beats agreeableness. Leads with the strongest technical truth, bans flattery openers, labels confidence, pushes back on insecure or over-engineered directions, and separates facts from assumptions. The blunt *register*; pairs with `adversarial-review` (the *pipeline*). |
| **[codebase-exploration](codebase-exploration/)** | An *investigate-before-mutate* discipline (adapted from NVIDIA's TensorRT-LLM exploration playbook) for any bug fix, feature, or refactor. Search the concept not the symbol, read callers before callees, find existing helpers before writing new ones, and use a three-pass file budget to avoid the "read 30 files, still lost" spiral. |
| **[optimize-claude-memory](optimize-claude-memory/)** | Audits and restructures a repo's agent memory into an `AGENTS.md`-only layout: a lean root `AGENTS.md`, per-directory `AGENTS.md` files, procedures moved into skills, and no `CLAUDE.md` (Claude Code reads `AGENTS.md` itself). Cuts per-turn token usage and keeps the docs portable across Claude Code / Copilot / Cursor / Cody. Always produces a plan for approval before editing. |
| **[skill-optimizer](skill-optimizer/)** | Audits and upgrades existing Claude Code skills against Anthropic's skill-authoring best practices — trims bloated descriptions without dropping triggers, splits monolith bodies into references, flags missing gotchas and dead handoffs, and reports drift between a skills repo and the installed copies. Complements `optimize-claude-memory` (which owns a repo's `AGENTS.md` tree). |
| **[zod-validation-patterns](zod-validation-patterns/)** | Zod v4 schema patterns for writing, editing, or reviewing validation code — locking schemas to generated API types, cross-field rules, custom error messages, transforms, `zodResolver` + react-hook-form, and a v3 → v4 migration reference. |

### 🚀 Founder, brand & growth

| Skill | What it does |
|-------|--------------|
| **[founder-validation-skills](founder-validation-skills/)** | A 5-step workflow taking a founder from "I have an idea" to a validated landing page and growth plan — without building the wrong thing. Customer-pain research → lead-magnet selection → copy → site build → funnel + 30/60/90 plan. Don't build until pain is validated. |
| **[profile-hero-redesign](profile-hero-redesign/)** | A 5-step workflow that turns a clean-but-generic profile, personal-brand, or service-provider hero into a focused, premium, conversion-driven layout. Diagnosis → message hierarchy → visual composition → CTA conversion → responsive polish. |

### 🎨 Design & UI

| Skill | What it does |
|-------|--------------|
| **[ui-craft-rules](ui-craft-rules/)** | 39 checkable UI/UX rules (hierarchy, component choice, button copy, radius, colour, dark mode, motion, tokens, AI-ready design systems) plus a 22-point review list of the tells AI-generated UI leaves: action buttons in tab bars, dropdowns for three options, "Are you sure?" dialogs, light cards in dark mode. Works in code or in Figma. Download the ready-to-upload zip: **[dist/ui-craft-rules.zip](dist/ui-craft-rules.zip)**. |

### ⚖️ Legal text

| Skill | What it does |
|-------|--------------|
| **[legal-draft](legal-draft/)** | Drafts or updates legal text: terms of use, privacy policies, cookie notices, NDAs, an MSA, DPAs, a HIPAA BAA, an advisor agreement and an offer letter from [General Legal's](https://github.com/General-Legal/legal-templates) CC0 templates (bundled), plus short notices and disclaimers backed by a project's own terms. It states only what the code does, never renumbers a published clause, and ends with the decisions that belong to the owner or a lawyer. **Not legal advice.** It is drafting help, and anything a customer's money or health depends on needs a lawyer's review. |

### 🖼️ Utilities

| Skill | What it does |
|-------|--------------|
| **[heic-to-jpeg](heic-to-jpeg/)** | Converts iPhone HEIC/HEIF images to widely-compatible JPEG, preserving EXIF metadata and orientation. Handles single files or whole directories, skips already-converted files, and auto-installs `pillow` + `pillow-heif` if missing. |
| **[publix-clip-all](publix-clip-all/)** | A browser-console script that clips every available Publix digital coupon. It clicks **Clip coupon** buttons in throttled batches, presses **Load more** until the list runs out, and logs progress as it goes. You paste it into DevTools in your own signed-in session. It never asks for credentials or calls private APIs. Not affiliated with Publix. |
| **[commit](commit/)** | Generates a Conventional Commits message from your staged/unstaged diff for review — correct type, scope, and a body that captures the *why*. Runs on Sonnet for the turn; never commits for you. |
| **[pull-request](pull-request/)** | Drafts a PR title + body from every commit on the branch since its base, grouped by theme rather than chronologically. Auto-detects the base branch and emits ready-to-run `git push` + `gh pr create` commands. |

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

- **Automatically** — just describe your task. "Give this PR a thorough review" loads `adversarial-review`; "convert these HEIC photos" loads `heic-to-jpeg`; "clip all my Publix coupons" loads `publix-clip-all`.
- **Explicitly** — reference the skill by name, e.g. *"use codebase-exploration before you touch this."*

---

## Author

**Joe Cook** — Cook Coding. Full-stack development across Python, Next.js, React, Node.js, and Azure, with a focus on AI-powered tools, scalable SaaS, and technology for churches and nonprofits.

- 🌐 [cookcoding.com](https://www.cookcoding.com/)
- 💼 [linkedin.com/in/cookcoding](https://www.linkedin.com/in/cookcoding/)
- 🐙 [github.com/joecookcoding](https://github.com/joecookcoding)
- 𝕏 [@thejoecook](https://x.com/thejoecook)

---

## Contributing

Each skill is independent — open an issue or PR against the relevant folder. New skills should follow the layout above and include a clear, trigger-rich `SKILL.md` description plus `evals/` cases that prove the skill fires when it should.
