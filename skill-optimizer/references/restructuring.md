# Restructuring Skills: When and How to Split

The skill *folder* is a progressive-disclosure machine: metadata (always loaded) → SKILL.md body (loaded on trigger) → bundled files (loaded only when pointed to). Restructuring moves content to the cheapest layer where it still does its job.

## Thresholds

| Body size | Action |
|---|---|
| < ~150 lines | Leave the structure alone. Fix content issues in place. |
| 150–400 lines | Reorganize in place: principle first, gotchas prominent, decision trees near the top. Split only if clear situational blocks exist. |
| > ~400 lines | Split. At this size the highest-value content (usually gotchas) is buried, and every invocation pays for sections most runs never need. |

## When NOT to split (the inverse failure)

- **Small utility skills**, especially cheap model-pinned ones (e.g., a Haiku-pinned commit-message skill): each `references/` file costs a Read round-trip at invocation. Splitting a 115-line skill saves nothing and adds latency.
- **Reference skills whose entire content is the payload** — if every invocation needs ~all of it, splitting just adds hops.
- **Don't split to satisfy the rubric.** Split because identifiable content blocks are *situational* (needed in some runs, dead weight in others).

## How to split

1. **Classify each section**: every-run (stays in SKILL.md) vs situational (moves to `references/`) vs output-material (moves to `assets/`) vs deterministic-mechanical (becomes `scripts/`).
2. **Move, don't rewrite.** The wording was earned through real use; silent rewrites during relocation lose corrections baked into the text. Restructure in a separate pass from rewording.
3. **Add an explicit conditional pointer for every moved block**: "If the backend shipped on a different cadence, read `references/edge-cases.md`." The blog's model: SKILL.md says *if a job is pending, reference stuck-jobs.md*. A bundled file with no pointer is invisible — an orphan.
4. **Keep in SKILL.md**: the core principle (the "why" that shapes judgment), the workflow overview, the gotchas *index* (one line each, pointing into the details file if long), and the when-NOT-to-use section.
5. **Re-run the inventory script** afterward and confirm: body line count down, no orphaned files (pointer count covers every bundled file), description unchanged.

## Ordering within SKILL.md (cheap wins without splitting)

- **Principle before procedure** — open with the constraint that makes the skill necessary ("TypeScript types are erased at runtime", "the Status: header is not a delivery signal"). A model that understands the why executes the steps better and adapts when they don't fit.
- **Decision trees and rule-of-thumb gates near the top** — they route the reader; burying them at line 350 defeats their purpose.
- **Gotchas visible, not appended** — if it's the highest-signal content, it shouldn't be the last thing loaded attention reaches.
