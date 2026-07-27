# Ingestion Protocol

## Initial map

1. Record Git state.
2. Read local agent instructions.
3. Inspect manifests, architecture docs, CI, deployment, schemas, routes, tests, and ownership files.
4. Build deterministic structure.
5. Produce semantic pages with provenance.
6. Generate the machine-readable architecture JSON.
7. Render the interactive architecture HTML from that JSON.
8. Create a safe Mesh export.

## Incremental map

1. Read the last mapped commit.
2. Calculate committed and working-tree changes.
3. Classify likely knowledge and graph impact.
4. Refresh only affected generated pages, nodes, edges, and flows.
5. Preserve stable graph IDs.
6. Retain disappeared items as unresolved.
7. Rebuild indexes, HTML, and export.

## Session context compilation

1. Seed from the task, changed paths, explicit targets, and named flows.
2. Traverse required and relevant edges in both directions.
3. Include complete flows when any step is selected.
4. Include reference edges on semantic match or deep-context request.
5. Inspect live source and expand when implementation reveals missing relationships.
6. Stop only when no new material relationship is found.
7. Record token estimates for visibility, never as a correctness cutoff.
