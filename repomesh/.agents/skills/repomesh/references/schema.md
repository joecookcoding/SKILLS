# Repo Map Schema

Every generated Markdown page should include YAML frontmatter with:

- `title`
- `type`
- `status`: `draft`, `active`, `stale`, `unresolved`, `superseded`, or `archived`
- `ownership`: `human`, `generated`, or `hybrid`
- `source_commit`
- `last_verified`
- `confidence`: `low`, `medium`, or `high`
- `sources`: repository-relative paths and optional line ranges

The architecture JSON additionally requires:

- `schema_version`
- `status`
- `project.id`, `project.name`, `project.source_commit`, and `project.generated_at`
- `nodes[]` with stable IDs
- `edges[]` whose source and target IDs exist
- `flows[]` with ordered steps referencing existing nodes

See `architecture-graph.md` for the full contract.

Mesh records additionally include:

- `source_project`
- `visibility`
- `export_schema_version`
- `generated_at`
