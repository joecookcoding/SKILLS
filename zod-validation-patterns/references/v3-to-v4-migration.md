# Zod v3 → v4 Migration

Read this when migrating Zod v3 → v4, or when the code uses `required_error` / `invalid_type_error` / `errorMap` / `.merge()` / `.strict()` / old `.default()` semantics. The patterns here are version-jump traps; the universally-applicable patterns live in `SKILL.md`.

## Error-syntax migration (v3 → v4)

Zod v4 replaced `required_error` / `invalid_type_error` / `errorMap` with a single `error` parameter (covered in full in SKILL.md "Pattern 3 — Zod v4 error syntax"). The migration cue:

**v3 → v4 migration cue:** if a codebase still has `required_error: '...'`, `invalid_type_error: '...'`, or `message: '...'` (as a Zod params-object key), that's v3 syntax. Per the Zod 4 migration guide, `message` is *still supported as a deprecated alias* — code works but should be migrated to `{ error: '...' }` for v4 idiom alignment. `required_error` / `invalid_type_error` are not in the v4 API and are silently ignored. If a custom error message refuses to appear, suspect a v3 params key on a v4 schema first.

## Zod v4 idioms (NOT v3) — top-level validators, strictness, composition, defaults

Zod v4 reshaped several APIs beyond error messages. When reviewing a schema that may have been written against v3, watch for these.

### Top-level format validators

```typescript
// v4 — preferred
z.email({ error: 'Invalid email' });
z.uuid();
z.url();
z.iso.datetime();
z.ipv4();
z.cuid2();

// v3 — works but deprecated, drop on sight
z.string().email();
z.string().uuid();
z.string().url();
```

Top-level format validators produce more efficient runtime code and cleaner types. Flag any `.string().email()` / `.string().uuid()` / `.string().url()` for migration.

### Object strictness via constructor, not chain

```typescript
// v4
z.strictObject({ name: z.string() });   // unknown keys → error
z.looseObject({ name: z.string() });    // unknown keys passed through
z.object({ name: z.string() });         // unknown keys stripped (default)

// v3 (deprecated)
z.object({ name: z.string() }).strict();        // → z.strictObject
z.object({ name: z.string() }).passthrough();   // → z.looseObject
```

### Composition with `.extend()`, not `.merge()`

```typescript
// v4
const userWithAge = baseUser.extend({ age: z.number() });

// v3 (REMOVED in v4)
const userWithAge = baseUser.merge(z.object({ age: z.number() }));
```

`.merge()` is gone in v4. `.extend()` is the only path. If you see `.merge()` in code, it's either v3 syntax or a polyfill — convert it.

### `.default()` vs `.prefault()` — behavior changed in v4

This is one of the most common v3 → v4 surprises and trips up form code constantly.

- **`.default(value)`** — runs AFTER validation. The default value must match the schema's **output type**. If your schema has a `.transform()`, the default is the post-transform shape, not the input shape.
- **`.prefault(value)`** — runs BEFORE validation. Use when you want the default to be parsed/coerced/transformed by the schema like any real input.

```typescript
// .default fires after coercion — value must be a number
z.coerce.number().default(0);

// .prefault fires before — value goes through the coercion
z.coerce.number().prefault('0');  // becomes 0 after validation
```

In v3, `.default()` behaved like v4's `.prefault()`. If a v3 schema with `.default('0')` on a coerced number was working, the v4 equivalent needs `.prefault('0')` or a refactor.

### Error helpers replaced `.format()` and `.flatten()`

```typescript
const result = schema.safeParse(input);
if (!result.success) {
  z.prettifyError(result.error);    // human-readable string
  z.treeifyError(result.error);     // nested object matching the schema shape
  z.flattenError(result.error);     // flat { fieldErrors, formErrors } shape
}
```

`result.error.format()` and `result.error.flatten()` are removed in v4. Use the new top-level helpers.
