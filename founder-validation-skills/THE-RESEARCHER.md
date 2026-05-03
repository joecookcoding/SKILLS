---
name: the-researcher
description: Validate that a target customer is already experiencing urgent, repeated, emotionally charged, paid-for problems before building anything — by mining Reddit, Amazon reviews, Facebook groups, YouTube comments, app/extension reviews, G2/Capterra/Trustpilot, niche forums, Quora, and search autocomplete for real complaints in customer language. Use when the user says "validate my idea", "is there a market for X", "find customer pain", "do customer research", "before I build", "voice-of-customer research", "find pain points for [audience]", "should I build this SaaS / course / coaching offer / productized service / lead magnet", "I have a startup idea", or any pre-build validation question. Step 1 of the founder-validation workflow — produces validated pains that feed the-strategist. Trigger this BEFORE any building, copywriting, or marketing work when the underlying problem hasn't been proven.
---

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
