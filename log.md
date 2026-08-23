# log

Append-only, chronological. Every ingest, query filed, lint pass, brief, and unsource lands
here. Newest at the bottom.

Entries keep this prefix exactly so the log stays greppable:

```
## [YYYY-MM-DD] <op> | <title>
```

`grep "^## \[" log.md | tail -5` gives the last five operations.

---

## [2026-08-23] init | vault created

Scaffolded from the specification in README.md. Schema in CLAUDE.md. Skills: capture,
ingest, bootstrap, brief, ask, lint, unsource. Vault empty — no sources compiled yet.
