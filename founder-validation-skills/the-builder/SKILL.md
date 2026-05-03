# Skill: The Builder

## Purpose

Turn the finalized copy into a live, mobile-optimized, one-page website.

This skill creates a focused landing page for a lead magnet. The goal is proof, not perfection. It should look strong enough to test demand, capture emails, and communicate the offer clearly.

## Primary Job

Build a visually strong one-page lead magnet site using the copy from **The Copywriter**.

The page should be:

- Clear
- Mobile-optimized
- Fast to ship
- Visually memorable
- Conversion-focused
- Easy to edit
- Accessible

## When To Use This Skill

Use this skill after **The Copywriter** has produced landing page copy.

Use it when you need:

- A one-page website
- A lead magnet landing page
- A fast prototype
- A mobile-first page
- A clean email capture flow
- A design based on a reference site or image

## Required Inputs

```text
Lead magnet title:
Target customer:
Headline:
Subheadline:
Benefit bullets:
CTA:
Email capture destination or tool:
Brand style:
Reference site or image:
Tech stack:
Deployment target:
```

## Core Prompt

```text
Build me a visually stunning one-page site for [insert lead magnet].

Follow the design style of [paste a link, screenshot, or description of a site you love].

Use this copy:

Headline:
[paste headline]

Subheadline:
[paste subheadline]

Bullets:
[paste bullets]

CTA:
[paste CTA]

Requirements:
- Optimize for mobile first.
- Add a clean email capture form.
- Make the CTA impossible to miss.
- Use strong visual hierarchy.
- Keep the page focused on the lead magnet.
- Avoid unnecessary sections.
- Make the design feel polished but fast to ship.
- Use accessible contrast, labels, focus states, and touch-friendly controls.
- Include responsive spacing and typography.
- Keep the page easy to update.

The goal is not a 12-page funnel. The goal is a one-page proof asset that can capture real leads.
```

## Recommended Page Structure

```text
1. Hero section
   - Eyebrow
   - Headline
   - Subheadline
   - Primary CTA or email form
   - Supporting visual or mockup

2. Pain section
   - Short statement of the problem
   - 3 quick pain points

3. What you get
   - Clear list of what is inside the lead magnet

4. Why it works
   - Short explanation of the value
   - Optional proof or credibility line

5. Email capture section
   - Form
   - CTA button
   - Reassurance line

6. Footer
   - Simple brand/footer text
```

## Design Pattern: Elevated Profile-Inspired Landing Page

Use this style when the user references a premium profile layout or editorial personal brand design.

```text
Design direction:
- Calm, refined, elevated, warm, quietly powerful.
- Use a strong hero focal point.
- Layer typography with a large display headline and clean supporting text.
- Add subtle background shapes, gradients, glows, or decorative marks.
- Use a small editorial eyebrow line.
- Use one primary CTA.
- Add a floating card or proof element if helpful.
- Preserve white space.
- Keep visual details intentional.
- On mobile, retain the custom feel rather than collapsing into a generic centered stack.
```

## Technical Defaults

Adjust based on the user's stack.

Recommended defaults:

```text
Framework: Next.js App Router or Vite React
Styling: Tailwind CSS or project-standard design system
Components: shadcn/ui where available
Form: Email capture connected to ConvertKit, Mailchimp, Resend, Supabase, HubSpot, or a simple API route
Deployment: Vercel, Netlify, Cloudflare Pages, or existing platform
```

## Accessibility Requirements

The page must include:

- Proper semantic headings
- Label associated with the email input
- Keyboard-focusable controls
- Visible focus states
- Sufficient color contrast
- Button touch target of at least 44px
- Form error and success states
- Reduced-motion consideration if animations are used
- No essential information hidden only in images

## Output Format

When generating code, include:

```markdown
# Landing Page Build: [Lead Magnet]

## Implementation Notes

- Tech stack:
- Form handling:
- Design style:
- Key sections:
- Deployment assumptions:

## Files

Provide each file with its full file path at the top as a comment.

## QA Checklist

- Mobile layout checked
- Desktop layout checked
- CTA visible above the fold
- Email field labeled
- Form has success state
- Form has error state
- Page has a clear title and meta description
- No unused sections
```

## Builder Constraints

Do not overbuild.

Avoid:

- Large navigation menus
- Multiple unrelated CTAs
- Overly complex animations
- Placeholder copy that weakens the offer
- Huge dependency lists
- Generic template look
- Unclear form destination
- Decorative elements that reduce readability

## Quality Checklist

Before finalizing, confirm:

- The page can be launched quickly.
- The lead magnet is obvious above the fold.
- The CTA is visible and specific.
- The email capture form is simple.
- The design supports the copy instead of competing with it.
- The mobile version feels intentionally designed.
- The page is ready to hand to **The Marketer**.

## Handoff To Next Skill

Pass the live page or build summary to **The Marketer**.

Include:

```text
Landing page URL or local route:
Lead magnet title:
Target customer:
Core pain:
Primary CTA:
Email capture tool:
Current conversion goal:
Any tracking installed:
```
