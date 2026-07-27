# Example First Run

Inside an existing source repository, give an agent `INSTALL.md` and say:

```text
MESH >> REPO .
```

This performs the initial map and creates both:

```text
.repo-map/generated/architecture.json
.repo-map/generated/architecture.html
```

To explicitly refresh the full map later:

```text
MESH >> MAP
```

After the local map is compiled, create the shared repository:

```text
MESH >> CREATE ../repo-mesh
```

Connect the source repository:

```text
MESH >> CONNECT ../repo-mesh
```

Rebuild its combined visual graph:

```text
MESH >> GRAPH ../repo-mesh
```

At the beginning and end of future coding sessions:

```text
MESH >> START
MESH >> END
```
