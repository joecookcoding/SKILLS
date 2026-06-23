---
name: zod-validation-patterns
description: Apply Zod v4 schema patterns whenever writing, editing, or reviewing Zod validation code — schemas, refinements, cross-field rules, error messages, transforms, resolver integration, or anything importing `zod`. Triggers on "validate X with Zod", "make a Zod schema for this type", "extend a TypeScript type for validation", "infer Zod from a type", "lock the schema to my generated API types", "add cross-field validation", "validate password confirmation", "why is my Zod schema not catching X", or any task involving zodResolver, react-hook-form + zod, OpenAPI → Zod, satisfies z.ZodType, .refine, .superRefine, .transform, .coerce. Also when editing files importing `zod` or `@hookform/resolvers/zod`, or migrating a hand-written validator function into the schema. Also triggers on "migrate/upgrade Zod v3 to v4", "required_error or invalid_type_error not working", "`.merge` is not a function", "error.format() removed". Not for other validation libraries (yup, JSON Schema) or non-Zod TypeScript type errors.
---

# Zod Validation Patterns

Apply these patterns when writing or editing Zod schemas. Most "weird Zod bug" reports trace to one of the misconceptions below — read the relevant section before debugging.

## Step 0 — detect the Zod version

Check `package.json` before applying anything below:

- **zod `^4`** → `import { z } from 'zod'` — everything in this skill applies as written.
- **zod `3.25.x`** → the v4 API ships inside the v3 package at a subpath — use `import { z } from 'zod/v4'`; with that import, everything in this skill applies.
- **zod `<3.25`** → the v4 syntax in this skill does not exist there — `{ error: '...' }` keys are **silently ignored** (schemas appear to work while every custom message is dropped). Recommend upgrading to 3.25+/4.x; otherwise stop applying these patterns.

**Resolver compatibility:** `zodResolver` with v4 schemas requires `@hookform/resolvers >= 5`. Also note the zod 4.3.x type-overload break with resolvers (react-hook-form/resolvers#842) — `zodResolver(schema)` fails to type-check against certain zod 4.3.x releases; the workaround is to pin/update the zod + `@hookform/resolvers` versions per that issue.

## Core insight — Zod cannot be derived from a TS type

**TypeScript types are erased at runtime.** A Zod schema is a runtime value carrying field metadata, validators, and refinements. There is no `z.fromType<T>()` and there cannot be — by the time Zod runs, the type literally doesn't exist anymore.

This constraint shapes everything else in this skill. When a developer asks *"can't I just give Zod the type?"* — the answer is no, and the recommended substitute is the `satisfies z.ZodType<T>` pattern below.

If full automation matters more than custom error messages, escape to OpenAPI → Zod code-gen (last section). Otherwise, write the schema by hand and let `satisfies` enforce sync.

## Decision tree for "I need to validate X"

```
Is the type already generated (OpenAPI, GraphQL, tRPC)?
├── Yes → Write a hand schema, lock with `satisfies z.ZodType<T>`.
│         ├── Cross-field rule? → `.refine()` / `.superRefine()` inside the schema.
│         └── Custom error messages? → `{ error: '...' }` per field.
└── No → Write the schema as the source of truth.
          ├── Derive the TS type via `z.infer<typeof schema>`.
          └── Same refinement / error rules apply.

Is there a sibling hand-rolled validator function?
└── Migrate its rules INTO the schema via `.superRefine()`. Delete the function.
    A separate validator is a future drift bug.
    (Finding ALL sibling validators and their call sites across a repo is a
    codebase-exploration job — invoke the `codebase-exploration` skill before deleting.)

Does the input shape differ from the validated shape (string → number, string → Date)?
└── `z.coerce.number()` for type coercion, `.transform()` for value mapping.
    Watch the `satisfies` interaction if you use `.transform()`.
```

## Pattern 1 — Lock a schema to a generated type with `satisfies`

When the type is the source of truth (OpenAPI-generated, shared with a backend, or imported from a typed API client), the schema is the runtime mirror — and the `satisfies` clause locks them together at compile time.

```typescript
import { z } from 'zod';
import type { paths } from '@my-api-generated';

type CreateUserRequest = paths['/api/users']['post']['requestBody']['content']['application/json'];

export const createUserSchema = z.object({
  email: z.string().min(1, { error: 'Email is required' }),
  name: z.string().nullable().optional(),
  age: z.number().int().nullable().optional(),
}) satisfies z.ZodType<CreateUserRequest>;
```

If the generated type ever changes — a new field arrives, a nullable field becomes required, an enum gets a new value — the `satisfies` clause **fails the build**. You get a compile error pointing at the exact divergence, and the schema must be updated to match.

Why this beats "infer the schema from the type":
- The compiler does the sync job that runtime introspection cannot.
- Custom error messages stay yours (`{ error: 'Email is required' }`), not generic "Required field".
- Schema-specific refinements (`.min(1)`, `.regex(...)`, `.refine(...)`) layer on top without fighting the type.

**Use this whenever a Zod schema mirrors a typed API contract.** It is the canonical Zod ↔ generated-types pattern.

If the **generated type itself** is wrong (the backend contract doesn't match what the API actually returns), the fix is a backend contract fix, not a schema workaround — raise it with whoever owns the backend contract instead of bending the schema to match a known-bad type.

## Pattern 2 — Cross-field rules belong INSIDE the schema, not next to it

A common anti-pattern: write a Zod schema, then wrap it with a separate hand-rolled validator function that adds extra rules ("if account_type is X then department is required"). The schema and the policy drift apart. The schema says one field is optional; the validator says it's required. Bugs hide there.

**Prefer `.refine()` for one cross-field rule, `.superRefine()` for several, both targeting the offending field with `path`.**

### `.refine()` with `path` — one rule, error attached to a specific field

```typescript
const passwordForm = z
  .object({
    password: z.string(),
    confirm: z.string(),
  })
  .refine((data) => data.password === data.confirm, {
    error: "Passwords don't match",
    path: ['confirm'],
  });
```

The `path: ['confirm']` is what surfaces the error on the right input, not as a generic form-level error. **Always include `path`** when the rule names a specific field.

### `.superRefine()` with `ctx.addIssue()` — multiple rules, multiple paths

```typescript
const fundAllocationSchema = z
  .object({
    fund_id: z.string().min(1),
    account_type: z.enum(['EXPENDITURE', 'REVENUE', 'BALANCE_SHEET']),
    department: z.string().nullable().optional(),
  })
  .superRefine((data, ctx) => {
    // Balance Sheet rows skip dept; everything else needs it
    if (data.account_type !== 'BALANCE_SHEET' && !data.department) {
      ctx.addIssue({
        code: 'custom',
        message: 'Department is required for this account type',
        path: ['department'],
      });
    }
  });
```

Each `ctx.addIssue()` lands one error on one path. This is the right tool when several conditional rules apply.

### Why this matters

A bug from a real codebase: the schema declared `unit: z.string().nullable().optional()` (matching the generated type — unit *is* nullable on the backend), but a sibling `validateFundAllocations()` function imposed "unit is required for non-Balance-Sheet rows." Departments that legitimately have zero units couldn't submit. The schema was honest; the external validator was the liar.

**Fix pattern:** when a cross-field rule exists, put it inside `.superRefine()`. The schema becomes the single source of truth for "what makes this object valid." External validator functions are a refactor away from drift.

## Pattern 3 — Zod v4 error syntax (NOT v3)

Zod v4 replaced `required_error` / `invalid_type_error` / `errorMap` with a single `error` parameter that accepts either a string OR a callback.

### Static string

```typescript
z.string({ error: 'Email is required' });
z.string().min(5, { error: 'Too short' });
z.uuid({ error: 'Bad UUID' });
```

### Dynamic callback (sees the issue context)

```typescript
z.string({
  error: (iss) => (iss.input === undefined ? 'Field is required.' : 'Invalid input.'),
});

z.string().min(5, {
  error: (iss) => `Must be at least ${iss.minimum} characters`,
});
```

The callback receives `iss` containing `code`, `input`, `path`, and schema-specific properties (`minimum`, `maximum`, `expected`, etc.).

### Per-parse override

```typescript
schema.parse(value, { error: (iss) => 'override at parse time' });
```

### Project-wide defaults via `z.config`

```typescript
z.config({
  customError: (iss) => {
    if (iss.code === 'invalid_type') return `Invalid type, expected ${iss.expected}`;
  },
});
```

**Error message priority (highest → lowest):** schema-level → per-parse → global config → locale defaults.

> If migrating Zod v3 → v4 (or the code uses `required_error` / `invalid_type_error` / old `.default()` semantics), read `references/v3-to-v4-migration.md`.

## Pattern 4 — `.check()` as a low-level alternative to `.superRefine()`

`.check()` is more verbose but faster in performance-sensitive paths. Use it only when profiling shows refinements are a bottleneck — `.superRefine()` is more readable and more than fast enough for form validation.

```typescript
const schema = z.string().check(z.property('length', z.number().min(10)));
schema.parse('hello there!'); // ✅
schema.parse('hello.');        // ❌
```

Default to `.refine()` / `.superRefine()` unless you have a measured reason.

## Pattern 5 — Conditional refinement with `when`

`.refine()` accepts a `when` callback to skip the refinement when prerequisite fields are themselves invalid. Useful when downstream rules cascade.

```typescript
const baseSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
  email: z.email(),
});

const schema = baseSchema.refine(
  (data) => data.password === data.confirmPassword,
  {
    error: 'Passwords do not match',
    path: ['confirmPassword'],
    when(payload) {
      // Only check password match if both password fields are individually valid
      return baseSchema
        .pick({ password: true, confirmPassword: true })
        .safeParse(payload.value).success;
    },
  },
);
```

Without `when`, a user with a too-short password sees TWO errors ("Password too short" AND "Passwords don't match"). With `when`, only the upstream error fires until it's resolved.

## Pattern 6 — General v4 usage — infer vs input, async parsing, catch

These v4 APIs apply to any schema (not v3-vs-v4 migration deltas — for those, see `references/v3-to-v4-migration.md`).

### `z.infer` vs `z.input` — output vs input type

`z.infer<typeof schema>` is shorthand for `z.output<typeof schema>` — the **post-transform / post-coercion** type. Most of the time this is what you want.

`z.input<typeof schema>` is the **pre-transform** type. You need this when the schema's input differs from its output (any `.transform()`, `z.coerce.*`, or asymmetric refinement) and you want to type the raw input — e.g., form `defaultValues`.

```typescript
const idSchema = z.coerce.number();

type IdInput = z.input<typeof idSchema>;   // unknown — coerce accepts anything
type IdOutput = z.infer<typeof idSchema>;  // number
```

In react-hook-form, `useForm<z.input<typeof schema>>()` matches what the form actually receives from inputs; `submitHandler` receives `z.infer<typeof schema>` (= output) after `zodResolver` parses.

### Async parsing with `parseAsync` / `safeParseAsync`

If any refinement returns a Promise (async DB lookup, remote uniqueness check), `.parse()` throws — you must use `parseAsync()` / `safeParseAsync()`.

```typescript
const usernameSchema = z.string().refine(
  async (v) => !(await isUsernameTaken(v)),
  { error: 'Username already taken' },
);

await usernameSchema.parseAsync('alice');  // works
usernameSchema.parse('alice');             // throws — async refinement in sync parse
```

### `z.catch()` — fallback value on validation failure

```typescript
const portSchema = z.number().int().min(1).max(65535).catch(3000);

portSchema.parse(8080);     // 8080
portSchema.parse('invalid'); // 3000 (fallback, no error)
```

Use sparingly. `.catch()` silently swallows invalid input — fine for env-var parsing where a sensible default beats a crash, dangerous in form code where the user wants to see the error.

## Pattern 7 — `z.coerce`, `z.iso`, `z.transform` — pick the right tool

- **`z.coerce.number()`** — runs `Number(value)` before validation. Use for query-string params, FormData fields, anything where input is always string but the schema is for a number.
- **`z.iso.datetime()` / `z.iso.date()` / `z.iso.time()`** — validates ISO 8601 strings. Use when the field stays as a string but must match the ISO format.
- **`z.string().transform(s => new Date(s))`** — parses to a different output type. The schema's input is a string; its output is a Date.

Common confusion: *"why doesn't my Zod schema accept the form value?"* — usually because the form gives a string and the schema expects a number. Either change the schema input to `z.coerce.number()` or convert before parsing.

## Known pitfalls

### `.transform()` breaks `satisfies z.ZodType<T>` in some cases

`.transform()` changes the schema's output type. If the upstream type `T` describes the input shape, `satisfies z.ZodType<T>` may stop type-checking after a transform. Two fixes:

1. **Transform outside the schema.** Parse with the un-transformed schema, then map the result manually. Keeps the `satisfies` lock.
2. **Use `z.ZodType<Input, Output>`** explicitly when both shapes are knowable. Heavier; only do this if (1) is awkward.

### `.default()` + `zodResolver` (react-hook-form)

Zod's `.default()` only fires when the input is `undefined`. If react-hook-form passes `null` or `""` for an empty field (which it commonly does), `.default()` won't trigger and the schema sees the empty value. Symptom: defaults silently don't apply in forms.

**Fix:** apply defaults in the form's `defaultValues`, not in the schema. Use the schema for shape validation only.

### Optional vs. nullable vs. both

- `z.string().optional()` accepts `string | undefined`
- `z.string().nullable()` accepts `string | null`
- `z.string().nullable().optional()` accepts `string | null | undefined`

When mirroring a generated type, match the exact shape:
- TS type `field?: string` → `z.string().optional()`
- TS type `field: string | null` → `z.string().nullable()`
- TS type `field?: string | null` → `z.string().nullable().optional()`

Mismatches don't always fail `satisfies` — they fail at parse time with confusing messages.

### `safeParse` vs `parse`

`parse()` throws on failure; `safeParse()` returns `{ success, data, error }`. In form code, prefer `safeParse()` — exceptions break React error boundaries in surprising ways.

## When to escape to OpenAPI → Zod code-gen

If the schema is a literal mirror of an OpenAPI document and custom error messages don't matter much, generate the Zod schemas alongside the TS types. Tools: `openapi-zod-client`, `kubb`, `orval` (Zod plugin).

**The tradeoff that usually disqualifies this approach:**
- Generated schemas have generic messages ("String must contain at least 1 character(s)") that leak into user-facing form errors.
- Cross-field rules are NOT in OpenAPI, so a separate `.superRefine()` layer is still required for any conditional logic.
- Adds a regen step (`npm run gen:zod` or similar) to coordinate with backend changes.

**The case where code-gen wins:**
- Internal/admin tools where error messages don't need polish.
- High schema churn from the backend (a dozen schemas changing weekly).
- Schemas that are pure data shape with zero cross-field logic.

For typical product forms, **hand-write + `satisfies`** is usually the better answer.

## Quick reference & bug triage

For the anti-pattern → fix table and the bug-report triage checklist, read `references/quick-reference.md`.

---

When the user is editing a Zod schema or asks "how do I validate X with Zod" — apply the patterns above. The single biggest leverage point in this skill is **putting cross-field rules inside the schema with `.refine` / `.superRefine`** instead of in a sibling validator function. Most real-world Zod bugs trace to that single anti-pattern.
