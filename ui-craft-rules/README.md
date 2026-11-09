# ui-craft-rules

An Agent Skill that gives an AI assistant 39 checkable UI/UX rules and a 22-point review list
of the tells AI-generated interfaces leave behind: tab bars with action buttons, dropdowns for
three options, "Are you sure?" dialogs, light cards in dark mode, muddy gradients, mismatched
corner radii, raw hex values, and more.

Use it when an assistant builds or reviews screens and components in code (React, HTML/CSS,
SwiftUI, Flutter) or in a design tool (Figma, Figma Make, Claude Design), or when it sets up
design tokens and component naming.

## What's inside

```
ui-craft-rules/
├── SKILL.md              # when to use, how to apply, the review list, and a one-line rule index
└── references/
    ├── hierarchy.md      # HIE-1–9: hierarchy, alignment, grouping, choice count
    ├── components.md     # CMP-1–9: tab bars, dropdowns, dialogs, menus, buttons, empty states
    ├── visual.md         # VIS-1–7: radius, contrast, gradients, type, colour, dark mode
    ├── motion.md         # MOT-1–4: transitions, staging, easing
    ├── tokens.md         # TOK-1–5: token tiers, token names, modes, component names, props
    └── ai-readiness.md   # SYS-1–5: layer names, file structure, token linting, agent docs
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
tokens". The skill fires on its own. You can also name it: "use ui-craft-rules to review this
modal".

When it reviews, it reports findings as `RULE-ID: what is wrong → the fix`.

## Credits

Distilled from the public UI design reels of Memorisely (memorisely.com), April–November 2026.
Packaged by Joe Cook ([cookcoding.com](https://www.cookcoding.com/)).
