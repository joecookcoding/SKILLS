# Architecture Proposal: Move from Postgres + Redis to a Single DynamoDB Deployment

## Current State

- **App:** Next.js SaaS, ~12K monthly active users, ~400 paying customers.
- **DB:** AWS RDS Postgres (db.m5.large), ~80 GB, ~30 tables, heavy use of joins for the analytics dashboard.
- **Cache:** AWS ElastiCache Redis (cache.t3.small), used for session storage and a query-result cache (~30% hit rate).
- **Team:** 4 backend engineers. None has shipped DynamoDB to production before.
- **Pain points:** RDS bill is ~$340/mo and growing. We had two ~10-minute outages in the last 6 months from connection-pool exhaustion. The analytics dashboard sometimes takes 6+ seconds to load.

## Proposed Change

Migrate the entire backend off RDS + ElastiCache and onto a single DynamoDB deployment. Use single-table design. Drop Redis entirely (DynamoDB will handle session lookup directly). Estimated migration time: one quarter.

## Stated Motivation

- DynamoDB is "infinitely scalable" so we never worry about connection pools again.
- Cheaper than RDS at our scale (claimed).
- One database instead of two services to operate.
- We want to support 10x more users next year and Postgres "won't keep up."

## Out of Scope

- Switching cloud providers.
- Rewriting the frontend.
- Changing the auth provider.
