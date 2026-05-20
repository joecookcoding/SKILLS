# Architecture Review Example

Use the Multi-Agent Devil’s Advocate Review Skill.

## Review Packet

Review Mode: Architecture Review

Target: Moving a single Next.js app into a Turborepo monorepo

Risk category: Developer productivity, deployment complexity, shared packages, CI/CD, maintainability

Relevant user flow or business process: Developers need to share UI, types, and service utilities across multiple apps

Expected behavior: The migration should improve reuse without slowing delivery or breaking deployment

Out of scope: Rewriting the app, changing database providers, changing hosting providers

## Prompt

Run the architecture review. Include strongest case for the migration, strongest case against it, operational risks, and the smallest reversible migration path.
