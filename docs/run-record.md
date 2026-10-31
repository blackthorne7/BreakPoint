# Run record format

`run_store.py` writes completed runs and their ordered tool and transcript events to an append-only SQLite database. The database is local and excluded from Git by default. Runs are immutable once recorded; a correction should be represented as a new run with a note in its summary.

The input document is a JSON object with this shape:

```json
{
  "run_id": "unique-run-id",
  "environment": {
    "id": "struts2-s2-045",
    "version": "vulhub/struts2:2.3.30",
    "image_ref": "vulhub/struts2:2.3.30",
    "image_digest": "sha256:...",
    "success_condition": "Lab-defined, independently checked condition"
  },
  "agent": {
    "config_id": "baseline",
    "config_version": "1",
    "model": "provider/model-version",
    "memory_snapshot": {}
  },
  "started_at": "2026-01-01T00:00:00Z",
  "finished_at": "2026-01-01T00:00:05Z",
  "outcome": "fail",
  "wall_time_ms": 5000,
  "tokens": {"input": 0, "output": 0, "cost_usd": null},
  "result_summary": "Short factual summary",
  "tool_invocations": [],
  "transcript_events": []
}
```

Each invocation needs an ID, sequence, fixed tool ID and version, parameters, target, start/finish times, status, and result. The store derives `step_count` from the number of invocations. Transcript events should contain the user-visible prompt/response and tool activity needed to replay the run; do not put hidden model reasoning or credentials in this field.

Token counts and cost may be `null` when the provider does not expose them. Do not substitute estimates without labeling them.
