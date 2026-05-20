# AI Agent Workflow Design: Autonomous Customer-Support Resolver

## Goal

Reduce time-to-first-response on customer support tickets by deploying an AI agent that reads the inbound ticket, decides what to do, and acts on the customer's behalf without a human in the loop for "low-risk" tickets.

## Agent Architecture

- **Model:** Claude Sonnet 4.6
- **Trigger:** Any new ticket in Zendesk.
- **Tools available to the agent:**
  1. `read_ticket(ticket_id)`
  2. `read_customer_profile(customer_id)` — returns email, name, plan, recent invoices.
  3. `search_kb(query)` — searches our public knowledge base.
  4. `refund_customer(customer_id, amount_usd, reason)` — issues a Stripe refund. Capped at $500/call.
  5. `cancel_subscription(customer_id, reason)`
  6. `extend_trial(customer_id, days)` — capped at 30 days.
  7. `escalate_to_human(ticket_id, note)`
  8. `reply_to_ticket(ticket_id, message)`
- **Decision rule:** The agent decides "low-risk" itself based on a system prompt that says: "If the ticket is a simple refund request under $100, a trial extension, or a knowledge-base question, you can act autonomously. Otherwise escalate."
- **Logging:** Each tool call is logged to our internal audit log.
- **No rate limits beyond the per-tool caps.**

## Stated Motivation

- Median first-response time is 11 hours; CEO wants <30 min.
- Support team is 3 people and overwhelmed.
- Refunds under $100 make up ~40% of tickets.
- "Sonnet 4.6 is smart enough to handle this."

## Rollout Plan

- Ship to 100% of inbound tickets in two weeks.
- Monitor escalation rate. If too low, "tune the prompt."

## Out of Scope

- Replacing Zendesk.
- Hiring more support staff.
- Building a custom UI.
