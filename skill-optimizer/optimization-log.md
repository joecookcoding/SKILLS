# Optimization Log (append-only)

Memory for the skill-optimizer skill. Each audit/optimization run appends an entry at the
bottom. At the start of every audit, read the latest entry and diff current measurements
against it instead of starting cold.

Entry format (one `## <date> — <summary>` heading per run): baseline measurements, the
decisions made, the actions taken, and anything deliberately *not* done so the next run
doesn't re-propose it.

---

_No runs logged yet — the next audit starts cold and writes the first entry here._
