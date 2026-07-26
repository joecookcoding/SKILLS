# MESH Command Card

Point a coding agent to `INSTALL.md`, then issue:

```text
MESH >> REPO .
```

This bakes the generic RepoMesh skill and a non-destructive `.repo-map/` into the current repository.

Create the optional shared Mesh repository:

```text
MESH >> CREATE ../repo-mesh
```

Connect the current source repository to it:

```text
MESH >> CONNECT ../repo-mesh
```

Begin and finish sessions:

```text
MESH >> START
MESH >> END
```

The local Repo Map continues working when the shared Mesh is absent or inaccessible.
