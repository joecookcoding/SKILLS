# Example First Run

Inside an existing source repository, give an agent `INSTALL.md` and say:

```text
MESH >> REPO .
```

After the local map is compiled, create the shared repository:

```text
MESH >> CREATE ../repo-mesh
```

Connect the source repository:

```text
MESH >> CONNECT ../repo-mesh
```

At the beginning and end of future coding sessions:

```text
MESH >> START
MESH >> END
```
