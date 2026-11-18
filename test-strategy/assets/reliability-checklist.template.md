# Reliability checklist

The agent reads the diff, runs only the items whose trigger matches, and reports each as
pass, fail or not applicable. Add an item only when a miss happened in at least two PRs
or caused an incident, and the trigger can be read from a diff. Prune items that haven't
fired in <N> months.

| # | Trigger (readable from the diff) | Check | Why (incident or PR) | Added |
|---|---|---|---|---|
| 1 | A stored type or persisted field changes | Data saved by the previous release still loads when the new field is missing | <link> | <date> |
| 2 | A migration file is added | It runs twice without error, and a rollback path exists or is stated as none | <link> | <date> |
| 3 | An env var is read for the first time | It is in the example env file and the deploy config, and the code fails clearly when it is missing | <link> | <date> |
| 4 | A public API response shape changes | Existing clients' fields are still present, or the change is versioned | <link> | <date> |
| 5 | Retry, queue or webhook handler code changes | Handling the same message twice has the same effect as once | <link> | <date> |
