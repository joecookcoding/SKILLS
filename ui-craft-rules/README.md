# ui-craft-rules

An Agent Skill that gives an AI assistant 58 checkable UI/UX rules and a 31-point review list
of the tells AI-generated interfaces leave behind: tab bars with action buttons, dropdowns for
three options, "Are you sure?" dialogs, light cards in dark mode, muddy gradients, mismatched
corner radii, raw hex values, icons sized by eye, tiny icon buttons, `transition: all`, placeholder-only labels,
and more.

Every rule opens with a **When** line saying when it applies. The 12 principles of animation
and the usability laws (Fitts, Hick, Miller, Doherty, Postel, Jakob, frequency of use) are
included as rules, and `SKILL.md` has a table that finds each one by name.
Where a short video teaches a rule, the rule links it on a **Watch** line.

Use it when an assistant builds or reviews screens and components in code (React, HTML/CSS,
SwiftUI, Flutter) or in a design tool (Figma, Figma Make, Claude Design), or when it sets up
design tokens and component naming.

## What's inside

```
ui-craft-rules/
├── SKILL.md              # how to apply, the review list, a principle finder, and a one-line rule index
├── references/
│   ├── hierarchy.md      # HIE-1–9: hierarchy, alignment, grouping, choice count (Hick's Law)
│   ├── components.md     # CMP-1–9: tab bars, dropdowns, dialogs, menus, buttons, empty states
│   ├── interaction.md    # INT-1–7: Fitts, hit areas, Jakob, Doherty, Miller, Postel, frequency of use
│   ├── visual.md         # VIS-1–9: radius, contrast, gradients, type, colour, dark mode, depth, icon size
│   ├── motion.md         # MOT-1–13: the animation principles: transitions, timing, easing, feedback, reduced motion
│   ├── tokens.md         # TOK-1–5: token tiers, token names, modes, component names, props
│   ├── ai-readiness.md   # SYS-1–6: layer names, file structure, token linting, agent docs, component contracts
│   └── enhancing.md      # improving pages that already ship: audit, plan, before and after
├── scripts/
│   └── shot.mjs          # before-and-after screenshots with headless Chrome (Node 22+, no packages)
└── evals/
    └── evals.json        # prompts and assertions for testing the skill
```

The assistant loads `SKILL.md` when a UI task comes up and reads a reference file only when it
needs that area.

## Install

The skill is the `ui-craft-rules` folder. If you received `ui-craft-rules.zip`, it contains
that folder.

- **Claude apps (claude.ai, desktop):** upload `ui-craft-rules.zip` in the Skills section of
  Settings.
- **Claude Code:** unzip into `~/.claude/skills/` for every project, or into a project's
  `.claude/skills/` for that project only. You should end up with
  `~/.claude/skills/ui-craft-rules/SKILL.md`.
- **Other agents that read `SKILL.md` folders:** unzip into that tool's skills directory.

## Use

Just ask for UI work: "build a settings screen", "review this checkout page", "set up dark mode
tokens", "add press feedback to these buttons", "apply Fitts's Law to this toolbar". The skill
fires on its own. You can also name it: "use ui-craft-rules to review this
modal".

When it reviews, it reports findings as `RULE-ID: what is wrong → the fix`.

Ask it to "enhance this site with ui-craft-rules" and it audits the pages, gives a plan, makes
the changes with the project's own components, shows before and after screenshots, and writes
the rules into the project's design doc.

## Credits

Distilled from the public UI design reels of Memorisely (memorisely.com), April–November 2026.
The animation principles and usability laws follow a 20-principle summary by Charles Liu, built
on Thomas and Johnston's *The Illusion of Life* (1981) and Laws of UX (lawsofux.com).
Packaged by Joe Cook ([cookcoding.com](https://www.cookcoding.com/)).
