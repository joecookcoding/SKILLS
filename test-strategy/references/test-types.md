# Test types: patterns and libraries

Read this when step 3 of the workflow has picked a test type and you need the shape.

## End-to-end

Drive the real app the way a user does, then check what the user would see.

- **Web:** Playwright or the browser the session has (Claude in Chrome, the built-in
  browser, CDP). Select by role and visible text, not CSS paths, so a restyle doesn't
  break the test.
- **Mobile:** the iOS simulator or Android emulator through their MCP or CLI.
- **Backend:** start the service locally and send real requests; assert on the response
  and on the row or message it produced.
- **CLI:** run the binary with real arguments in a temp directory; assert on stdout,
  exit code and files written.

A **feature map** makes a good rubric: a list of features from the user's side, each
with its path, shortcut or selector, and expected result. Keep it next to the `verify`
skill and add a row when a feature ships.

On failure, keep the evidence: a screenshot, a trace, the step that broke. "Timeout
after 30 s" tells nobody anything; "the Pay button stayed disabled after the card was
entered" does.

Keep the E2E set small: the flows that make money or lose data first. Each one costs
real run time.

## Property tests

State a rule that can't fail, then let a library generate inputs that try to break it.

| Language | Library |
|---|---|
| JS / TS | fast-check |
| Python | Hypothesis |
| Rust | proptest |
| Go | `testing/quick`, rapid |
| JVM | jqwik |

Properties nearly every project has:

- **Round trip:** `decode(encode(x)) == x`; `parse(print(ast)) == ast`.
- **Invariant:** a balance never goes negative; a sorted list stays sorted after insert;
  totals equal the sum of their lines.
- **Idempotency:** running a migration, a normaliser or a retry twice equals running it
  once.
- **Equivalence:** the optimised function returns what the naive one does.

```ts
import fc from "fast-check";
test("slug round-trips through the URL", () => {
  fc.assert(fc.property(fc.string(), (title) => {
    expect(fromSlug(toSlug(title))).toBe(normalise(title));
  }));
});
```

When a property fails, the library shrinks the input to the smallest failing case. Add
that case as a plain unit test too, so it stays fixed if the generator changes.

## Differential tests

For a rewrite, port, or migration that must behave the same: run old and new on the same
inputs and diff the outputs.

- **Inputs:** random generation, or a sample of real production traffic (scrubbed of
  personal data). Hand-picked fixtures miss what production sends.
- **Normalise noise** before diffing: whitespace, key order, timestamps, generated IDs,
  float rounding.
- **Keep an approved-differences list** for places the new system is meant to differ,
  each with a reason. Every other difference is a bug or an undeclared breaking change.
- Report the count of inputs run, the count that differed, and the first few diffs.

## Table-driven unit tests

For pure logic with many named cases. The table is the spec: each row is an input and the
output a domain expert would give, written from the requirement, not from running the code.

```py
@pytest.mark.parametrize("income,expected", [
    (0, 0), (11_600, 1_160), (47_150, 5_426),   # from the published bracket table
])
def test_tax(income, expected):
    assert tax_2024_single(income) == expected
```

## Integration tests

Against the real database, queue or service (or its official emulator), started by the
test or by a script. Where containers run is a project rule: check it before starting one.
Tools that embed the engine in-process (PGlite, mongodb-memory-server, SQLite for
SQLite-only code) are fine. Reset state between tests with transactions or truncation,
not by sharing one dirty database.
