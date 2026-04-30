# Writing Skill Descriptions That Trigger Accurately

The description field in SKILL.md frontmatter is the ONLY mechanism that determines whether Claude auto-invokes a skill on user intent. A vague description = a skill that never fires. A precise description with explicit keyword triggers = a skill that fires reliably when needed.

## The anatomy of a good description

```yaml
description: [One-sentence purpose]. Use when [specific user contexts — what phrases, what tasks]. Triggers on [explicit keyword list]. [Any scope/exclusion notes].
```

### Structure

1. **Purpose sentence** — what the skill does, in plain language. One sentence.
2. **"Use when" clause** — the situational triggers. What tasks, what flows, what questions.
3. **"Triggers on" clause** — the explicit keyword list. The user's actual words.
4. **Scope notes** (optional) — limits, exclusions, or "also use when…" additions.

### Character budget

- Total cap per skill: **1,536 characters**
- Average good description: 400–700 chars
- Don't pad; don't abbreviate to the point of vagueness. Invest every character in matching accuracy.

## Examples

### Bad — too vague

```yaml
description: Design system guidance.
```

Why it fails: no verbs, no user phrasings, no keywords. Claude won't associate this with "what color should I use?" or "fix dark mode contrast."

### Bad — too narrow

```yaml
description: Use this skill when the user says "apply the design system tokens."
```

Why it fails: no one says that. Users say "what color should I use", "fix dark mode", "make this look better", "what's the radius for cards". None of those match.

### Good

```yaml
description: Apply the @volusia design system when choosing colors, dark mode tokens, atmospheres, typography, radius, squircles, hero backgrounds, tones, badges, buttons, or card styles. Use when writing or editing any JSX/TSX with visible UI, picking CSS classes, fixing dark mode contrast issues, reviewing against design standards, or asking "what color should I use for X?". Triggers on "color", "dark mode", "atmosphere", "token", "radius", "squircle", "hero", "badge", "button variant", "tone", "primary/info/accent", "--vc-*", "bg-*", "text-*", or when polishing a page.
```

Why it works:
- Purpose is clear in the first sentence
- "Use when" covers multiple scenarios in user's own words
- "Triggers on" is a comprehensive keyword list — CSS variable names, common terms, and tool-specific slang all included
- Scope is bounded (design, not accessibility or forms)

## Keyword mining

Before writing the description, list everything a user might say to invoke the skill. Cast a wide net:

- **Literal terms** — the thing's technical name (`useMemo`, `zodResolver`, `TipTap`)
- **Colloquial phrasings** — how users talk when they're not being formal ("fix the thing where", "make X work")
- **Task contexts** — "writing a form", "debugging styles", "adding a route"
- **Tool/library names** — the framework or lib involved
- **Verbs that implicate the skill** — "refactor", "migrate", "polish", "audit"
- **File types that usually need the skill** — `.tsx`, `.css`, `.sql`, `.yaml`

Then write "Triggers on" as a comma-separated list of the highest-signal items.

## The "pushy" principle

Claude tends to **under-trigger** skills — erring on the side of "I can handle this myself." Counteract this by being explicit in the description:

- Instead of: "This skill handles X."
- Write: "Use this skill whenever the user mentions X, Y, Z, even if they don't explicitly ask for it."

For skills that are your primary way of handling a domain, say so:

```yaml
description: ...This is the primary way to approach [domain] tasks. Invoke it whenever the user asks about [keywords], even in passing.
```

## Specificity wins — generic descriptions lose

Compare:

```yaml
# Weak
description: Helps with React components.

# Strong
description: Apply React 19 + React Compiler patterns when writing, reviewing, or refactoring components, hooks, refs, context providers, or memoization. Use when asked to write a component, fix a memoization issue, migrate forwardRef, convert Context.Provider, add useRef, remove useMemo/useCallback/React.memo, use the new `use()` API for conditional reads, or use `startTransition`. Triggers on "useMemo", "useCallback", "React.memo", "forwardRef", "Context.Provider", "useRef", "startTransition", "use()", or any edit to a .tsx file with hooks.
```

The strong version enumerates the specific user actions that implicate it. Claude matches intent against this list and fires the skill.

## Testing descriptions

After writing a description:

1. Write 5–10 realistic user prompts that SHOULD trigger it
2. Write 5–10 prompts that SHOULD NOT trigger it (adjacent domains)
3. Mentally score each: does the description obviously match the positive cases? Does it NOT match the negative cases?
4. Adjust until both sides are clean

For high-stakes skills, use the description optimization loop from skill-creator (runs 3x per query, iterates 5 times, picks best-scoring version on held-out test set).

## Scope/exclusion phrases

If your skill overlaps with another, disambiguate:

- `Use for X. SKIP when the user is really asking about Y (use /other-skill for that).`
- `This covers document accessibility. For component-level a11y, use /web-design-guidelines instead.`

## When NOT to trigger

Some skills should only run when the user explicitly invokes them via `/skill-name`. For those, add `disable-model-invocation: true` to the frontmatter. The description still exists as documentation but costs zero tokens at startup.

Use this sparingly — most skills benefit from auto-triggering.

## A template to start from

```yaml
---
name: your-skill-name
description: [One sentence: what the skill does]. Use when [scenarios, tasks, questions — in user's words, not yours]. Triggers on "[keyword1]", "[keyword2]", "[keyword3]", ..., or when [contextual trigger like 'editing files under src/X/']. [Optional: scope limits or 'also use for...' additions].
---
```

Fill it in. Re-read it. Ask yourself: "If I were Claude, and a user said [specific thing], would I see this description and know to fire?" If no, rewrite.
