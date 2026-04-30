# Content Categorization Framework

How to decide where a given chunk of CLAUDE.md content should live after optimization. Apply this to each section, paragraph, and rule.

## The four buckets

### 1. Always-true fact → stays in root CLAUDE.md

A fact is information Claude needs **regardless of what task is being performed**. Examples:

- "This project uses PowerShell, not bash"
- "The build command is `npm run build`"
- "Types are auto-generated from OpenAPI — never define manually"
- "Never commit; user manages git"
- "Minimum 44px touch targets"

**Test:** Close your eyes. Pick a random file in the repo. Would a developer need to know this rule to safely edit that file? If yes for most files → fact.

**Signal:** The rule applies universally. Violations are possible anywhere. No directory is exempt.

### 2. Procedure / reference → skill

A procedure is a multi-step workflow or a lookup table that's only relevant for specific tasks. Examples:

- "How to look up Agenda API endpoints" → `agenda-api-reference` skill
- "ADA compliance checklists for documents/PDFs/maps" → `ada-compliance` skill
- "Design system token catalog and atmosphere rules" → `design-system-tokens` skill
- "React 19 + Compiler migration patterns" → `react-19-patterns` skill
- "Form building with react-hook-form + Zod" → `forms-validation` skill

**Test:** Is this "how to do X" or "reference material for X"? If yes, and if most sessions DON'T need X, it's a skill candidate.

**Signal:** The content is long (>20 lines), has structured procedures or lookup tables, or references external resources you search through.

**Write the skill's description with explicit trigger keywords.** A vague description is useless — see `skill-writing.md`.

### 3. Area-specific rule → nested AGENTS.md + sibling CLAUDE.md

An area rule applies only when working in a specific subtree of the repo. Examples:

- "Query hooks must use direct imports from `@api/queries/[domain]/...`" → `src/api/queries/AGENTS.md`
- "Pages must use `React.lazy()` + `routePrefetch.ts` entries" → `src/routes/AGENTS.md` or `src/pages/AGENTS.md`
- "Status codes live in generated constants — don't hardcode" → `src/constants/AGENTS.md`
- "Component directory pattern for files >300 lines" → `src/components/AGENTS.md`

**Test:** Ask "would a developer editing `src/X/foo.ts` need this rule?" If yes, and "would a developer editing `src/Y/bar.ts` need this rule?" is no → area-specific.

**Signal:** The rule mentions specific file patterns, directory names, or module boundaries.

### 4. Dead / stale → delete

Content that describes patterns we no longer use, or references files that no longer exist. Examples:

- Migration instructions for a migration that completed 6 months ago
- Pointers to `.claude/instructions/foo.md` where `foo.md` was deleted
- Rules about "the old auth system" after the auth rewrite shipped
- Step-by-step guides to workflows that are now automated

**Test:** Search the codebase for the pattern described. Does any current code follow it? Does any referenced file exist?

**Signal:** Age, deleted-file references, words like "legacy" / "old" / "deprecated" without a migration path.

## Decision tree

```
Is this content a fact Claude needs in every session?
├── YES → bucket 1 (root CLAUDE.md)
└── NO → Is this describing how to do X or reference material for X?
        ├── YES → Is X invoked by intent keywords?
        │       ├── YES → bucket 2 (skill)
        │       └── NO (only relevant in specific dirs) → bucket 3 (AGENTS.md)
        └── NO → Is this still accurate about the current codebase?
                ├── YES → keep somewhere relevant (maybe /docs/)
                └── NO → bucket 4 (delete)
```

## Common miscategorizations

**Over-categorizing as "fact":** The original 478-line CLAUDE.md case-study had 33 numbered "critical rules" — but only ~12 were truly always-relevant. The rest were area-specific or reference material misfiled as universal.

**Under-using skills:** Many repos put all API reference material directly in CLAUDE.md. This is always wrong — API references are the textbook case for skills. Tight description matches when the user asks about endpoints; zero cost otherwise.

**Skipping AGENTS.md for "small" rules:** Even a single rule like "in this directory, use `client.query(...)` instead of raw SQL" should live in the directory's AGENTS.md, not in root CLAUDE.md. The principle is directory locality, not size.

## Handling edge cases

### "This rule SOMETIMES applies repo-wide, but mostly only in src/X/"

Put the rule in `src/X/AGENTS.md`. If there are exceptions elsewhere, add a one-liner in root CLAUDE.md: "For X, see src/X/AGENTS.md." Rare violations are easier to catch in review than bloating CLAUDE.md for 80% unaffected work.

### "This procedure is invoked via slash command"

Slash commands (`.claude/commands/*.md`) and skills are different mechanisms, but overlap heavily. Prefer skills for content — they have structured frontmatter and richer discovery. Slash commands can remain as thin entry points.

### "The user explicitly said 'always do X'"

"Always" is user phrasing, not necessarily a universal rule. Read it literally: do they mean "always in UI components" or "always across all code"? Put it at the scope they meant. If genuinely universal, it's a fact.

### "Content spans multiple scopes"

Split it. The "Design System" section might have:
- Universal facts (use `--vc-*` tokens, never raw colors) → root CLAUDE.md as a 1-liner
- Deep reference (token catalog, atmospheres) → `design-system-tokens` skill
- Component-specific conventions (badges, buttons) → `src/components/AGENTS.md` or per-component doc

## What to do with the output of categorization

For each existing section, note:
1. Target bucket (1, 2, 3, or 4)
2. Target file path (if bucket 2 or 3)
3. Whether content needs rewording for the new home (e.g., removing "in this repo" if moving to a skill that works across repos)

Put this in the plan file before executing. This is the spine of the migration.
