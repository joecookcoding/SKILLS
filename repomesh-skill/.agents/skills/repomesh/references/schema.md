# Repo Map Schema

Every generated page should include YAML frontmatter with:

- `title`
- `type`
- `status`: `draft`, `active`, `stale`, `unresolved`, `superseded`, or `archived`
- `ownership`: `human`, `generated`, or `hybrid`
- `source_commit`
- `last_verified`
- `confidence`: `low`, `medium`, or `high`
- `sources`: repository-relative paths and optional line ranges

Mesh records additionally include:

- `source_project`
- `visibility`
- `export_schema_version`
- `generated_at`
