# Severity Guide, Anti-Noise Rules, and Safety Boundaries

Read this when grading findings or when you're unsure whether a request crosses a safety line.

## Severity Guide

| Level | Meaning |
| :--- | :--- |
| **Critical** | Immediate risk to users, data, money, production stability, authn, authz, or legal/compliance exposure. |
| **High** | Likely real issue with meaningful impact, but not immediately catastrophic. |
| **Medium** | Valid issue with limited scope, unclear reachability, or moderate business impact. |
| **Low** | Cleanup, maintainability, UX, performance, or documentation improvement. |
| **Needs Evidence** | Plausible but not proven. Mark this rather than guessing a severity. |
| **Reject** | Unsupported, false positive, out of scope, or based on incorrect assumptions. |

## Anti-Noise Rules

Reject or revise findings that use vague hedging without evidence:

- "Might be insecure"
- "Could be an issue"
- "Potential vulnerability"
- "Consider improving"
- "This seems risky"
- "Maybe add validation"

A valid finding must include: **what** specifically is wrong, **where** it occurs (file/function/line), **why** it matters, **what would prove or disprove it**, and **what to do next**.

## Safety Boundaries

### This skill must NOT be used to:

- Create exploit code or proof-of-concept attacks
- Chain vulnerabilities into working attacks
- Bypass authentication or authorization
- Evade detection / logging / monitoring
- Extract secrets, tokens, or credentials
- Attack third-party systems
- Perform unauthorized testing
- Generate malware
- Provide operational abuse steps

### This skill MAY be used to:

- Improve code quality
- Review architecture
- Find defensive gaps
- Validate assumptions
- Reduce false positives
- Improve testing
- Strengthen authorization logic
- Improve deployment safety
- Improve AI agent governance
- Improve business or technical decisions

## Human Approval Gates

Agents may recommend actions but should not automatically perform high-impact actions. Require human approval for:

- Production changes
- Authentication or authorization changes
- Permission changes
- Data migrations
- Data deletion
- Public disclosure
- Security reports
- Large refactors
- Dependency upgrades with breaking changes
- Anything touching secrets, tokens, credentials, private data, or customer data
