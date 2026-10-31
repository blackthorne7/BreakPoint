#!/usr/bin/env python3
"""Append-only SQLite storage for BreakPoint run records."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


DEFAULT_DB = Path("data/runs.sqlite3")
OUTCOMES = {"success", "partial", "fail"}


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    environment_id TEXT NOT NULL,
    environment_version TEXT NOT NULL,
    image_ref TEXT NOT NULL,
    image_digest TEXT,
    success_condition TEXT NOT NULL,
    agent_config_id TEXT NOT NULL,
    agent_config_version TEXT NOT NULL,
    model TEXT NOT NULL,
    memory_snapshot_json TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'partial', 'fail')),
    step_count INTEGER NOT NULL CHECK (step_count >= 0),
    wall_time_ms INTEGER NOT NULL CHECK (wall_time_ms >= 0),
    input_tokens INTEGER CHECK (input_tokens IS NULL OR input_tokens >= 0),
    output_tokens INTEGER CHECK (output_tokens IS NULL OR output_tokens >= 0),
    token_cost_usd REAL CHECK (token_cost_usd IS NULL OR token_cost_usd >= 0),
    result_summary TEXT NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tool_invocations (
    invocation_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    tool_id TEXT NOT NULL,
    tool_version TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    target TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    status TEXT NOT NULL,
    result_json TEXT NOT NULL,
    UNIQUE (run_id, sequence)
);

CREATE TABLE IF NOT EXISTS transcript_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL,
    event_type TEXT NOT NULL,
    content TEXT NOT NULL,
    UNIQUE (run_id, sequence)
);

CREATE TRIGGER IF NOT EXISTS runs_no_update
BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT, 'run records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS runs_no_delete
BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT, 'run records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS invocations_no_update
BEFORE UPDATE ON tool_invocations BEGIN SELECT RAISE(ABORT, 'invocation records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS invocations_no_delete
BEFORE DELETE ON tool_invocations BEGIN SELECT RAISE(ABORT, 'invocation records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS transcript_no_update
BEFORE UPDATE ON transcript_events BEGIN SELECT RAISE(ABORT, 'transcript records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS transcript_no_delete
BEFORE DELETE ON transcript_events BEGIN SELECT RAISE(ABORT, 'transcript records are append-only'); END;
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def required(mapping: dict[str, Any], key: str, parent: str) -> Any:
    value = mapping.get(key)
    if value is None or value == "":
        raise ValueError(f"missing required field: {parent}.{key}")
    return value


def record_run(conn: sqlite3.Connection, document: dict[str, Any]) -> None:
    run_id = str(required(document, "run_id", "run"))
    environment = required(document, "environment", "run")
    agent = required(document, "agent", "run")
    tokens = document.get("tokens", {})
    invocations = document.get("tool_invocations", [])
    transcript = document.get("transcript_events", [])
    outcome = required(document, "outcome", "run")
    if outcome not in OUTCOMES:
        raise ValueError("outcome must be success, partial, or fail")
    if not isinstance(invocations, list) or not isinstance(transcript, list):
        raise ValueError("tool_invocations and transcript_events must be arrays")

    with conn:
        conn.execute(
            """INSERT INTO runs (
                run_id, environment_id, environment_version, image_ref, image_digest,
                success_condition, agent_config_id, agent_config_version, model,
                memory_snapshot_json, started_at, finished_at, outcome, step_count,
                wall_time_ms, input_tokens, output_tokens, token_cost_usd, result_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                required(environment, "id", "environment"),
                required(environment, "version", "environment"),
                required(environment, "image_ref", "environment"),
                environment.get("image_digest"),
                required(environment, "success_condition", "environment"),
                required(agent, "config_id", "agent"),
                required(agent, "config_version", "agent"),
                required(agent, "model", "agent"),
                json.dumps(agent.get("memory_snapshot", {}), sort_keys=True),
                required(document, "started_at", "run"),
                required(document, "finished_at", "run"),
                outcome,
                len(invocations),
                int(required(document, "wall_time_ms", "run")),
                tokens.get("input"),
                tokens.get("output"),
                tokens.get("cost_usd"),
                required(document, "result_summary", "run"),
            ),
        )

        for item in invocations:
            conn.execute(
                """INSERT INTO tool_invocations (
                    invocation_id, run_id, sequence, tool_id, tool_version,
                    parameters_json, target, started_at, finished_at, status, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    required(item, "invocation_id", "tool_invocation"),
                    run_id,
                    int(required(item, "sequence", "tool_invocation")),
                    required(item, "tool_id", "tool_invocation"),
                    required(item, "tool_version", "tool_invocation"),
                    json.dumps(required(item, "parameters", "tool_invocation"), sort_keys=True),
                    required(item, "target", "tool_invocation"),
                    required(item, "started_at", "tool_invocation"),
                    required(item, "finished_at", "tool_invocation"),
                    required(item, "status", "tool_invocation"),
                    json.dumps(item.get("result", {}), sort_keys=True),
                ),
            )

        for item in transcript:
            conn.execute(
                """INSERT INTO transcript_events (
                    event_id, run_id, sequence, timestamp, role, event_type, content
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    required(item, "event_id", "transcript_event"),
                    run_id,
                    int(required(item, "sequence", "transcript_event")),
                    required(item, "timestamp", "transcript_event"),
                    required(item, "role", "transcript_event"),
                    required(item, "event_type", "transcript_event"),
                    required(item, "content", "transcript_event"),
                ),
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="initialize the local run database")
    record_parser = commands.add_parser("record", help="append one completed run JSON record")
    record_parser.add_argument("document", type=Path, help="path to a run JSON document")
    commands.add_parser("list", help="list recorded runs")
    args = parser.parse_args()

    try:
        with connect(args.db) as conn:
            if args.command == "init":
                print(f"initialized {args.db}")
            elif args.command == "record":
                data = json.loads(args.document.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("run document must be a JSON object")
                record_run(conn, data)
                print(f"recorded run {data['run_id']}")
            elif args.command == "list":
                rows = conn.execute(
                    "SELECT run_id, environment_id, outcome, step_count, wall_time_ms, recorded_at "
                    "FROM runs ORDER BY recorded_at, run_id"
                )
                for row in rows:
                    print(json.dumps(dict(row), sort_keys=True))
        return 0
    except (OSError, sqlite3.Error, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
