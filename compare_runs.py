#!/usr/bin/env python3
"""Print a small local comparison for two stored BreakPoint attempts."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_ids", nargs=2)
    parser.add_argument("--db", type=Path, default=Path("data/runs.sqlite3"))
    parser.add_argument("--notes", type=Path, help="notes JSON from the extraction step, for extraction usage")
    args = parser.parse_args()

    try:
        with sqlite3.connect(args.db) as conn:
            conn.row_factory = sqlite3.Row
            rows = [conn.execute("SELECT run_id, outcome, step_count, wall_time_ms, input_tokens, output_tokens, token_cost_usd, memory_snapshot_json FROM runs WHERE run_id = ?", (run_id,)).fetchone() for run_id in args.run_ids]
        if any(row is None for row in rows):
            missing = [run_id for run_id, row in zip(args.run_ids, rows) if row is None]
            raise ValueError("unknown run ID(s): " + ", ".join(missing))
        extraction = json.loads(args.notes.read_text(encoding="utf-8")) if args.notes else {}
    except (OSError, sqlite3.Error, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    print("| Run | Outcome | Tool calls | Time (ms) | Input tokens | Output tokens | Cost (USD) | Memory |")
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for row in rows:
        memory = json.loads(row["memory_snapshot_json"])
        used_memory = "yes" if memory.get("type") != "none" and memory else "no"
        values = [row["run_id"], row["outcome"], row["step_count"], row["wall_time_ms"], row["input_tokens"], row["output_tokens"], row["token_cost_usd"], used_memory]
        print("| " + " | ".join("N/A" if value is None else str(value).replace("|", "\\|") for value in values) + " |")
    if args.notes:
        usage = extraction.get("usage", {})
        print("\nStrategy extraction usage: input tokens = " + str(usage.get("input", "N/A")) + ", output tokens = " + str(usage.get("output", "N/A")) + ", cost = N/A (provider did not report a price).")
    print("\nIllustrative demo; two attempts; not evidence of reliable improvement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
