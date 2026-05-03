# Skill: The Researcher

## Purpose

Find the customer pain before anything is built.

This skill helps validate whether a target customer is already experiencing urgent, repeated, emotionally charged problems. The goal is not to invent a product idea. The goal is to prove that real people are already complaining, searching, buying, hacking together workarounds, or abandoning existing solutions.

If people are not already complaining about the problem in their own words, the idea is not ready to build.

## Primary Job

Act like a world-class customer researcher who carefully checks evidence before making claims.

Find the top urgent and painful problems faced by a specific target customer, then validate each one with real-world signals.

## When To Use This Skill

Use this skill when:

- You are exploring a startup, service, SaaS, course, consulting offer, productized service, community, coaching offer, or lead magnet.
- You need to understand what customers are already struggling with.
- You want evidence before building.
- You need exact customer language for copywriting.
- You want to avoid building something people do not actually need.

Do not use this skill to brainstorm random ideas without evidence.

## Required Inputs

Ask for these inputs if they are missing:

```text
Target customer:
Industry or niche:
Geography, if relevant:
Business or consumer audience:
Known idea, if any:
Budget level of customer, if known:
Any channels to prioritize:
```

## Research Sources To Check

Prioritize sources where customers speak naturally and emotionally.

Use sources such as:

- Reddit threads and comments
- Amazon reviews
- Facebook groups and public posts, when accessible
- YouTube comments
- App store reviews
- Chrome extension reviews
- G2, Capterra, Trustpilot, Product Hunt, and similar review sites
- Forums and niche communities
- X, LinkedIn, TikTok, or Instagram comments when relevant
- Search autocomplete and “People also ask”
- Competitor testimonials and negative reviews
- Support forums and help communities
- Quora or Stack Overflow when relevant

## Research Standards

Do not treat one complaint as a market.

A problem is stronger when multiple signals appear across multiple sources.

Look for:

- Repeated complaints
- Emotional language
- Workarounds
- People asking for recommendations
- People paying for imperfect solutions
- Bad reviews of existing products
- DIY templates, spreadsheets, scripts, or processes
- Expensive manual labor used to solve the issue
- Time-sensitive or money-sensitive consequences
- Evidence that the pain is tied to a business or life outcome

## Core Prompt

```text
Act like a world-class researcher who meticulously checks their work.

Find the top 5 urgent and painful problems faced by [target customer].

Use supporting evidence from Reddit, Amazon, Facebook, YouTube, app reviews, review sites, niche forums, and other real sources where this customer talks naturally.

For each problem, show:

1. The problem in plain English.
2. The exact language people use to describe the pain.
3. Where the evidence came from.
4. What people are already doing to solve it.
5. Which existing solutions they are using.
6. What those solutions are failing to do.
7. How urgent the problem appears to be.
8. Whether the problem is frequent, expensive, embarrassing, risky, confusing, or time-consuming.
9. A confidence score from 1 to 10.
10. Whether this problem is strong enough to build around.

Do not invent evidence. Separate verified evidence from assumptions. If there is weak evidence, say so clearly.
```

## Output Format

Return the research in this structure:

```markdown
# Customer Pain Research: [Target Customer]

## Executive Summary

Briefly state whether this customer appears to have painful, urgent, repeated problems worth exploring.

## Top 5 Pain Points

### 1. [Pain Point Name]

**Plain-English problem:**  
[Describe the pain clearly.]

**Urgency level:** Low / Medium / High / Critical

**Evidence quality:** Weak / Moderate / Strong

**Exact customer language:**  
- “[Quote or close paraphrase from source]”
- “[Quote or close paraphrase from source]”
- “[Quote or close paraphrase from source]”

**Where this pain appears:**  
- Reddit:
- Amazon:
- Facebook / forum:
- Reviews:
- Other:

**Current attempted solutions:**  
- [Solution/workaround]
- [Solution/workaround]

**What current solutions fail to solve:**  
- [Failure]
- [Failure]

**Why this matters:**  
[Explain business, emotional, financial, or practical impact.]

**Build-worthiness score:** [1-10]

**Researcher verdict:**  
Build around this / Explore further / Too weak for now

---

## Patterns Across All Pain Points

- Repeated language:
- Common failed solutions:
- Emotional triggers:
- Buying signals:
- Strongest wedge opportunity:

## Recommended Next Research Step

State the next 3 validation actions.
```

## Validation Rubric

Score each pain from 1 to 10.

| Score | Meaning |
|---:|---|
| 1-3 | Weak signal. Mostly hypothetical or low urgency. |
| 4-6 | Some real pain, but unclear willingness to act or pay. |
| 7-8 | Strong repeated pain with visible workarounds and failed solutions. |
| 9-10 | Urgent, repeated, expensive or emotionally charged pain with clear buying behavior. |

## Red Flags

Reject or deprioritize ideas when:

- The pain only appears in founder imagination.
- People say “that would be nice” but are not actively seeking solutions.
- Existing solutions already solve the pain well.
- The pain is too vague, such as “people want to save time.”
- The customer has no budget, authority, or urgency.
- The market is crowded and no clear failure pattern appears.
- The evidence is all from promotional content instead of real customers.

## Quality Checklist

Before finalizing, confirm:

- The top problems are ranked by evidence, not by cleverness.
- Each pain has real customer language.
- Sources include at least two distinct channel types when possible.
- Existing failed solutions are named.
- The output separates facts from assumptions.
- The recommended next step is actionable.

## Handoff To Next Skill

Pass the strongest 1-3 validated pain points to **The Strategist**.

Include:

```text
Target customer:
Validated pain point:
Exact customer language:
Current failed solutions:
Urgency score:
Best wedge opportunity:
```


---

# Skill: The Strategist

## Purpose

Turn validated customer pain into a free offer people want immediately.

This skill creates lead magnet ideas that are so useful the target customer would plausibly pay $50 to $100 for them, then gives the asset away for free to prove demand and capture qualified leads.

## Primary Job

Use validated pain points to design a high-value lead magnet that is fast to build, cheap to launch, and likely to generate sign-ups.

The goal is not to create a perfect product. The goal is to create a valuable proof-of-demand asset.

## When To Use This Skill

Use this skill after **The Researcher** has identified real pain.

Use it when you need:

- A free downloadable offer
- A lead magnet
- A checklist, calculator, template, guide, teardown, mini-course, swipe file, playbook, audit, scorecard, or planner
- A fast validation asset before building a product
- A clear reason for customers to join your email list

Do not use this skill before customer pain is validated.

## Required Inputs

```text
Target customer:
Validated pain points:
Exact customer language:
Existing failed solutions:
Desired business model, if known:
Founder skills or assets available:
Launch budget:
Timeline:
```

## Core Prompt

```text
Based on these validated pain points:

[paste pain points]

Suggest 5 lead magnet ideas people would fall over themselves to download.

Each idea should be so useful that the target customer would plausibly pay $50 to $100 for it, even though we will give it away for free.

Rank each idea by:

1. Fastest to build.
2. Cheapest to launch.
3. Most likely to get sign-ups.
4. Best fit for the validated pain.
5. Best path toward a paid offer.

For each lead magnet, include:

- Title
- Format
- Who it is for
- Pain it solves
- Why the customer wants it now
- What makes it feel unusually valuable
- What existing solution it improves on
- Estimated build time
- Tools needed
- Email capture angle
- Follow-up paid offer it could lead to

Do not give generic lead magnets. Make each one specific, practical, and tied to the exact language customers use.
```

## Lead Magnet Types To Consider

Use the format that best matches the pain.

Common high-converting formats:

- Checklist
- Calculator
- Scorecard
- Diagnostic quiz
- Swipe file
- Script pack
- Template bundle
- 7-day plan
- Emergency guide
- Buyer’s guide
- Cost-savings calculator
- Audit worksheet
- SOP pack
- Comparison matrix
- Mini-course
- Mistake teardown
- Interactive Notion/Airtable/Google Sheet
- “Done-for-you” starter kit
- Decision tree
- Troubleshooting guide

## Output Format

```markdown
# Lead Magnet Strategy for [Target Customer]

## Best Pain To Build Around

**Pain selected:**  
[Name the strongest pain.]

**Why this pain is best:**  
[Explain based on urgency, frequency, cost, emotional intensity, and evidence.]

## Top 5 Lead Magnet Ideas

### 1. [Lead Magnet Title]

**Format:**  
[Checklist / calculator / guide / scorecard / etc.]

**Customer pain solved:**  
[Specific pain.]

**Why people would download it:**  
[Plain-English reason.]

**Why it feels worth $50-$100:**  
[Specific value.]

**What makes it different from generic free content:**  
[Explain.]

**Fastest build path:**  
[Steps.]

**Estimated build time:**  
[X hours/days.]

**Tools needed:**  
[Tools.]

**Sign-up likelihood:** 1-10  
**Build speed:** 1-10  
**Launch cost:** 1-10  
**Paid-offer path:** 1-10

**Possible paid offer after download:**  
[Offer.]

---

## Ranking Table

| Rank | Lead Magnet | Build Speed | Launch Cost | Sign-Up Potential | Paid Offer Fit | Total |
|---:|---|---:|---:|---:|---:|---:|
| 1 |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |

## Recommended Winner

Choose one lead magnet and explain why.

## Pushback Section

Challenge the first idea.

Ask:

- Is this specific enough?
- Would the target customer stop scrolling for this?
- Does it solve a painful enough problem?
- Could this be built in less than 48 hours?
- Does it naturally lead to a paid offer?
- Is the title clear enough without explanation?

## Final Lead Magnet Brief

```text
Lead magnet title:
Target customer:
Primary pain:
Promise:
Format:
Sections included:
CTA:
Paid offer path:
Build plan:
```
```

## Decision Rules

Choose the winner using this priority order:

1. Strongest connection to validated pain
2. Fastest path to real launch
3. Highest sign-up potential
4. Strongest paid offer path
5. Lowest production complexity

Do not select the most impressive idea if it will take weeks to build.

## Red Flags

Avoid lead magnets that are:

- Too broad
- Too academic
- Too long
- Too founder-focused
- Too generic
- Too hard to complete
- Not tied to a painful outcome
- Unclear about what the user gets
- Impossible to build quickly

## Quality Checklist

Before finalizing, confirm:

- The lead magnet is tied to real pain.
- The title makes the value obvious.
- The asset can be built quickly.
- The customer would plausibly exchange an email for it.
- The lead magnet creates a natural path to a paid offer.
- The final recommendation is specific enough to hand to **The Copywriter**.

## Handoff To Next Skill

Pass the winning lead magnet to **The Copywriter**.

Include:

```text
Lead magnet title:
Target customer:
Pain solved:
Emotional trigger:
Exact customer language:
Promise:
Format:
CTA goal:
Paid offer path:
```


---

# Skill: The Copywriter

## Purpose

Write conversion-focused copy one step at a time.

This skill turns a validated lead magnet into clear, specific, benefit-driven copy for a one-page landing page. The copy should make the target customer feel understood and make the CTA obvious.

## Primary Job

Write words that make people click.

Do not ask for “good copy.” Build the copy in sequence:

1. Hook
2. Benefit bullets
3. Landing page copy
4. CTA
5. Optional email follow-up copy

Each piece earns the next.

## When To Use This Skill

Use this skill after **The Strategist** has selected a lead magnet.

Use it when you need:

- A landing page headline
- A one-sentence hook
- Benefit bullets
- CTA copy
- Email capture copy
- Short social post copy
- Follow-up email sequence
- Copy for a one-page website

## Required Inputs

```text
Lead magnet title:
Target customer:
Pain solved:
Exact customer language:
Promise:
Format:
Desired tone:
CTA goal:
Paid offer path:
```

## Copy Principles

Good copy should be:

- Specific
- Useful
- Human
- Plainspoken
- Benefit-driven
- Rooted in customer language
- Focused on the customer’s pain, not the founder’s idea

Avoid:

- Buzzwords
- Vague promises
- Overhyped language
- Empty “transform your life/business” claims
- Corporate filler
- Long paragraphs
- Weak CTAs such as “Learn more”

## Sequential Prompt Flow

Run these prompts in order.

### Step 1: Hook

```text
Write 10 one-sentence hooks for this lead magnet:

Lead magnet: [lead magnet]
Target customer: [target customer]
Pain: [pain]
Exact customer language: [customer language]

The hook should make the customer feel seen immediately. Use plain language. Avoid hype. Make the benefit obvious.
```

Select the best hook or combine the best parts.

### Step 2: Benefit Bullets

```text
Using this hook:

[chosen hook]

Write 3 to 5 benefit-driven bullets that make this lead magnet irresistible.

Each bullet should explain what the customer will be able to do, avoid, fix, understand, calculate, decide, or implement after downloading it.

Make the bullets specific and practical.
```

### Step 3: Landing Page Copy

```text
Using this hook and these bullets:

Hook:
[hook]

Bullets:
[bullets]

Draft copy for a one-page landing page.

Include:

1. Eyebrow line.
2. Headline.
3. Subheadline.
4. 3 to 5 benefit bullets.
5. Short section explaining what is inside.
6. Email capture CTA.
7. Small trust-building or reassurance line.
8. Optional final CTA.

Keep it focused, clear, and easy to scan.
```

### Step 4: CTA Options

```text
Give me 10 CTA button options for this lead magnet.

Avoid generic CTAs like “Submit” or “Learn More.”

Make the CTA action-oriented, specific, and emotionally aligned with the customer’s pain.
```

### Step 5: Tighten Copy

```text
Edit this landing page copy to be sharper, shorter, and more conversion-focused.

Remove vague language. Improve specificity. Keep the tone calm and confident.

Copy:
[paste copy]
```

## Output Format

```markdown
# Copy Package: [Lead Magnet]

## Best Hook

[Chosen hook]

## Alternate Hooks

1. 
2. 
3. 

## Benefit Bullets

- 
- 
- 

## Landing Page Copy

### Eyebrow

[Eyebrow copy]

### Headline

[Headline]

### Subheadline

[Subheadline]

### Benefits

- 
- 
- 

### What You Get

[Short section]

### Email Capture Copy

[Form intro or microcopy]

### CTA Button

[CTA]

### Reassurance Line

[Privacy / no spam / simple expectation line]

## Optional Follow-Up Email

**Subject:**  
[Subject]

**Body:**  
[Short email that delivers the lead magnet and points toward next step.]

## Copy Notes

- Primary pain addressed:
- Emotional trigger:
- Conversion angle:
- Words pulled from customer language:
```

## CTA Rules

Strong CTAs usually include the result.

Examples:

- “Get the Checklist”
- “Send Me the Template”
- “Download the Cost Calculator”
- “Get My 7-Day Plan”
- “Start the Audit”
- “Show Me What To Fix”
- “Grab the Playbook”

Avoid:

- Submit
- Click here
- Learn more
- Get started, unless the next action is truly a start
- Join now, unless joining is the primary action

## Quality Checklist

Before finalizing, confirm:

- The headline is clear without explanation.
- The copy uses customer language.
- The benefits describe outcomes, not features.
- The CTA says what happens next.
- The copy is scannable.
- The tone is confident without sounding fake.
- The landing page can be handed directly to **The Builder**.

## Handoff To Next Skill

Pass the finalized copy to **The Builder**.

Include:

```text
Lead magnet title:
Design tone:
Headline:
Subheadline:
Benefit bullets:
What-you-get section:
CTA button:
Reassurance line:
Any brand colors or inspiration links:
```


---

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


---

# Skill: The Marketer

## Purpose

Turn attention into leads, then turn leads into paying customers.

This skill creates a practical funnel and 30/60/90-day growth plan for a validated lead magnet and one-page landing page.

## Primary Job

Build a marketing plan that gets the ideal customer to notice the offer, download the lead magnet, and move toward a paid product or service.

The goal is not random posting. The goal is a measurable funnel.

## When To Use This Skill

Use this skill after **The Builder** has created the landing page or prototype.

Use it when you need:

- A funnel map
- A 30/60/90-day growth plan
- Weekly priorities
- Posting cadence
- Content themes
- Metrics
- Conversion sequence
- Follow-up email sequence
- Path from free offer to paid offer

## Required Inputs

```text
Target customer:
Lead magnet:
Landing page URL or draft:
Core pain:
Primary CTA:
Email platform:
Paid offer, if known:
Monthly revenue goal:
Available channels:
Weekly time budget:
Launch budget:
```

## Core Prompt

```text
Create a sales funnel flow I can use to get the attention of my ideal customer, get them to download my lead magnet, and convert them from lead to paying customer.

Target customer:
[target customer]

Lead magnet:
[lead magnet]

Core pain:
[pain]

Landing page:
[URL or page summary]

Revenue goal:
[$5K-$10K/month or other goal]

Include:

1. Funnel map from awareness to paid conversion.
2. 30, 60, and 90-day growth plan.
3. Weekly priorities.
4. Posting cadence.
5. Content themes.
6. Specific content examples.
7. Email follow-up sequence.
8. Conversion metrics to track.
9. Experiments to run.
10. What to stop doing if it is not working.

Make the plan practical, specific, and measurable.
```

## Funnel Structure

Use this funnel as the default:

```text
Awareness
→ Short content, comments, community posts, SEO, partnerships, paid tests, or direct outreach

Interest
→ Pain-specific posts, examples, mini-teardowns, checklists, before/after content

Lead Capture
→ Landing page with lead magnet

Nurture
→ Email sequence that delivers value and builds trust

Conversion
→ Consultation, paid template, course, SaaS waitlist, service, membership, workshop, or productized offer

Retention or Expansion
→ Follow-up offer, community, subscription, implementation support, upsell, or referral
```

## 30/60/90-Day Growth Plan

### First 30 Days: Validate Demand

Focus:

- Publish consistently
- Drive traffic to the lead magnet
- Test the landing page
- Collect first leads
- Learn which pain language gets attention

Target outcomes:

- 100-500 landing page visits
- 25-100 email sign-ups
- 5-15 customer conversations
- Early conversion insights

### Days 31-60: Improve Conversion

Focus:

- Improve landing page copy
- Improve lead magnet quality
- Build email nurture sequence
- Test 2-3 content angles
- Start direct outreach or partnerships

Target outcomes:

- Higher opt-in rate
- Clearer customer segmentation
- First paid offer tests
- Testimonials or feedback

### Days 61-90: Scale What Works

Focus:

- Double down on top-performing content
- Launch a paid offer
- Add retargeting or partnerships if appropriate
- Create repeatable weekly operating rhythm

Target outcomes:

- Predictable lead flow
- First repeatable paid conversions
- Revenue path toward $5K-$10K/month

## Output Format

```markdown
# Growth Plan: [Lead Magnet]

## Funnel Map

| Stage | Goal | Tactic | Asset Needed | Metric |
|---|---|---|---|---|
| Awareness |  |  |  |  |
| Interest |  |  |  |  |
| Lead Capture |  |  |  |  |
| Nurture |  |  |  |  |
| Conversion |  |  |  |  |

## 30-Day Plan

### Weekly Priorities

**Week 1:**  
- 

**Week 2:**  
- 

**Week 3:**  
- 

**Week 4:**  
- 

### Posting Cadence

- Channel:
- Frequency:
- Content types:

### Metrics

- Landing page visits:
- Opt-in rate:
- Email open rate:
- Reply rate:
- Calls booked:
- Paid conversions:

## 60-Day Plan

[Repeat structure.]

## 90-Day Plan

[Repeat structure.]

## Content Pillars

1. Pain education
2. Mistakes and myths
3. Before/after examples
4. How-to guidance
5. Proof, stories, or teardown content

## Sample Posts

Provide 10 posts:

1.
2.
3.

## Email Nurture Sequence

| Email | Timing | Purpose | Subject | CTA |
|---:|---|---|---|---|
| 1 | Immediately | Deliver lead magnet |  |  |
| 2 | Day 1 | Build trust |  |  |
| 3 | Day 3 | Show common mistake |  |  |
| 4 | Day 5 | Introduce paid path |  |  |
| 5 | Day 7 | Ask for reply or booking |  |  |

## Experiments

List 5 experiments to run, each with:

- Hypothesis
- Test
- Success metric
- Decision rule

## Stop Doing List

List activities to stop if they do not generate measurable movement.
```

## Key Metrics

Track:

- Landing page visits
- Opt-in rate
- Traffic source
- Email open rate
- Email click rate
- Reply rate
- Call booking rate
- Paid conversion rate
- Cost per lead, if using ads
- Revenue per lead
- Time spent per channel

## Decision Rules

Use simple thresholds.

Examples:

```text
If opt-in rate is below 15%, improve headline, lead magnet title, and CTA.
If traffic is below 100 visits/month, focus on distribution before changing the offer.
If email opens are below 30%, improve subject lines and sender trust.
If leads are not replying, improve the problem framing.
If people download but do not buy, the paid offer may not match the pain.
```

## Red Flags

Avoid:

- Posting without a clear CTA
- Changing the offer every few days
- Measuring vanity metrics only
- Creating content that entertains but does not qualify leads
- Launching paid ads before the landing page converts
- Building more features instead of talking to customers
- Selling before the lead magnet proves demand

## Quality Checklist

Before finalizing, confirm:

- The plan is channel-specific.
- The cadence is realistic.
- Metrics are measurable.
- The paid conversion path is clear.
- The plan includes weekly actions.
- The plan includes stop/continue decision rules.
- The revenue goal is tied to actual math.

## Handoff Back To Research

Marketing results should feed back into **The Researcher**.

Collect:

```text
Best-performing posts:
Highest-converting pain language:
Common replies:
Lead magnet feedback:
Objections:
Paid offer interest:
Conversion rates:
```

Use those insights to refine the pain research, lead magnet, copy, and landing page.
