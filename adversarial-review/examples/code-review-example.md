# Code Review Example

Use the Multi-Agent Devil’s Advocate Review Skill.

## Review Packet

Review Mode: Code Review

Target: Changed files in the current pull request

Risk category: Authorization, validation, error handling, and regression risk

Relevant user flow or business process: A signed-in user updates account settings

Trust boundary, if applicable: Browser client to server route handler

Expected behavior: Users may only update their own account settings unless they have an admin role

Out of scope: Full repo review, unrelated refactors, styling changes

## Prompt

Apply the skill to the changed files in my staging area. Focus on concrete claims only. Challenge every serious claim before making a final merge recommendation.
