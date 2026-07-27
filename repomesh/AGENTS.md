# RepoMesh Package Instructions

Use `INSTALL.md` for first-run installation commands.

For RepoMesh behavior, read `.agents/skills/repomesh/SKILL.md`.

Non-negotiable rules:

- Live code and reviewed local documentation outrank generated maps.
- The local `.repo-map/` must remain usable without a connected Mesh.
- Preserve missing or conflicting knowledge as unresolved; do not silently delete it.
- Never ingest secrets, credentials, private keys, `.env` contents, PHI, customer data, or proprietary datasets.
- The architecture JSON is the machine source of truth; regenerate the HTML from it and never hand-edit the HTML.
- Do not commit, push, or alter source code unless explicitly requested.
