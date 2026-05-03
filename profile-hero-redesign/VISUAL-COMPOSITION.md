---
name: visual-composition
description: Design the elevated visual composition for a profile or personal-brand hero — focal point, portrait integration, background depth (gradients, arcs, glows, shapes), typography contrast, scan path, and desktop+mobile layout. Use whenever the user says "redesign my hero layout", "make my hero more premium", "the portrait looks isolated / pasted in", "add depth to my hero", "make the hero feel modern / editorial / elevated", "split hero", "overlap portrait", "background shapes", "visual flow", "newsletter hero design", or asks for a hero that feels less generic and more conversion-driven. Step 3 of profile-hero-redesign — pairs final hero copy with a layout plan that cta-conversion and responsive-polish can execute. Trigger this aggressively any time hero VISUAL design (not just copy) is on the table.
---

# Skill: Visual Composition

## Purpose

Turn the improved hero copy into a stronger visual composition with better focal point, portrait integration, background depth, typography contrast, and directional flow.

This skill creates the design direction for the hero.

## Primary Job

Create a layout that feels intentional, modern, premium, and conversion-driven without becoming cluttered.

## When To Use

Use this skill after the message hierarchy has been defined.

It is especially useful when:

- the portrait feels isolated or pasted into a box
- the page lacks movement or visual flow
- the design is clean but too flat
- the CTA does not feel connected to the message
- the layout lacks differentiation
- the design needs to feel more premium and polished

## Required Inputs

- Final hero copy block from Skill 02
- Portrait/profile image
- Brand colors, if available
- Desired tone
- CTA and proof copy
- Reference style, if available
- Existing layout screenshot, if available

## Core Prompt

```text
Act like a world-class web designer specializing in personal-brand hero sections.

Create a visual composition plan for this hero section using the copy below:
[PASTE FINAL HERO COPY]

Design goal:
Transform a clean but generic layout into a more focused, modern, premium, and conversion-driven hero.

Requirements:
- Use the portrait as the emotional and visual anchor.
- Create a strong scan path from role label to headline to supporting copy to CTA to proof.
- Emphasize only one key word or phrase in the headline.
- Add background depth through soft gradients, curved shapes, large arcs, abstract forms, subtle patterns, or glow effects.
- Integrate the portrait into the design instead of placing it in a disconnected rectangle.
- Keep the design clean and spacious.
- Make the CTA area feel like a clear conversion unit.
- Add proof near the CTA without making the layout noisy.
- Include desktop and mobile composition guidance.

Return a practical design plan that a designer or code agent can implement.
```

## Output Format

```text
# Visual Composition Plan

## Design Direction
[Short description of the desired visual feel.]

## Layout Structure
### Desktop
- [Describe columns, alignment, spacing, and order]

### Mobile
- [Describe stacking order and preserved focal points]

## Focal Point Strategy
[Explain what the eye should notice first and why.]

## Portrait Treatment
- Size:
- Crop:
- Background integration:
- Shape treatment:
- Overlap/layering:

## Typography Treatment
- Eyebrow:
- Headline:
- Highlighted word:
- Body copy:
- Proof/testimonial:

## Background and Depth
- Base background:
- Accent shape:
- Gradient/glow:
- Decorative details:
- What to avoid:

## CTA/Form Placement
[Explain where the CTA belongs and how it should be visually grouped.]

## Social Proof Placement
[Explain where proof should appear and how prominent it should be.]

## Visual Hierarchy Order
1. [First thing user sees]
2. [Second]
3. [Third]
4. [Fourth]
5. [Fifth]

## Implementation Notes
- [Practical note]
- [Practical note]
- [Practical note]
```

## Design Patterns To Use

Choose from these repeatable patterns:

### Pattern A: Split Hero With Integrated Portrait
- Left side: copy, CTA, proof
- Right side: large portrait
- Background shape behind portrait
- CTA form grouped under copy

### Pattern B: Editorial Overlap Hero
- Large headline overlaps slightly with image area
- Portrait partially breaks out of a soft frame
- Decorative word or shape behind the subject

### Pattern C: Newsletter Conversion Hero
- Strong headline and form on one side
- Portrait and proof on the other
- Subscriber count and testimonial directly below form

### Pattern D: Premium Coach/Speaker Hero
- Role label at top
- Large confident headline
- Portrait in circular/arched shape
- Soft gradient background and testimonial quote

## Quality Checklist

Before completing this skill, confirm:

- [ ] The portrait is treated as a design anchor.
- [ ] The layout has one clear focal point.
- [ ] The headline has one emphasized word or phrase.
- [ ] The CTA is visually connected to the message.
- [ ] Proof is close enough to support conversion.
- [ ] Background effects add depth without noise.
- [ ] Mobile layout preserves the design intent.

## Red Flags

Avoid:

- Using too many decorative elements.
- Making the portrait too small.
- Adding background details that compete with the message.
- Centering everything by default.
- Creating a generic two-column layout with no depth.
- Making the mobile layout feel like an afterthought.

## Handoff To Next Skill

Pass the following to **CTA Conversion**:

- Final hero copy
- Visual composition plan
- CTA location and style
- Proof placement
- Desired action
