# Skill: Responsive Polish

## Purpose

Finalize the hero redesign so it feels polished, accessible, and intentional across desktop, tablet, and mobile.

This skill prevents the redesign from looking good only on desktop while collapsing into a generic or cluttered mobile layout.

## Primary Job

Create final implementation guidance for spacing, responsive behavior, accessibility, image treatment, typography scaling, touch targets, and polish.

## When To Use

Use this skill after:

- diagnosis is complete
- message hierarchy is finalized
- visual composition is planned
- CTA conversion path is defined

Use it before sending the design to a code agent, designer, or frontend developer.

## Required Inputs

- Final hero copy
- Visual composition plan
- CTA conversion plan
- Brand colors or design tokens, if available
- Target framework, if applicable
- Accessibility requirements, if applicable

## Core Prompt

```text
Act like a senior frontend design systems reviewer and responsive web designer.

Review this hero redesign plan and turn it into final responsive implementation guidance.

Inputs:
Hero copy:
[PASTE FINAL HERO COPY]

Visual composition plan:
[PASTE VISUAL COMPOSITION PLAN]

CTA conversion plan:
[PASTE CTA CONVERSION PLAN]

Your job:
- Make the desktop, tablet, and mobile versions feel intentional.
- Preserve hierarchy on smaller screens.
- Keep the portrait visually important on mobile.
- Ensure the CTA remains obvious and easy to tap.
- Improve accessibility, contrast, spacing, and typography scaling.
- Identify what should simplify on mobile.
- Identify what should not be removed because it supports conversion.
- Provide practical implementation notes for a code/design agent.
```

## Output Format

```text
# Responsive Polish Plan

## Final Design Intent
[One short paragraph describing the intended final experience.]

## Desktop Guidance
- Layout:
- Max width:
- Spacing:
- Portrait treatment:
- CTA placement:
- Proof placement:

## Tablet Guidance
- Layout:
- Spacing changes:
- Image behavior:
- CTA behavior:

## Mobile Guidance
- Stack order:
- Headline sizing:
- Portrait placement:
- CTA/form layout:
- Proof placement:
- Decorative elements to simplify:

## Accessibility Requirements
- Contrast:
- Touch targets:
- Form labels:
- Focus states:
- Image alt text:
- Motion/animation:

## Typography Scaling
- Eyebrow:
- Headline desktop:
- Headline mobile:
- Body copy:
- CTA:
- Proof text:

## Spacing System
- Section padding desktop:
- Section padding mobile:
- Gap between headline and copy:
- Gap between copy and CTA:
- Gap between CTA and proof:

## Visual Polish Notes
- [Note]
- [Note]
- [Note]

## Code Agent Instructions
[Clear implementation instructions for a frontend agent.]

## Final QA Checklist
- [ ] Value is clear within 3 seconds.
- [ ] CTA is visible without searching.
- [ ] Portrait remains important on mobile.
- [ ] Form is accessible and easy to use.
- [ ] Decorative elements do not hurt readability.
- [ ] Proof remains close to the CTA.
- [ ] Layout feels custom, not generic.
```

## Responsive Rules

Use these principles:

- Mobile should not simply be a collapsed desktop layout.
- Preserve the emotional anchor of the portrait.
- Keep the CTA above or near the first viewport when possible.
- Proof should remain visible but compact.
- Decorative background elements should reduce on mobile.
- Do not let the hero become text-only unless the brand requires it.
- Maintain comfortable spacing and touch targets.

## Accessibility Rules

- Use real form labels or accessible labels.
- Maintain sufficient color contrast.
- Ensure buttons and inputs meet touch target expectations.
- Avoid placing important text over busy image areas.
- Do not rely only on color to communicate emphasis.
- Provide meaningful alt text for the portrait.
- Keep animation subtle and non-essential.

## Quality Checklist

Before completing this skill, confirm:

- [ ] Desktop version feels premium and structured.
- [ ] Tablet version does not feel cramped.
- [ ] Mobile version still feels designed.
- [ ] CTA remains prominent.
- [ ] Social proof remains near the CTA.
- [ ] Typography scales cleanly.
- [ ] Accessibility concerns are addressed.
- [ ] Decorative elements support the hierarchy.

## Red Flags

Avoid:

- Letting the portrait disappear on mobile.
- Shrinking text until it loses impact.
- Keeping oversized decorative shapes that hurt mobile readability.
- Moving proof too far from the CTA.
- Making form fields too small.
- Creating a desktop-only design.

## Final Handoff

The output from this skill should be ready to hand to:

- a frontend developer
- a design agent
- a Figma designer
- a code generation tool
- a site builder such as Lovable, Bolt, Claude Code, or Cursor
