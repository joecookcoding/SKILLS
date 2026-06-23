# Zod Quick Reference

The anti-pattern → fix table and the bug-report triage checklist. Read this when reviewing existing Zod code for anti-patterns, or when triaging a reported Zod bug.

## Quick reference — patterns this skill replaces

| Anti-pattern | Replace with |
|---|---|
| Hand-rolled `validateFoo()` function next to the schema | `.refine()` or `.superRefine()` inside the schema |
| `required_error: 'msg'` (v3) | `{ error: 'msg' }` (v4) |
| `invalid_type_error: 'msg'` (v3) | `{ error: 'msg' }` (v4) |
| `message: 'msg'` (v3) | `{ error: 'msg' }` (v4) |
| `errorMap: () => ...` (v3) | `{ error: (iss) => ... }` per schema, or `z.config({ customError })` global |
| `z.string().email()` (v3) | `z.email()` (v4) — top-level format validator |
| `z.string().uuid()` (v3) | `z.uuid()` (v4) |
| `z.string().url()` (v3) | `z.url()` (v4) |
| `.strict()` / `.passthrough()` (v3) | `z.strictObject({...})` / `z.looseObject({...})` (v4) |
| `.merge()` (v3, removed in v4) | `.extend()` (v4) |
| `.default('0')` on a coerced number (v3 behavior) | `.prefault('0')` (v4 — `.default` runs AFTER validation) |
| `result.error.format()` / `result.error.flatten()` (v3) | `z.prettifyError(err)` / `z.treeifyError(err)` / `z.flattenError(err)` (v4) |
| `.default()` inside schema for form initial values | `defaultValues` in `useForm` / `useFormContext` |
| Generic `z.string()` accepting empty | `z.string().min(1, { error: 'Required' })` |
| `as Foo` casting after `.parse()` | `satisfies z.ZodType<Foo>` on the schema |
| Two schemas: one for input, one for output | One schema with `.transform()` OR keep transform outside |
| `z.infer<typeof s>` everywhere | `z.input<typeof s>` for form `defaultValues` when schema has transform/coerce |
| `.parse()` with an async refinement | `parseAsync()` / `safeParseAsync()` — sync parse throws on async refinements |

---

## Quick triage when a Zod-related bug is reported

1. **Read the schema first.** Does it actually permit what the user thinks it permits? Check `.optional()` vs `.nullable()` vs `.nullable().optional()`.
2. **Look for sibling validator functions.** If a hand-rolled function runs after `schema.parse()`, the bug is usually there, not in the schema. Migrate it to `.superRefine()`.
3. **Check the error param syntax.** `required_error: 'msg'` and `invalid_type_error: 'msg'` are NOT in the v4 API and are silently ignored — symptom: the error message stays "Required" no matter what you set. `message: 'msg'` IS still accepted as a deprecated alias for `error: 'msg'`, so existing v3 code keeps working — but for any new code, the v4 idiom is `{ error: 'msg' }`. **Single biggest "why won't my error message work" diagnosis.**
4. **Check for `.string().email()` / `.string().uuid()` patterns.** These still work in v4 but they're v3 idiom. Migrate to `z.email()` / `z.uuid()` and you sometimes get a clearer error path as a side effect.
5. **For form bugs:** check `defaultValues` in `useForm` separately from the schema. `.default()` doesn't fire on `null` / `""` — and in v4 it runs AFTER validation so the default must match the OUTPUT type (post-transform/coerce). If a v3 schema's `.default('0')` on a coerced number used to work, the v4 equivalent likely needs `.prefault('0')` instead.
6. **Async refinement + `.parse()`?** Switch to `parseAsync` / `safeParseAsync` — `.parse()` throws on async refinements.
7. **Run `safeParse(value)` in a console with the actual input.** The `success: false` branch's `error.issues` array names the exact rule and path. Then `z.prettifyError(result.error)` for human-readable output, or `z.treeifyError(result.error)` for nested form-shape output, or `z.flattenError(result.error)` for the flat `{ fieldErrors, formErrors }` shape RHF-style code expects.
8. **`.merge()` errors?** v4 removed it. Use `.extend()`.
