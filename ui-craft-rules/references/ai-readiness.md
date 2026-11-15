# Design-system AI readiness (SYS)

Rules that make a design system or design file legible to AI agents.

Each rule: **When** to apply it, **Why** it matters, then **Check**, what to verify in a design
or in code.

**SYS-1 Name every layer and frame semantically.**
When: preparing a Figma file for handoff or for an AI tool to read.
Check: no default names (`Frame 4832`, `Rectangle 12`) in shipped files; names describe role (`User Info`, `Profile Image`, `Bottom Bar`). Figma's AI "Rename layers" is an acceptable first pass.

**SYS-2 Use a standard file structure.**
When: creating or reorganising a design file or project.
Why: it makes handoffs, reviews, and coming back six months later easier, and AI tools working in the file (Figma MCP, Claude Design) read what's there, so a messy file means messy output.
Check: the file is named `Product - Feature - Version` and carries a status from a fixed set (Live, Ready to build, In progress, Backlog, Archived); projects are sorted by status. Pages are grouped and ordered by importance:
- Cover (a visual thumbnail), Overview, Metrics (success measures)
- Screens, Components, Prototype, Motion, each marked "ready for dev" when it is
- Iterations, Flows, Research (the evidence behind decisions)
- Playground, Inspiration, Archived

**SYS-3 Make wrong tokens fail the build.**
When: a codebase has tokens, and especially when AI-generated code drifts off-brand.
Why: Polar's team saw AI drift off-brand (wrong greys, spacing, dark mode) until invalid tokens stopped compiling.
Check: tokens are exported as typed constants or a closed union, a lint rule bans raw colour and spacing values in components, and CI fails on unknown token names.

**SYS-4 Give agents a machine-readable path into the system.**
When: agents build UI against a design system.
Why: without one, agents hallucinate component names, hard-code hex, and pick the wrong tokens. Atlassian reported 4.9% more accurate code, 34% faster tasks, 16% fewer tokens, and 26% fewer tool calls after restructuring its docs and shipping an MCP server. Only 17% of design-system teams rate their docs as AI-ready (Zeroheight, 2026).
Check: structured token files, per-component docs (props, usage, do/don't), and either an MCP server or a skill the agent loads before building.
Reference systems worth studying: Atlassian, Adobe Spectrum, IBM Carbon, Material Design 3, Polar (Orbit), Meta's Astryx (public in 2026 with a full MCP server), GOV.UK, Government of Canada, and New York State.

**SYS-5 Every value comes from a scale.**
When: reviewing any design file or stylesheet before handoff.
Why: fractional and one-off values are the signature of a file nobody can hand over. Agents copy whatever values they find.
Check: spacing, padding, gap, and radius are whole numbers from the spacing and radius scales (no 13.5, 6.6, 10.7, 15.3). Every colour in use maps to a named token; a file or stylesheet with dozens of unnamed hex values fails. Frames and layers carry real names (SYS-1).

**SYS-6 Every interactive component documents its interaction contract.**
When: adding a component to a design system, documenting one for agents, or reviewing a component spec before build.
Why: principles left as general advice get applied unevenly. Written into each component, they become a standard that can be checked in review and tested in code.
Check: each interactive component's doc or spec states its target size (INT-2), keyboard behaviour and focus appearance, loading or pending state (INT-4), error state (MOT-8, INT-6), motion (duration and easing tokens, MOT-4, MOT-5), and reduced-motion behaviour (MOT-6). A missing entry is a gap to fill before the component ships, not a default to guess.
