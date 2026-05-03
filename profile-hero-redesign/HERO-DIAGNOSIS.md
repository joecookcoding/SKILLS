---
name: hero-diagnosis
description: Diagnose a profile, personal-brand, coach, speaker, author, creator, consultant, counselor, or service-provider hero section to find why it feels generic, flat, forgettable, or low-converting before any redesign. Use whenever the user says "audit my hero", "review my landing page hero", "my hero feels generic / boring / flat / template-y", "headline is weak", "CTA is invisible", "portrait looks pasted in", "no focal point", "evaluate my above-the-fold", or shares a screenshot of a homepage hero and asks what's wrong. Step 1 of the profile-hero-redesign workflow — produces the diagnosis that feeds message-hierarchy. Always invoke this before jumping to layout or visual fixes when the user shows a hero they're unhappy with.
---

# Skill: Hero Diagnosis

## Purpose

Evaluate a profile or personal-brand hero section and identify why it feels generic, flat, forgettable, or low-converting.

This skill does not redesign the page yet. It diagnoses the current layout, message, hierarchy, focal point, and conversion path so the next skills know what to improve.

## Primary Job

Find what is weak, what is working, what should be preserved, and what must change before redesigning.

## When To Use

Use this skill when a homepage or profile hero:

- looks clean but lacks energy
- feels generic or template-like
- has no strong focal point
- has a weak or vague headline
- has a CTA that is easy to miss
- has a portrait that feels placed rather than integrated
- lacks trust signals or proof
- does not clearly communicate why the visitor should stay

## Required Inputs

Provide as many as possible:

- Screenshot or image of the current hero
- Current headline
- Current subheadline/body copy
- Current CTA text
- Target customer or audience
- Business/person type, such as coach, speaker, author, creator, consultant, counselor, church leader, nonprofit leader, educator
- Desired action, such as subscribe, book a call, download a guide, join a waitlist, apply, donate, contact
- Available proof, such as subscribers, testimonials, client count, media logos, credentials, years of experience, audience size

## Core Prompt

```text
Act like a senior conversion designer and brand strategist.

Analyze this personal-brand or profile hero section. The current design may look clean, but I want to know whether it clearly communicates value, creates a strong focal point, builds trust, and guides the user toward action.

Diagnose the hero across these areas:
1. Message clarity
2. Visual hierarchy
3. Focal point
4. Portrait/image usage
5. CTA visibility
6. Trust and proof
7. Layout rhythm and spacing
8. Emotional impression
9. Mobile-readiness concerns
10. Conversion weaknesses

For each area, explain:
- What is working
- What is weak
- Why it matters
- What should be improved in the redesign

Do not redesign the full page yet. Focus only on diagnosis and clear recommendations.
```

## Output Format

Return the diagnosis in this structure:

```text
# Hero Diagnosis

## Overall Read
[Short summary of the current hero's main issue.]

## What Is Working
- [Strength 1]
- [Strength 2]
- [Strength 3]

## Main Problems
### 1. Message Clarity
- Issue:
- Why it matters:
- Recommended fix:

### 2. Visual Hierarchy
- Issue:
- Why it matters:
- Recommended fix:

### 3. Focal Point
- Issue:
- Why it matters:
- Recommended fix:

### 4. CTA and Conversion Path
- Issue:
- Why it matters:
- Recommended fix:

### 5. Trust and Proof
- Issue:
- Why it matters:
- Recommended fix:

## Keep / Change / Remove
### Keep
- [What should remain]

### Change
- [What needs improvement]

### Remove
- [What creates clutter, confusion, or weakness]

## Redesign Priorities
1. [Most important priority]
2. [Second priority]
3. [Third priority]
4. [Fourth priority]
5. [Fifth priority]
```

## Decision Rules

A hero needs redesign work if any of these are true:

- The headline could apply to hundreds of similar brands.
- The CTA is not visually obvious within 3 seconds.
- The user cannot tell what the person offers or why it matters.
- The portrait does not contribute to the emotional impression.
- There is no proof near the CTA.
- The page is clean but has no clear visual direction.
- The mobile version likely becomes a generic stack.

## Quality Checklist

Before completing this skill, confirm:

- [ ] The main weakness is clearly identified.
- [ ] The diagnosis separates message issues from visual issues.
- [ ] The recommendations are actionable.
- [ ] The strongest existing elements are preserved.
- [ ] The output gives the next skill enough context to rewrite the message.

## Red Flags

Avoid:

- Saying only “make it more modern” without explaining why.
- Jumping straight into design before diagnosing the page.
- Treating decoration as the primary fix.
- Ignoring the CTA.
- Ignoring the difference between clean and compelling.

## Handoff To Next Skill

Pass the following to **Message Hierarchy**:

- Current headline and copy
- Main diagnosis
- Target audience
- Desired action
- Available proof
- Top 3 redesign priorities
